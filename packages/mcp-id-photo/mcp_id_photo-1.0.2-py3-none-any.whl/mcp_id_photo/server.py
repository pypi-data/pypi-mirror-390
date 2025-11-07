#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成证件照 MCP 服务器（基于阿里云百炼 通义千问-图像编辑）
功能：
- 仅提供一个工具：输入 `image_url`（必填），可选 `output_path`、`bg`、`spec` 或 `size`。
- 先用 `image_url` 与 `bg` 调用文档 API 生成证件照；
- 随后将结果按目标尺寸裁剪：默认二寸-标准（413×531），如传参则按参裁剪；
- 最终保存到桌面或指定输出路径，并返回保存路径等信息。

说明：本实现采用同步调用，直接返回生成结果，不再提供异步任务查询工具。
"""

import logging
import os
import time
import json
import base64
from io import BytesIO
from http import HTTPStatus
from typing import Literal, Tuple
from urllib.request import urlopen, Request

import dashscope
from mcp.server.fastmcp import FastMCP
from PIL import Image, ImageChops

# 配置日志
logging.basicConfig(
    level=logging.INFO if os.getenv("MCP_DEBUG") == "1" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 设置 DashScope 基础 API 地址（中国大陆北京地域）
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

# 创建 FastMCP 服务器实例
mcp = FastMCP("证件照生成（通义千问-图像编辑）")


def verify_api_key():
    """验证 DashScope API Key 是否配置"""
    if not os.environ.get("DASHSCOPE_API_KEY"):
        raise ValueError("未设置环境变量 DASHSCOPE_API_KEY（阿里云百炼 API Key）")


def _spec_to_size(spec: str) -> Tuple[int, int]:
    """常用证件照规格映射为像素尺寸（px）
    - 一寸：295×413 px（25×35 mm @ 300dpi）
    - 二寸-标准：413×531 px（35×45 mm @ 300dpi）
    - 二寸-大：413×579 px（35×49 mm @ 300dpi）
    """
    mapping = {
        "一寸": (295, 413),
        "二寸-标准": (413, 531),
        "二寸-大": (413, 579),
    }
    if spec not in mapping:
        raise ValueError(f"不支持的规格：{spec}")
    return mapping[spec]


def _parse_size_str(size: str) -> Tuple[int, int]:
    """解析像素尺寸字符串，支持格式："宽*高"、"宽x高"（大小写均可）。
    例如："295*413" 或 "295x413" -> (295, 413)
    """
    s = size.strip().lower().replace("×", "x")
    if "*" in s:
        parts = s.split("*")
    elif "x" in s:
        parts = s.split("x")
    else:
        raise ValueError("size 格式不正确，应为 '宽*高' 或 '宽x高'，例如 '295*413'")
    if len(parts) != 2:
        raise ValueError("size 解析失败，应包含两个数值：宽与高")
    try:
        w = int(parts[0].strip())
        h = int(parts[1].strip())
    except Exception:
        raise ValueError("size 中包含非整数数值，请使用如 '295*413' 的格式")
    if w <= 0 or h <= 0:
        raise ValueError("size 的宽高必须为正整数")
    return (w, h)


def _bg_to_prompt_and_rgb(bg: str) -> Tuple[str, Tuple[int, int, int]]:
    """背景色到提示词与RGB的映射"""
    bg = bg.lower()
    if bg == "white":
        return "纯白色背景", (255, 255, 255)
    if bg == "blue":
        # 常用证件照蓝底（近似值）
        return "纯蓝色背景", (0, 85, 170)
    if bg == "red":
        return "纯红色背景", (220, 0, 0)
    raise ValueError(f"不支持的背景色：{bg}")


def _resize_and_pad(img: Image.Image, target_size: Tuple[int, int], bg_rgb: Tuple[int, int, int]) -> Image.Image:
    """将图像按比例缩放并在指定背景色上居中填充到目标尺寸"""
    img = img.convert("RGBA")
    tw, th = target_size
    ratio = min(tw / img.width, th / img.height)
    new_w = max(1, int(img.width * ratio))
    new_h = max(1, int(img.height * ratio))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (tw, th), bg_rgb)
    paste_x = (tw - new_w) // 2
    paste_y = (th - new_h) // 2
    canvas.paste(resized.convert("RGB"), (paste_x, paste_y))
    return canvas


def _crop_by_person_mask(
    img: Image.Image,
    target_size: Tuple[int, int],
    bg_rgb: Tuple[int, int, int],
    expand_ratio: float = 0.92,
    top_margin_ratio: float = 0.12,
    bg_threshold: int = 40,
) -> Image.Image:
    """
    基于背景差异生成前景掩膜，按证件照构图规则进行裁剪：
    - 头顶上边距占输出高度的 `top_margin_ratio`（默认 12%，符合通用证件照推荐比例）
    - 垂直方向裁剪高度约为前景包围盒的 `expand_ratio`（默认 0.92，便于覆盖肩部与上胸部）
    - 裁剪区域的宽高比与目标尺寸一致，避免后续拉伸变形

    说明：不引入额外依赖，利用背景纯色与主体的差异来估计前景区域。
    在掩膜无法可靠获取时，回退为居中填充模式。
    """
    rgb = img.convert("RGB")
    tw, th = target_size
    aspect = tw / th if th > 0 else 1.0

    # 生成与背景的差异掩膜
    bg_img = Image.new("RGB", rgb.size, bg_rgb)
    diff = ImageChops.difference(rgb, bg_img).convert("L")
    # 二值化掩膜：与背景的差异超过阈值的像素视为前景
    mask = diff.point(lambda v: 255 if v > bg_threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        # 掩膜失败时，回退为居中填充
        return _resize_and_pad(img, target_size, bg_rgb)

    min_x, min_y, max_x, max_y = bbox
    head_top = min_y
    bbox_h = max(1, max_y - min_y)

    # 初始裁剪高度：适度下延到肩部与上胸部
    H0 = max(1, int(bbox_h * max(0.4, min(expand_ratio, 1.5))))

    # 约束：根据头顶上边距，保证裁剪框不越界
    eps = 1e-6
    H_by_top = int(head_top / max(top_margin_ratio, eps))
    H_by_bottom = int((rgb.height - head_top) / max(1.0 - top_margin_ratio, eps))
    H_limit = max(1, min(H0, H_by_top, H_by_bottom, rgb.height))

    # 保证宽度不越界（按目标宽高比）
    Hcrop = max(1, min(H_limit, int(rgb.width / max(aspect, eps))))
    Wcrop = max(1, int(aspect * Hcrop))

    # 水平居中于主体包围盒
    center_x = (min_x + max_x) // 2
    x_left = max(0, min(rgb.width - Wcrop, center_x - Wcrop // 2))

    # 垂直位置按头顶上边距确定
    y_top = head_top - int(top_margin_ratio * Hcrop)
    y_top = max(0, min(rgb.height - Hcrop, y_top))

    crop = rgb.crop((x_left, y_top, x_left + Wcrop, y_top + Hcrop))
    return crop.resize((tw, th), Image.LANCZOS)

def _resolve_output_file(output_path: str | None, default_name: str) -> str:
    """解析最终保存文件路径：
    - 若提供 `output_path` 且为目录，则保存为目录下的 `default_name`
    - 若提供 `output_path` 且为文件路径，则直接使用；若上级目录不存在则创建
    - 否则默认保存到桌面（不可用时退回当前工作目录）
    """
    def _get_desktop_dir() -> str:
        """跨平台获取桌面目录，Windows 优先使用系统 API。
        - Windows：优先 `SHGetFolderPathW(CSIDL_DESKTOPDIRECTORY)`，再尝试 `USERPROFILE`、`HOMEDRIVE+HOMEPATH`、`OneDrive`。
        - 其他系统：`~ / Desktop`。
        - 若以上路径不可用，则回退为当前工作目录。
        """
        try:
            if os.name == "nt":
                try:
                    import ctypes  # 延迟导入，避免非 Windows 报错
                    buf = ctypes.create_unicode_buffer(260)
                    CSIDL_DESKTOPDIRECTORY = 0x10
                    SHGFP_TYPE_CURRENT = 0
                    # 成功返回 0
                    ret = ctypes.windll.shell32.SHGetFolderPathW(
                        None, CSIDL_DESKTOPDIRECTORY, None, SHGFP_TYPE_CURRENT, buf
                    )
                    if ret == 0:
                        p = buf.value
                        if p and os.path.isdir(p):
                            return p
                except Exception:
                    pass

                # 环境变量回退
                base = os.environ.get("USERPROFILE")
                if base:
                    p = os.path.join(base, "Desktop")
                    if os.path.isdir(p):
                        return p

                homedrive = os.environ.get("HOMEDRIVE")
                homepath = os.environ.get("HOMEPATH")
                if homedrive and homepath:
                    p = os.path.join(homedrive + homepath, "Desktop")
                    if os.path.isdir(p):
                        return p

                onedrive = os.environ.get("OneDrive")
                if onedrive:
                    p = os.path.join(onedrive, "Desktop")
                    if os.path.isdir(p):
                        return p

            # 非 Windows 或以上未命中
            p = os.path.join(os.path.expanduser("~"), "Desktop")
            if os.path.isdir(p):
                return p
        except Exception:
            pass
        return os.getcwd()

    def _is_windows_style_path(p: str) -> bool:
        try:
            s = p.strip()
            if len(s) >= 3 and s[1] == ':' and (s[2] == '\\' or s[2] == '/'):
                # 形如 C:\ 或 D:/
                return True
        except Exception:
            pass
        return False

    try:
        if output_path:
            raw = output_path.strip()
            # 若是 Windows 风格绝对路径，避免在非 Windows 环境被当作相对路径拼接到 cwd（如 /app）
            if _is_windows_style_path(raw) or os.name == "nt":
                p = raw
                # 判断是否目录还是文件：有扩展名视为文件，否则目录
                _, ext = os.path.splitext(p)
                if not ext:
                    return os.path.join(p, default_name)
                parent = os.path.dirname(p) or "."
                try:
                    os.makedirs(parent, exist_ok=True)
                except Exception:
                    # 创建失败不影响返回路径，但保存可能失败
                    pass
                return p

            # 非 Windows 风格，按当前 OS 规则解析
            p = os.path.abspath(raw)
            if os.path.isdir(p):
                return os.path.join(p, default_name)
            parent = os.path.dirname(p) or "."
            os.makedirs(parent, exist_ok=True)
            return p
        # 默认桌面（使用系统 API/环境变量解析）
        desktop = _get_desktop_dir()
        return os.path.join(desktop, default_name)
    except Exception:
        # 兜底：当前工作目录
        return os.path.join(os.getcwd(), default_name)


@mcp.tool()
def make_id_photo(
    image_url: str,
    output_path: str | None = None,
    bg: Literal["white", "blue", "red"] = "blue",
    spec: Literal["一寸", "二寸-标准", "二寸-大"] | None = None,
) -> dict:
    """
    生成并保存证件照

    流程：
    1) 使用 `image_url` 与 `bg` 调用通义千问-图像编辑生成证件照；
    2) 将生成结果按目标尺寸进行裁剪——默认二寸-标准（413×531），若传入 `spec` 则按规格；
    3) 将裁剪结果保存到桌面或 `output_path` 指定位置；返回保存路径与元数据。

    参数：
    - `image_url`（必填）：公网可访问的人像图片 URL。
    - `output_path`（可选）：输出目录或最终文件路径，留空则保存桌面。
    - `bg`（可选）：背景色 white/blue/red，默认 blue。
    - `spec`（可选）：一寸/二寸-标准/二寸-大。

    返回：
    - `success`: 是否成功
    - `file_path`: 最终保存的文件路径
    - `size_applied`: 实际应用的目标尺寸（如 `413x531`）
    - `bg`: 背景色
    - `source_images`: 从模型返回中解析出的图片 URL 或 data URL 列表
    - `behavior_notice`: 说明为同步生成
    """
    verify_api_key()
    api_key = os.getenv("DASHSCOPE_API_KEY")

    # 目标尺寸解析，默认二寸-标准
    try:
        if spec:
            target_size = _spec_to_size(spec)
        else:
            target_size = _spec_to_size("二寸-标准")
        size_label = f"{target_size[0]}x{target_size[1]}"
    except Exception as e:
        raise ValueError(f"目标规格解析失败: {e}")

    # 构造提示词与参数
    try:
        bg_prompt, bg_rgb = _bg_to_prompt_and_rgb(bg)
    except Exception as e:
        raise ValueError(str(e))

    prompt = (
        f"与参考图面部特征一致，去除面部多余阴影，将背景替换为{bg_prompt}，生成标准证件照，穿着规范、摄影棚灯光"
    ) 

    # DashScope 多模态生成接口
    base = dashscope.base_http_api_url.rstrip("/")
    url = f"{base}/services/aigc/multimodal-generation/generation"
    payload = {
        "model": "qwen-image-edit-plus",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": image_url},
                        {"text": prompt},
                    ],
                }
            ]
        },
        "parameters": {
            "n": 1,
            "negative_prompt": "人像面部细节改变，发型改变",
            "watermark": False,
        }
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 调用生成
    try:
        req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        raw = urlopen(req).read()
        data = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"调用生成接口失败: {e}")

    # 解析图片 URL 列表
    images = []
    try:
        out = data.get("output", {})
        choices = out.get("choices", [])
        for ch in choices:
            msg = ch.get("message") or {}
            content = msg.get("content") or []
            for item in content:
                if isinstance(item, dict):
                    if "image" in item:
                        v = item["image"]
                        if isinstance(v, str):
                            images.append(v.strip())
                        elif isinstance(v, dict):
                            if "url" in v:
                                images.append(v["url"])
                            elif "base64" in v:
                                images.append("data:image/png;base64," + v["base64"])
                    elif item.get("type") == "image" and "url" in item:
                        images.append(item["url"])
                    elif "url" in item and item.get("mime_type"):
                        images.append(item["url"])
    except Exception:
        pass

    if not images:
        raise RuntimeError("未在响应中解析到图片结果")

    # 取第一张进行裁剪到目标尺寸
    src = images[0]
    try:
        if src.startswith("data:image"):
            b64 = src.split(",", 1)[1]
            img_bytes = base64.b64decode(b64)
        else:
            img_bytes = urlopen(src).read()
        img = Image.open(BytesIO(img_bytes))
    except Exception as e:
        raise RuntimeError(f"下载或解析图片失败: {e}")

    try:
        # 强制使用裁剪到目标尺寸（符合证件照构图）
        final_img = _crop_by_person_mask(
            img,
            target_size,
            bg_rgb,
            expand_ratio=0.92,
            top_margin_ratio=0.12,
            bg_threshold=40,
        )
    except Exception:
        # 回退为居中填充
        final_img = _resize_and_pad(img, target_size, bg_rgb)

    # 保存到路径
    ts = int(time.time())
    default_name = f"id_photo_{size_label}_{ts}.png"
    file_path = _resolve_output_file(output_path, default_name)
    try:
        final_img.save(file_path, format="PNG")
    except Exception as e:
        raise RuntimeError(f"保存文件失败: {e}；请检查输出路径是否可写: {file_path}")

    result = {
        "success": True,
        "file_path": file_path,
        "size_applied": size_label,
        "bg": bg,
        "spec": spec if spec else "二寸-标准",
        "source_images": images,
    }
    return result




def main():
    """主函数入口"""
    logger.info("启动证件照生成 MCP 服务器...")
    mcp.run()


if __name__ == "__main__":
    main()
