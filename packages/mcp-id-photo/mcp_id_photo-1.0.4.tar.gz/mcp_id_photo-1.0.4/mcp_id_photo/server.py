#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成证件照 MCP 服务器（基于阿里云百炼 通义千问-图像编辑）
功能：
- 仅提供一个工具：输入 `image_url`（必填），可选 `bg`、`spec` 或 `size`。
- 先用 `image_url` 与 `bg` 调用文档 API 生成证件照；
- 随后将结果按目标尺寸裁剪：默认二寸-标准（413×531），如传参则按参裁剪；
- 最终上传到 OSS 并返回文件 URL。

说明：本实现采用同步调用，直接返回生成结果，不再提供异步任务查询工具。
"""

import logging
import os
import time
import json
import base64
import tempfile
from io import BytesIO
from http import HTTPStatus
from typing import Literal, Tuple
from urllib.request import urlopen, Request
import uuid

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

# 上传API（参考 typescript/文件上传下载/src/index.ts）
UPLOAD_API_URL = "https://www.mcpcn.cc/api/fileUploadAndDownload/uploadMcpFile"


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



def _clean_url(s: str) -> str:
    """移除首尾的反引号/引号与空白，避免URL被包裹。"""
    try:
        t = (s or "").strip()
        while t and t[0] in "`'\"":
            t = t[1:].strip()
        while t and t[-1] in "`'\"":
            t = t[:-1].strip()
        return t
    except Exception:
        return s


def _guess_mime_type_from_ext(ext: str) -> str:
    """根据扩展名猜测 MIME 类型（仅覆盖图片常见类型）。"""
    e = (ext or "").lower()
    if e in (".jpg", ".jpeg"):
        return "image/jpeg"
    if e == ".png":
        return "image/png"
    if e == ".gif":
        return "image/gif"
    if e == ".webp":
        return "image/webp"
    if e in (".bmp"):
        return "image/bmp"
    if e in (".tiff", ".tif"):
        return "image/tiff"
    return "application/octet-stream"


def _upload_file_to_oss(file_path: str) -> str:
    """将本地文件以 multipart/form-data 上传到 OSS，返回URL。

    成功：返回可访问的文件URL。
    失败：抛出 RuntimeError。
    """
    try:
        if not os.path.isfile(file_path):
            raise RuntimeError(f"待上传文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        content_type = _guess_mime_type_from_ext(ext)

        with open(file_path, "rb") as f:
            data = f.read()
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"

        # 构建 multipart/form-data
        preamble = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
        closing = f"\r\n--{boundary}--\r\n".encode("utf-8")
        body = preamble + data + closing

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }
        req = Request(UPLOAD_API_URL, data=body, headers=headers, method="POST")
        raw = urlopen(req, timeout=30).read()
        resp = json.loads(raw.decode("utf-8"))

        if isinstance(resp, dict) and resp.get("code") == 0:
            url = ((resp.get("data") or {}).get("url"))
            if url:
                return url
            raise RuntimeError("上传成功但未返回URL")
        # 非0视为失败
        msg = resp.get("msg") if isinstance(resp, dict) else str(resp)
        raise RuntimeError(f"上传失败: {msg}")
    except Exception as e:
        raise RuntimeError(f"上传到OSS失败: {e}")


@mcp.tool()
def make_id_photo(
    image_url: str,
    bg: Literal["white", "blue", "red"] = "blue",
    spec: Literal["一寸", "二寸-标准", "二寸-大"] | None = None,
) -> dict:
    """
    生成并保存证件照

    流程：
    1) 使用 `image_url` 与 `bg` 调用通义千问-图像编辑生成证件照；
    2) 将生成结果按目标尺寸进行裁剪——默认二寸-标准（413×531），若传入 `spec` 则按规格；
    3) 将裁剪结果保存到临时目录用于上传，上传成功后删除临时文件并返回 URL。

    参数：
    - `image_url`（必填）：公网可访问的人像图片 URL。
    - `bg`（可选）：背景色 white/blue/red，默认 blue。
    - `spec`（可选）：一寸/二寸-标准/二寸-大。

    返回：
    - `success`: 是否成功
    - `file_url`: 上传后的文件 URL（为兼容旧字段，`file_path` 同为 URL）
    - `size_applied`: 实际应用的目标尺寸（如 `413x531`）
    - `bg`: 背景色
    - `source_images`: 从模型返回中解析出的图片 URL 或 data URL 列表
    - `behavior_notice`: 说明为同步生成
    """
    verify_api_key()
    api_key = os.getenv("DASHSCOPE_API_KEY")

    # 清理可能包裹的反引号或引号
    image_url = _clean_url(image_url)

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

    # 保存到临时目录（PNG）
    ts = int(time.time())
    default_name = f"id_photo_{size_label}_{ts}.png"
    file_path = os.path.join(tempfile.gettempdir(), default_name)
    try:
        img_to_save = final_img
        img_to_save.save(file_path, format="PNG")
        # 写入后校验
        if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
            raise RuntimeError("保存文件失败：未创建或文件大小为0")
    except Exception as e:
        raise RuntimeError(f"保存文件失败: {e}；请检查临时目录是否可写: {file_path}")

    # 上传到 OSS
    try:
        uploaded_url = _upload_file_to_oss(file_path)
    except Exception as e:
        # 上传失败，不删除本地文件，便于排查和保留结果
        raise RuntimeError(f"上传到OSS失败: {e}")

    # 上传成功后删除本地文件
    try:
        os.remove(file_path)
    except Exception:
        # 删除失败不影响结果，仅记录日志
        logger.warning(f"删除本地文件失败: {file_path}")

    result = {
        "success": True,
        # 为兼容性保留字段名，但值改为URL；同时增加专用字段
        "file_path": uploaded_url,
        "file_url": uploaded_url,
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
