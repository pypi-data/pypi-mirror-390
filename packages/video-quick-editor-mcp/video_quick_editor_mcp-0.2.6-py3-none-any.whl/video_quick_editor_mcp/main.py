from mcp.server.fastmcp import FastMCP, Context
import ffmpeg
import os
import re
import tempfile
import shutil
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import platform
import urllib.parse
import time

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

package = "video-quick-editor-mcp"

# 使用用户临时目录存放日志文件
log_dir = Path(tempfile.gettempdir()) / package
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "debug.log"

file_handler = RotatingFileHandler(
    str(log_file), maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)
logger.propagate = False

# 测试代码使用的
FFMPEG_BINARY = os.environ.get("FFMPEG_BINARY")
FFPROBE_BINARY = os.environ.get("FFPROBE_BINARY")


def _ffmpeg_run(stream_spec, **kwargs):
    if "overwrite_output" not in kwargs:
        kwargs["overwrite_output"] = True
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BINARY, **kwargs)


def _ffmpeg_run_async(stream_spec, **kwargs):
    return ffmpeg.run_async(stream_spec, cmd=FFMPEG_BINARY, **kwargs)


def _ffprobe_probe(path: str, **kwargs):
    return ffmpeg.probe(path, cmd=FFPROBE_BINARY, **kwargs)


def _parse_time_to_seconds(time_str: str) -> float:
    if isinstance(time_str, (int, float)):
        return float(time_str)
    if ":" in time_str:
        parts = time_str.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    return float(time_str)


def _get_media_properties(media_path: str) -> dict:
    try:
        probe = _ffprobe_probe(media_path)
        video_stream_info = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"), None
        )
        audio_stream_info = next(
            (s for s in probe["streams"] if s["codec_type"] == "audio"), None
        )

        props = {
            "duration": float(probe["format"].get("duration", 0.0)),
            "has_video": video_stream_info is not None,
            "has_audio": audio_stream_info is not None,
            "width": int(video_stream_info["width"])
            if video_stream_info and "width" in video_stream_info
            else 0,
            "height": int(video_stream_info["height"])
            if video_stream_info and "height" in video_stream_info
            else 0,
            "avg_fps": 0,
            "sample_rate": int(audio_stream_info["sample_rate"])
            if audio_stream_info and "sample_rate" in audio_stream_info
            else 44100,
            "channels": int(audio_stream_info["channels"])
            if audio_stream_info and "channels" in audio_stream_info
            else 2,
            "channel_layout": audio_stream_info.get("channel_layout", "stereo")
            if audio_stream_info
            else "stereo",
        }
        if (
            video_stream_info
            and "avg_frame_rate" in video_stream_info
            and video_stream_info["avg_frame_rate"] != "0/0"
        ):
            num, den = map(int, video_stream_info["avg_frame_rate"].split("/"))
            if den > 0:
                props["avg_fps"] = num / den
            else:
                props["avg_fps"] = 30
        else:
            props["avg_fps"] = 30
        return props
    except ffmpeg.Error as e:
        raise RuntimeError(
            f"Error probing file {media_path}: {e.stderr.decode('utf8') if e.stderr else str(e)}"
        )
    except Exception as e:
        raise RuntimeError(f"Unexpected error probing file {media_path}: {str(e)}")


def _prepare_path(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise RuntimeError(f"Error: Input file not found at {input_path}")
    try:
        parent_dir = os.path.dirname(output_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(
            f"Error creating output directory for {output_path}: {str(e)}"
        )
    if os.path.exists(output_path):
        raise RuntimeError(
            f"Error: Output file already exists at {output_path}. Please choose a different path or delete the existing file."
        )


def _open_aido_link(ctx: Context, return_message: str) -> None:
    """跨平台静默执行aido://tool?xxx&chatSessionId=xxx"""
    try:
        # 检查 ctx 是否为 None
        if ctx is None:
            logger.debug("Context is None, skipping aido link execution")
            return

        # 尝试从 request_context 获取
        request_context = getattr(ctx, "request_context", None)
        # 尝试从 request_context.meta 获取 chatSessionId
        chatSessionId = None
        if request_context and hasattr(request_context, "meta"):
            context_meta = getattr(request_context, "meta", None)
            logger.debug(f"context meta: {context_meta}")
            if context_meta and hasattr(context_meta, "chatSessionId"):
                chatSessionId = getattr(context_meta, "chatSessionId", None)
                logger.debug(
                    f"chatSessionId from request_context.meta: {chatSessionId}"
                )

        # 验证 chatSessionId 是否有效
        if not chatSessionId or chatSessionId == "None":
            logger.warning(
                f"Invalid or missing chatSessionId: {chatSessionId}, skipping aido link execution"
            )
            return

        encoded_message = urllib.parse.quote(return_message, safe="")
        package_name = urllib.parse.quote(package, safe="")
        aido_url = f"aido://tool?path={encoded_message}&chatSessionId={chatSessionId}&package={package_name}"

        # 根据操作系统选择合适的命令
        system = platform.system().lower()
        if system == "darwin":  # macOS
            result = subprocess.run(
                ["open", aido_url], check=False, capture_output=True, text=True
            )
            if result.returncode != 0 and result.stderr:
                logger.warning(f"macOS open command failed: {result.stderr}")
        elif system == "windows":  # Windows
            # 使用 os.startfile (推荐方式) 或修正 start 命令语法
            try:
                os.startfile(aido_url)
            except (OSError, AttributeError) as e:
                # 如果 os.startfile 不可用,回退到 start 命令
                logger.debug(f"os.startfile failed, trying start command: {e}")
                # 修正 start 命令语法: start "窗口标题" "URL"
                result = subprocess.run(
                    f'start "" "{aido_url}"',
                    shell=True,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0 and result.stderr:
                    logger.warning(f"Windows start command failed: {result.stderr}")
        elif system == "linux":  # Linux
            result = subprocess.run(
                ["xdg-open", aido_url], check=False, capture_output=True, text=True
            )
            if result.returncode != 0 and result.stderr:
                logger.warning(f"Linux xdg-open command failed: {result.stderr}")
        else:
            logger.warning(f"Unsupported operating system: {system}")
            return

        logger.info(f"Executed aido link on {system}: {aido_url}")
    except Exception as e:
        logger.error(f"Failed to execute aido link: {str(e)}", exc_info=True)


mcp = FastMCP("VideoEditServer")


@mcp.tool()
def change_aspect_ratio(
    video_path: str,
    output_video_path: str,
    target_aspect_ratio: str,
    resize_mode: str = "pad",
    padding_color: str = "black",
) -> str:
    """调整视频的画面纵横比。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        target_aspect_ratio: 目标纵横比字符串，格式 '宽:高'（如 '16:9'、'4:3'、'1:1'）。
        resize_mode: 调整模式，'pad' 表示等比缩放并补边，'crop' 表示居中裁剪以适配。
        padding_color: 当使用 'pad' 时的补边颜色（例如 'black'、'white'、'#RRGGBB'）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(video_path, output_video_path)
    try:
        probe = _ffprobe_probe(video_path)
        video_stream_info = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        if not video_stream_info:
            raise RuntimeError("Error: No video stream found in the input file.")

        original_width = int(video_stream_info["width"])
        original_height = int(video_stream_info["height"])

        num, den = map(int, target_aspect_ratio.split(":"))
        target_ar_val = num / den
        original_ar_val = original_width / original_height

        vf_filter = ""

        if resize_mode == "pad":
            if abs(original_ar_val - target_ar_val) < 1e-4:
                try:
                    _ffmpeg_run(
                        ffmpeg.input(video_path).output(output_video_path, c="copy"),
                        capture_stdout=True,
                        capture_stderr=True,
                    )
                    return f"Video aspect ratio already matches. Copied to {output_video_path}."
                except ffmpeg.Error:
                    _ffmpeg_run(
                        ffmpeg.input(video_path).output(output_video_path),
                        capture_stdout=True,
                        capture_stderr=True,
                    )
                    return f"Video aspect ratio already matches. Re-encoded to {output_video_path}."

            # 计算两种可能的目标尺寸，选择能完全包含原视频的方案
            # 方案1：保持原高度，计算新宽度
            option1_w = int(original_height * target_ar_val)
            option1_h = original_height

            # 方案2：保持原宽度，计算新高度
            option2_w = original_width
            option2_h = int(original_width / target_ar_val)

            # 选择能完全包含原视频的方案（尺寸不小于原尺寸）
            if option1_w >= original_width and option1_h >= original_height:
                final_w = option1_w
                final_h = option1_h
            elif option2_w >= original_width and option2_h >= original_height:
                final_w = option2_w
                final_h = option2_h
            else:
                # 如果两种方案都无法完全包含，选择尺寸更大的方案并确保不小于原尺寸
                if option1_w * option1_h > option2_w * option2_h:
                    final_w = max(option1_w, original_width)
                    final_h = max(option1_h, original_height)
                else:
                    final_w = max(option2_w, original_width)
                    final_h = max(option2_h, original_height)

            vf_filter = f"scale={final_w}:{final_h}:force_original_aspect_ratio=decrease,pad={final_w}:{final_h}:(ow-iw)/2:(oh-ih)/2:{padding_color}"

        elif resize_mode == "crop":
            if abs(original_ar_val - target_ar_val) < 1e-4:
                try:
                    _ffmpeg_run(
                        ffmpeg.input(video_path).output(output_video_path, c="copy"),
                        capture_stdout=True,
                        capture_stderr=True,
                    )
                    return f"Video aspect ratio already matches. Copied to {output_video_path}."
                except ffmpeg.Error:
                    _ffmpeg_run(
                        ffmpeg.input(video_path).output(output_video_path),
                        capture_stdout=True,
                        capture_stderr=True,
                    )
                    return f"Video aspect ratio already matches. Re-encoded to {output_video_path}."

            if original_ar_val > target_ar_val:
                new_width = int(original_height * target_ar_val)
                vf_filter = f"crop={new_width}:{original_height}:(iw-{new_width})/2:0"
            else:
                new_height = int(original_width / target_ar_val)
                vf_filter = f"crop={original_width}:{new_height}:0:(ih-{new_height})/2"
        else:
            raise RuntimeError(
                f"Error: Invalid resize_mode '{resize_mode}'. Must be 'pad' or 'crop'."
            )

        try:
            _ffmpeg_run(
                ffmpeg.input(video_path).output(
                    output_video_path,
                    vf=vf_filter,
                    vcodec="libx264",
                    pix_fmt="yuv420p",
                    acodec="copy",
                ),
                capture_stdout=True,
                capture_stderr=True,
            )
            return f"Video aspect ratio changed (audio copy) to {target_aspect_ratio} using {resize_mode}. Saved to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                _ffmpeg_run(
                    ffmpeg.input(video_path).output(
                        output_video_path,
                        vf=vf_filter,
                        vcodec="libx264",
                        pix_fmt="yuv420p",
                    ),
                    capture_stdout=True,
                    capture_stderr=True,
                )
                return f"Video aspect ratio changed (audio re-encoded) to {target_aspect_ratio} using {resize_mode}. Saved to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = (
                    e_acopy.stderr.decode("utf8") if e_acopy.stderr else str(e_acopy)
                )
                err_recode_msg = (
                    e_recode_all.stderr.decode("utf8")
                    if e_recode_all.stderr
                    else str(e_recode_all)
                )
                raise RuntimeError(
                    f"Error changing aspect ratio. Audio copy attempt failed: {err_acopy_msg}. Full re-encode attempt also failed: {err_recode_msg}."
                )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error changing aspect ratio: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: Input video file not found at {video_path}")
    except ValueError:
        raise RuntimeError(
            f"Error: Invalid target_aspect_ratio format. Expected 'num:den' (e.g., '16:9')."
        )
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def add_subtitles(
    video_path: str, srt_file_path: str, output_video_path: str, font_style: dict = None
) -> str:
    """将 SRT 字幕烧录到视频上（默认显示在视频底部居中位置）。

    Args:
        video_path: 输入视频文件路径。
        srt_file_path: 字幕文件路径（SRT 格式）。
        output_video_path: 输出视频文件路径。
        font_style: 字幕样式配置字典（可选）。支持键：
            - font_name: 字体名（如 'Arial'）。
            - font_file: 字体文件路径（如 '/path/to/font.ttf'）。
            - font_size: 字号（整数，默认 24）。
            - font_color: 主颜色（默认 'white'，支持颜色名或十六进制如 '#FFFFFF'）。
            - outline_color: 描边颜色（如 'black'）。
            - outline_width: 描边宽度（整数，默认 2）。
            - shadow_color: 阴影颜色。
            - alignment: 字幕位置（SSA v4 样式，默认 2）：
                * 1=左下角  2=底部居中（推荐）  3=右下角
                * 5=左上角  6=顶部居中          7=右上角
                * 9=左中    10=正中心           11=右中
                ⚠️ 注意：4 和 8 未定义，请勿使用
                重要：字幕通常应该放在底部，建议使用 2（底部居中）
            - margin_v: 垂直边距，距离底部的像素数（默认 50）。
            - margin_l/margin_r: 左右边距（整数）。
            - x_position: 水平位置（像素或表达式，如 '(w-text_w)/2'）。
            - y_position: 垂直位置（像素或表达式，如 'h-text_h-50'）。

    Returns:
        A status message indicating success or failure.

    示例:
        # 使用默认样式（底部居中，白色字体）
        add_subtitles("video.mp4", "subs.srt", "output.mp4")

        # 自定义样式但保持底部显示
        add_subtitles("video.mp4", "subs.srt", "output.mp4",
                     {"font_size": 32, "font_color": "yellow", "alignment": 2, "outline_width": 3})

        # 使用自定义字体和位置
        add_subtitles("video.mp4", "subs.srt", "output.mp4",
                     {"font_file": "/path/to/font.ttf", "font_size": 28, "font_color": "#00FF00"})
    """
    _prepare_path(video_path, output_video_path)
    try:
        logger.info(
            f"[add_subtitles] 开始处理字幕 - video: {video_path}, srt: {srt_file_path}, font_style: {font_style}"
        )

        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        if not os.path.exists(srt_file_path):
            raise RuntimeError(f"Error: SRT subtitle file not found at {srt_file_path}")

        input_stream = ffmpeg.input(video_path)
        logger.info(f"[add_subtitles] 创建输入流成功")

        # 设置默认字幕样式：底部居中显示
        default_style = {
            "alignment": 2,  # 底部居中对齐
            "margin_v": 50,  # 距离底部50像素
            "font_size": 24,  # 默认字体大小
            "font_color": "white",  # 默认白色字体
            "outline_width": 2,  # 默认描边宽度
        }

        # 如果用户提供了自定义样式，合并到默认样式中
        if font_style:
            logger.info(f"[add_subtitles] 合并用户样式: {font_style}")
            default_style.update(font_style)

            # 智能调整 margin_v：如果用户指定了非底部对齐，且没有显式设置 margin_v，则设为 0
            if "alignment" in font_style and "margin_v" not in font_style:
                alignment = font_style["alignment"]
                # SSA v4 样式：alignment 为 1,2,3 是底部对齐，保留默认的 margin_v
                # alignment 为 5,6,7 (顶部) 或 9,10,11 (中部) 不是底部对齐，应该将 margin_v 设为 0
                if alignment not in [1, 2, 3]:
                    default_style["margin_v"] = 0
                    logger.info(
                        f"[add_subtitles] 检测到非底部对齐 (alignment={alignment})，自动设置 margin_v=0"
                    )

        # 检测字幕文件是否包含中文字符，自动添加中文字体
        has_chinese_in_style = False
        if "font_file" not in default_style and "font_name" not in default_style:
            try:
                with open(srt_file_path, "r", encoding="utf-8") as f:
                    srt_content = f.read()
                    if any("\u4e00" <= char <= "\u9fff" for char in srt_content):
                        # 自动选择中文字体
                        default_cn_fonts = [
                            ("PingFang SC", "/System/Library/Fonts/PingFang.ttc"),
                            ("STHeiti", "/System/Library/Fonts/STHeiti Medium.ttc"),
                            (
                                "Hiragino Sans GB",
                                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                            ),
                            ("Arial Unicode MS", "/Library/Fonts/Arial Unicode.ttf"),
                        ]
                        for font_name, font_path in default_cn_fonts:
                            if os.path.exists(font_path):
                                default_style["font_name"] = font_name
                                default_style["font_file"] = font_path
                                has_chinese_in_style = True
                                logger.info(
                                    f"[add_subtitles] 检测到中文，自动使用字体: {font_name} ({font_path})"
                                )
                                break
            except Exception as e:
                logger.warning(f"[add_subtitles] 检测中文字符失败: {e}")

        logger.info(f"[add_subtitles] 最终样式: {default_style}")

        # 辅助函数：将颜色名或 RGB 十六进制转换为 ASS 格式的 BGR 颜色
        def _color_to_ass(color_input):
            """将颜色转换为 ASS 字幕格式 (&HBBGGRR 或 &HAABBGGRR)"""
            if color_input is None:
                return None

            color_str = str(color_input).lower().strip()

            # 颜色名称映射到 RGB 值
            color_map = {
                "white": (255, 255, 255),
                "black": (0, 0, 0),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "yellow": (255, 255, 0),
                "cyan": (0, 255, 255),
                "magenta": (255, 0, 255),
                "gray": (128, 128, 128),
                "grey": (128, 128, 128),
                "orange": (255, 165, 0),
                "purple": (128, 0, 128),
                "pink": (255, 192, 203),
            }

            # 如果是颜色名称，获取 RGB 值
            if color_str in color_map:
                r, g, b = color_map[color_str]
            # 如果是十六进制格式 #RRGGBB
            elif color_str.startswith("#") and len(color_str) == 7:
                try:
                    r = int(color_str[1:3], 16)
                    g = int(color_str[3:5], 16)
                    b = int(color_str[5:7], 16)
                except ValueError:
                    logger.warning(f"Invalid color format: {color_input}, using white")
                    r, g, b = 255, 255, 255
            else:
                logger.warning(f"Unknown color format: {color_input}, using white")
                r, g, b = 255, 255, 255

            # 转换为 ASS 格式的 BGR 颜色（格式：&HBBGGRR）
            return f"&H{b:02X}{g:02X}{r:02X}"

        style_args = []
        if "font_name" in default_style:
            style_args.append(f"FontName={default_style['font_name']}")
        if "font_size" in default_style:
            style_args.append(f"FontSize={default_style['font_size']}")
        if "font_color" in default_style:
            # 将颜色转换为 ASS 格式
            color = _color_to_ass(default_style["font_color"])
            if color:
                style_args.append(f"PrimaryColour={color}")
        if "outline_color" in default_style:
            outline_color = _color_to_ass(default_style["outline_color"])
            if outline_color:
                style_args.append(f"OutlineColour={outline_color}")
        if "outline_width" in default_style:
            style_args.append(f"Outline={default_style['outline_width']}")
        if "shadow_color" in default_style:
            shadow_color = _color_to_ass(default_style["shadow_color"])
            if shadow_color:
                style_args.append(f"ShadowColour={shadow_color}")
        if "shadow_offset_x" in default_style or "shadow_offset_y" in default_style:
            shadow_val = default_style.get(
                "shadow_offset_x", default_style.get("shadow_offset_y", 1)
            )
            style_args.append(f"Shadow={shadow_val}")
        if "alignment" in default_style:
            style_args.append(f"Alignment={default_style['alignment']}")
        if "margin_v" in default_style:
            style_args.append(f"MarginV={default_style['margin_v']}")
        if "margin_l" in default_style:
            style_args.append(f"MarginL={default_style['margin_l']}")
        if "margin_r" in default_style:
            style_args.append(f"MarginR={default_style['margin_r']}")

        logger.info(f"[add_subtitles] 生成的样式参数: {style_args}")

        safe_srt_path = (
            srt_file_path.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")
        )
        vf_filter_value = f"subtitles='{safe_srt_path}'"
        if style_args:
            vf_filter_value += f":force_style='{','.join(style_args)}'"

        logger.info(f"[add_subtitles] 滤镜字符串: {vf_filter_value}")

        # 如果指定了字体文件，使用 subtitles 滤镜的 fontsdir 参数
        if "font_file" in default_style:
            font_path = default_style["font_file"]
            if os.path.exists(font_path):
                font_dir = os.path.dirname(font_path)
                safe_font_dir = (
                    font_dir.replace("\\", "\\\\")
                    .replace("'", "\\'")
                    .replace(":", "\\:")
                )
                vf_filter_value += f":fontsdir='{safe_font_dir}'"
                logger.info(f"[add_subtitles] 使用字体目录: {font_dir}")

        logger.info(f"[add_subtitles] 准备创建输出流...")

        try:
            output_stream = input_stream.output(
                output_video_path,
                vf=vf_filter_value,
                vcodec="libx264",
                pix_fmt="yuv420p",
                acodec="copy",
            )
            logger.info(f"[add_subtitles] 输出流创建成功，准备运行 ffmpeg...")
        except Exception as e:
            logger.error(
                f"[add_subtitles] 创建输出流失败: {type(e).__name__}: {str(e)}"
            )
            import traceback

            logger.error(f"[add_subtitles] 堆栈跟踪:\n{traceback.format_exc()}")
            raise

        try:
            _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)
            return f"Subtitles added successfully (audio copied) to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            output_stream_recode_audio = input_stream.output(
                output_video_path,
                vf=vf_filter_value,
                vcodec="libx264",
                pix_fmt="yuv420p",
                acodec="aac",
            )
            try:
                _ffmpeg_run(
                    output_stream_recode_audio, capture_stdout=True, capture_stderr=True
                )
                return f"Subtitles added successfully (audio re-encoded) to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = (
                    e_acopy.stderr.decode("utf8") if e_acopy.stderr else str(e_acopy)
                )
                err_recode_msg = (
                    e_recode_all.stderr.decode("utf8")
                    if e_recode_all.stderr
                    else str(e_recode_all)
                )
                raise RuntimeError(
                    f"Error adding subtitles. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}"
                )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error adding subtitles: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: A specified file was not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def add_text_watermark(
    video_path: str,
    output_video_path: str,
    watermark_text: str,
    font_size: int = 24,
    font_color: str = "white",
    position: str = "bottom_right",
    opacity: float = 0.7,
    font_file: str = None,
    outline_color: str = None,
    outline_width: int = 0,
    box: bool = False,
    box_color: str = "black@0.5",
    box_padding: int = 5,
) -> str:
    """为视频添加文字水印（全程显示）。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        watermark_text: 水印文字内容。
        font_size: 字体大小（默认 24）。
        font_color: 字体颜色（默认 'white'，支持颜色名或十六进制如 '#FFFFFF'）。
        position: 水印位置，可选值：
            - 'top_left': 左上角
            - 'top_center': 顶部居中
            - 'top_right': 右上角
            - 'center_left': 左侧居中
            - 'center': 正中心
            - 'center_right': 右侧居中
            - 'bottom_left': 左下角
            - 'bottom_center': 底部居中
            - 'bottom_right': 右下角（默认）
            - 或自定义表达式如 'x=100:y=100'
        opacity: 透明度（0.0-1.0，默认 0.7）。
        font_file: 字体文件路径（可选，用于支持中文等特殊字体）。
        outline_color: 描边颜色（可选）。
        outline_width: 描边宽度（默认 0）。
        box: 是否显示背景框（默认 False）。
        box_color: 背景框颜色（默认 'black@0.5'，半透明黑色）。
        box_padding: 背景框内边距（默认 5）。

    Returns:
        成功或失败的状态消息。

    示例:
        # 简单水印
        add_text_watermark("video.mp4", "output.mp4", "© 2024 MyCompany")

        # 自定义样式的水印
        add_text_watermark("video.mp4", "output.mp4", "我的水印",
                          font_size=32, font_color="yellow", position="top_right",
                          opacity=0.8, box=True)

        # 使用自定义字体
        add_text_watermark("video.mp4", "output.mp4", "中文水印",
                          font_file="/path/to/chinese_font.ttf",
                          font_size=28, position="bottom_center")
    """
    _prepare_path(video_path, output_video_path)
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")

        # 转义特殊字符
        safe_text = (
            watermark_text.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace(":", "\\:")
            .replace(",", "\\,")
        )

        # 计算位置
        position_map = {
            "top_left": ("10", "10"),
            "top_center": ("(w-text_w)/2", "10"),
            "top_right": ("w-text_w-10", "10"),
            "center_left": ("10", "(h-text_h)/2"),
            "center": ("(w-text_w)/2", "(h-text_h)/2"),
            "center_right": ("w-text_w-10", "(h-text_h)/2"),
            "bottom_left": ("10", "h-text_h-10"),
            "bottom_center": ("(w-text_w)/2", "h-text_h-10"),
            "bottom_right": ("w-text_w-10", "h-text_h-10"),
        }

        if position in position_map:
            x_pos, y_pos = position_map[position]
        elif ":" in position:
            # 自定义位置表达式
            parts = position.split(":")
            x_pos = "w-text_w-10"
            y_pos = "h-text_h-10"
            for part in parts:
                if part.startswith("x="):
                    x_pos = part.split("=")[1]
                elif part.startswith("y="):
                    y_pos = part.split("=")[1]
        else:
            raise RuntimeError(f"Error: Invalid position '{position}'")

        # 构建 drawtext 滤镜参数
        filter_params = [
            f"text='{safe_text}'",
            f"fontsize={font_size}",
            f"fontcolor={font_color}@{opacity}",  # 添加透明度
            f"x={x_pos}",
            f"y={y_pos}",
        ]

        # 添加字体文件
        if font_file and os.path.exists(font_file):
            safe_font_path = (
                font_file.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")
            )
            filter_params.append(f"fontfile='{safe_font_path}'")
        else:
            # 检测是否包含中文字符，自动选择中文字体
            if any("\u4e00" <= char <= "\u9fff" for char in watermark_text):
                default_cn_fonts = [
                    "/System/Library/Fonts/PingFang.ttc",
                    "/System/Library/Fonts/STHeiti Medium.ttc",
                    "/Library/Fonts/Arial Unicode.ttf",
                ]
                for font in default_cn_fonts:
                    if os.path.exists(font):
                        safe_font_path = (
                            font.replace("\\", "\\\\")
                            .replace("'", "\\'")
                            .replace(":", "\\:")
                        )
                        filter_params.append(f"fontfile='{safe_font_path}'")
                        logger.info(f"使用中文字体: {font}")
                        break

        # 添加描边
        if outline_color and outline_width > 0:
            filter_params.append(f"bordercolor={outline_color}")
            filter_params.append(f"borderw={outline_width}")

        # 添加背景框
        if box:
            filter_params.append("box=1")
            filter_params.append(f"boxcolor={box_color}")
            filter_params.append(f"boxborderw={box_padding}")

        drawtext_filter = f"drawtext={':'.join(filter_params)}"

        input_stream = ffmpeg.input(video_path)

        try:
            stream = input_stream.output(
                output_video_path,
                vf=drawtext_filter,
                vcodec="libx264",
                pix_fmt="yuv420p",
                acodec="copy",
            )
            _ffmpeg_run(stream, capture_stdout=True, capture_stderr=True)
            return f"Text watermark added successfully to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                stream_recode = input_stream.output(
                    output_video_path,
                    vf=drawtext_filter,
                    vcodec="libx264",
                    pix_fmt="yuv420p",
                    acodec="aac",
                )
                _ffmpeg_run(stream_recode, capture_stdout=True, capture_stderr=True)
                return f"Text watermark added successfully (audio re-encoded) to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = (
                    e_acopy.stderr.decode("utf8") if e_acopy.stderr else str(e_acopy)
                )
                err_recode_msg = (
                    e_recode_all.stderr.decode("utf8")
                    if e_recode_all.stderr
                    else str(e_recode_all)
                )
                raise RuntimeError(
                    f"Error adding text watermark. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}"
                )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error processing text watermark: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: Input video file not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def add_text_overlay(
    video_path: str, output_video_path: str, text_elements: list[dict]
) -> str:
    """为视频添加按时间区间显示的文本叠加。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        text_elements: 文本元素列表，每个元素为字典，常见键：
            - text: 文本内容（必填）。
            - start_time/end_time: 起止时间（秒或 'HH:MM:SS'）。
            - font_size: 字号（整数，默认 24）。
            - font_color: 字体颜色（默认 'white'）。
            - x_pos/y_pos: 位置表达式或像素（默认居中/底部上方）。
            - box: 是否显示背景框（布尔）。
            - box_color/box_border_width: 背景框颜色与边框宽度。
            - font_file: 字体文件路径（可选）。
            - box_padding: 背景框内边距（整数，默认 5）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(video_path, output_video_path)
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        if not text_elements:
            raise RuntimeError("Error: No text elements provided for overlay.")

        input_stream = ffmpeg.input(video_path)
        drawtext_filters = []

        for element in text_elements:
            text = element.get("text")
            start_time = element.get("start_time")
            end_time = element.get("end_time")
            if text is None or start_time is None or end_time is None:
                raise RuntimeError(
                    f"Error: Text element is missing required keys (text, start_time, end_time)."
                )
            safe_text = (
                text.replace("\\", "\\\\")
                .replace("'", "\\'")
                .replace(":", "\\:")
                .replace(",", "\\,")
            )
            # 将时间统一转换为秒
            start_sec = _parse_time_to_seconds(start_time)
            end_sec = _parse_time_to_seconds(end_time)

            # 获取配置参数
            font_size = element.get("font_size", 48)  # 增加默认字体大小
            font_color = element.get("font_color", "white")
            x_pos = element.get("x_pos", "(w-text_w)/2")
            y_pos = element.get("y_pos", "h-text_h-50")  # 距离底部更远一些
            box_padding = element.get("box_padding", 10)  # 背景框内边距

            filter_params = [
                f"text='{safe_text}'",
                f"fontsize={font_size}",
                f"fontcolor={font_color}",
                f"x={x_pos}",
                f"y={y_pos}",
                f"enable=between(t\\,{start_sec}\\,{end_sec})",
            ]

            # 处理背景框
            if element.get("box", False):
                filter_params.append("box=1")
                # 默认使用半透明黑色背景，确保文字清晰可见
                box_color = element.get("box_color", "black@0.7")
                filter_params.append(f"boxcolor={box_color}")

                # 设置边框宽度，确保文字与边框有足够间距
                box_border_width = element.get("box_border_width", box_padding)
                filter_params.append(f"boxborderw={box_border_width}")

                # 如果使用黑色背景，自动将文字颜色改为白色以提高对比度
                if "black" in box_color.lower() and font_color.lower() == "black":
                    filter_params[2] = "fontcolor=white"
                    logger.info(f"自动调整文字颜色为白色以提高与黑色背景的对比度")

            # 处理字体文件
            if "font_file" in element:
                font_path = (
                    element["font_file"]
                    .replace("\\", "\\\\")
                    .replace("'", "\\'")
                    .replace(":", "\\:")
                )
                filter_params.append(f"fontfile='{font_path}'")
            else:
                # 对于中文，尝试使用系统默认的中文字体
                # 检测文本是否包含中文字符
                if any("\u4e00" <= char <= "\u9fff" for char in text):
                    # macOS 系统默认中文字体路径
                    default_cn_fonts = [
                        "/System/Library/Fonts/PingFang.ttc",
                        "/System/Library/Fonts/STHeiti Medium.ttc",
                        "/Library/Fonts/Arial Unicode.ttf",
                        "/System/Library/Fonts/Helvetica.ttc",
                    ]
                    for font in default_cn_fonts:
                        if os.path.exists(font):
                            safe_font_path = (
                                font.replace("\\", "\\\\")
                                .replace("'", "\\'")
                                .replace(":", "\\:")
                            )
                            filter_params.append(f"fontfile='{safe_font_path}'")
                            logger.info(f"使用中文字体: {font}")
                            break
            drawtext_filter = f"drawtext={':'.join(filter_params)}"
            drawtext_filters.append(drawtext_filter)

        final_vf_filter = ",".join(drawtext_filters)

        try:
            stream = input_stream.output(
                output_video_path,
                vf=final_vf_filter,
                vcodec="libx264",
                pix_fmt="yuv420p",
                acodec="copy",
            )
            _ffmpeg_run(stream, capture_stdout=True, capture_stderr=True)
            return f"Text overlays added successfully to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                stream_recode = input_stream.output(
                    output_video_path,
                    vf=final_vf_filter,
                    vcodec="libx264",
                    pix_fmt="yuv420p",
                    acodec="aac",
                )
                _ffmpeg_run(stream_recode, capture_stdout=True, capture_stderr=True)
                return f"Text overlays added successfully to {output_video_path}"
            except ffmpeg.Error as e_recode_all:
                err_acopy_msg = (
                    e_acopy.stderr.decode("utf8") if e_acopy.stderr else str(e_acopy)
                )
                err_recode_msg = (
                    e_recode_all.stderr.decode("utf8")
                    if e_recode_all.stderr
                    else str(e_recode_all)
                )
                raise RuntimeError(
                    f"Error adding text overlays. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}"
                )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error processing text overlays: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: Input video file not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def add_image_overlay(
    video_path: str,
    output_video_path: str,
    image_path: str,
    position: str = "top_right",
    opacity: float = None,
    start_time: str = None,
    end_time: str = None,
    width: str = None,
    height: str = None,
) -> str:
    """为视频添加图片叠加（水印/徽标）。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        image_path: 叠加图片路径（支持透明通道）。
        position: 预设位置 'top_left'|'top_right'|'bottom_left'|'bottom_right'|'center'，或 'x=..:y=..' 自定义。
        opacity: 透明度（0.0~1.0）。
        start_time: 生效开始时间（秒或 'HH:MM:SS'）。
        end_time: 生效结束时间（秒或 'HH:MM:SS'）。
        width/height: 目标尺寸（像素或表达式；只设其一时另一边按比例自适应）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(video_path, output_video_path)
    try:
        if not os.path.exists(video_path):
            raise RuntimeError(f"Error: Input video file not found at {video_path}")
        if not os.path.exists(image_path):
            raise RuntimeError(f"Error: Overlay image file not found at {image_path}")

        main_input = ffmpeg.input(video_path)
        overlay_input = ffmpeg.input(image_path)
        processed_overlay = overlay_input

        if width or height:
            # ffmpeg scale 使用 w/h 参数，而非 width/height
            w_val = width if width else "-1"
            h_val = height if height else "-1"
            processed_overlay = processed_overlay.filter("scale", w=w_val, h=h_val)

        if opacity is not None and 0.0 <= opacity <= 1.0:
            processed_overlay = processed_overlay.filter("format", "rgba")
            processed_overlay = processed_overlay.filter(
                "colorchannelmixer", aa=str(opacity)
            )

        overlay_x_pos = "0"
        overlay_y_pos = "0"
        if position == "top_left":
            overlay_x_pos, overlay_y_pos = "10", "10"
        elif position == "top_right":
            overlay_x_pos, overlay_y_pos = "main_w-overlay_w-10", "10"
        elif position == "bottom_left":
            overlay_x_pos, overlay_y_pos = "10", "main_h-overlay_h-10"
        elif position == "bottom_right":
            overlay_x_pos, overlay_y_pos = "main_w-overlay_w-10", "main_h-overlay_h-10"
        elif position == "center":
            overlay_x_pos, overlay_y_pos = (
                "(main_w-overlay_w)/2",
                "(main_h-overlay_h)/2",
            )
        elif ":" in position:
            pos_parts = position.split(":")
            for part in pos_parts:
                if part.startswith("x="):
                    overlay_x_pos = part.split("=")[1]
                if part.startswith("y="):
                    overlay_y_pos = part.split("=")[1]

        overlay_filter_kwargs = {"x": overlay_x_pos, "y": overlay_y_pos}
        if start_time is not None or end_time is not None:
            # 将起止时间转换为秒
            actual_start_sec = (
                _parse_time_to_seconds(start_time) if start_time is not None else 0
            )
            if end_time is not None:
                actual_end_sec = _parse_time_to_seconds(end_time)
                enable_expr = f"between(t,{actual_start_sec},{actual_end_sec})"
            else:
                enable_expr = f"gte(t,{actual_start_sec})"
            overlay_filter_kwargs["enable"] = enable_expr

        try:
            video_with_overlay = ffmpeg.filter(
                [main_input, processed_overlay], "overlay", **overlay_filter_kwargs
            )
            # 若输入无音频，则仅输出视频流
            probe = _ffprobe_probe(video_path)
            has_audio = any(s["codec_type"] == "audio" for s in probe["streams"])
            if has_audio:
                output_node = ffmpeg.output(
                    video_with_overlay,
                    main_input.audio,
                    output_video_path,
                    vcodec="libx264",
                    pix_fmt="yuv420p",
                    acodec="copy",
                )
            else:
                output_node = ffmpeg.output(
                    video_with_overlay,
                    output_video_path,
                    vcodec="libx264",
                    pix_fmt="yuv420p",
                )
            _ffmpeg_run(output_node, capture_stdout=True, capture_stderr=True)
            return f"Image overlay added successfully to {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                video_with_overlay_fallback = ffmpeg.filter(
                    [main_input, processed_overlay], "overlay", **overlay_filter_kwargs
                )
                probe = _ffprobe_probe(video_path)
                has_audio = any(s["codec_type"] == "audio" for s in probe["streams"])
                if has_audio:
                    output_node_fallback = ffmpeg.output(
                        video_with_overlay_fallback,
                        main_input.audio,
                        output_video_path,
                        vcodec="libx264",
                        pix_fmt="yuv420p",
                        acodec="aac",
                    )
                else:
                    output_node_fallback = ffmpeg.output(
                        video_with_overlay_fallback,
                        output_video_path,
                        vcodec="libx264",
                        pix_fmt="yuv420p",
                    )
                _ffmpeg_run(
                    output_node_fallback, capture_stdout=True, capture_stderr=True
                )
                return f"Image overlay added successfully to {output_video_path}"
            except ffmpeg.Error as e_recode:
                err_acopy_msg = (
                    e_acopy.stderr.decode("utf8") if e_acopy.stderr else str(e_acopy)
                )
                err_recode_msg = (
                    e_recode.stderr.decode("utf8") if e_recode.stderr else str(e_recode)
                )
                raise RuntimeError(
                    f"Error adding image overlay. Audio copy attempt: {err_acopy_msg}. Full re-encode attempt: {err_recode_msg}"
                )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error processing image overlay: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(
            f"Error: An input file was not found (video: '{video_path}', image: '{image_path}'). Please check paths."
        )
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred in add_image_overlay: {str(e)}"
        )


@mcp.tool()
def concatenate_videos(
    video_paths: list[str],
    output_video_path: str,
    transition_effect: str = None,
    transition_duration: float = None,
) -> str:
    """拼接视频序列，并可选两段间的过渡效果。

    Args:
        video_paths: 输入视频路径列表（至少 1 个）。
        output_video_path: 输出视频文件路径。
        transition_effect: 过渡效果（可选）。支持 'dissolve'|'fade'|'wipeleft'|'wiperight'|'wipeup'|'wipedown'|'slideleft'|'slideright'|'slideup'|'slidedown' 等。
        transition_duration: 过渡时长（秒，>0；仅在指定 transition_effect 且两段时有效）。

    Returns:
        A status message indicating success or failure.
    """
    if not video_paths:
        raise RuntimeError("Error: No video paths provided for concatenation.")
    if len(video_paths) < 1:
        raise RuntimeError("Error: At least one video is required.")
    for video_path in video_paths:
        _prepare_path(video_path, output_video_path)
    if transition_effect and transition_duration is None:
        raise RuntimeError(
            "Error: transition_duration is required when transition_effect is specified."
        )
    if transition_effect and transition_duration <= 0:
        raise RuntimeError("Error: transition_duration must be positive.")

    valid_transitions = {
        "dissolve",
        "fade",
        "fadeblack",
        "fadewhite",
        "fadegrays",
        "distance",
        "wipeleft",
        "wiperight",
        "wipeup",
        "wipedown",
        "slideleft",
        "slideright",
        "slideup",
        "slidedown",
        "smoothleft",
        "smoothright",
        "smoothup",
        "smoothdown",
        "circlecrop",
        "rectcrop",
        "circleopen",
        "circleclose",
        "vertopen",
        "vertclose",
        "horzopen",
        "horzclose",
        "diagtl",
        "diagtr",
        "diagbl",
        "diagbr",
        "hlslice",
        "hrslice",
        "vuslice",
        "vdslice",
        "pixelize",
        "radial",
        "hblur",
    }
    if transition_effect and transition_effect not in valid_transitions:
        raise RuntimeError(
            f"Error: Invalid transition_effect '{transition_effect}'. Valid options: {', '.join(sorted(valid_transitions))}"
        )

    if len(video_paths) == 1:
        try:
            _ffmpeg_run(
                ffmpeg.input(video_paths[0]).output(
                    output_video_path, vcodec="libx264", acodec="aac"
                ),
                capture_stdout=True,
                capture_stderr=True,
            )
            return f"Single video processed and saved to {output_video_path}"
        except ffmpeg.Error as e:
            raise RuntimeError(
                f"Error processing single video: {e.stderr.decode('utf8') if e.stderr else str(e)}"
            )

    if transition_effect and len(video_paths) == 2:
        temp_dir = tempfile.mkdtemp()
        try:
            video1_path = video_paths[0]
            video2_path = video_paths[1]
            props1 = _get_media_properties(video1_path)
            props2 = _get_media_properties(video2_path)
            if not props1["has_video"] or not props2["has_video"]:
                raise RuntimeError(
                    "Error: xfade transition requires both inputs to be videos."
                )
            if transition_duration >= props1["duration"]:
                raise RuntimeError(
                    f"Error: Transition duration ({transition_duration}s) cannot be equal or longer than the first video's duration ({props1['duration']})."
                )

            has_audio = props1["has_audio"] and props2["has_audio"]
            target_w = max(props1["width"], props2["width"], 640)
            target_h = max(props1["height"], props2["height"], 360)
            target_fps = max(props1["avg_fps"], props2["avg_fps"], 30)
            if target_fps <= 0:
                target_fps = 30

            norm_video1_path = os.path.join(temp_dir, "norm_video1.mp4")
            try:
                subprocess.run(
                    [
                        FFMPEG_BINARY,
                        "-i",
                        video1_path,
                        "-vf",
                        f"scale={target_w}:{target_h}",
                        "-r",
                        str(target_fps),
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "-c:a",
                        "aac",
                        "-y",
                        norm_video1_path,
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Error normalizing first video: {e.stderr.decode('utf8') if e.stderr else str(e)}"
                )

            norm_video2_path = os.path.join(temp_dir, "norm_video2.mp4")
            try:
                subprocess.run(
                    [
                        FFMPEG_BINARY,
                        "-i",
                        video2_path,
                        "-vf",
                        f"scale={target_w}:{target_h}",
                        "-r",
                        str(target_fps),
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "-c:a",
                        "aac",
                        "-y",
                        norm_video2_path,
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Error normalizing second video: {e.stderr.decode('utf8') if e.stderr else str(e)}"
                )

            norm_props1 = _get_media_properties(norm_video1_path)
            norm_video1_duration = norm_props1["duration"]
            if transition_duration >= norm_video1_duration:
                raise RuntimeError(
                    f"Error: Transition duration ({transition_duration}s) is too long for the normalized first video ({norm_video1_duration}s)."
                )

            offset = norm_video1_duration - transition_duration
            # 标注视频与音频输出标签，便于 -map 精确映射
            filter_complex = f"[0:v][1:v]xfade=transition={transition_effect}:duration={transition_duration}:offset={offset}[v]"
            cmd = [
                FFMPEG_BINARY,
                "-i",
                norm_video1_path,
                "-i",
                norm_video2_path,
                "-filter_complex",
            ]
            if has_audio:
                filter_complex += (
                    f";[0:a][1:a]acrossfade=d={transition_duration}:c1=tri:c2=tri[a]"
                )
                cmd.extend([filter_complex, "-map", "[v]", "-map", "[a]"])
            else:
                cmd.extend([filter_complex, "-map", "[v]"])
            cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-y", output_video_path])

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                return f"Videos concatenated successfully with '{transition_effect}' transition to {output_video_path}"
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Error during xfade process: {e.stderr.decode('utf8') if e.stderr else str(e)}"
                )
            except Exception as e:
                raise RuntimeError(
                    f"An unexpected error occurred during xfade concatenation: {str(e)}"
                )
        finally:
            shutil.rmtree(temp_dir)

    temp_dir = tempfile.mkdtemp()
    try:
        normalized_paths = []
        first_props = _get_media_properties(video_paths[0])
        target_w = first_props["width"] if first_props["width"] > 0 else 1280
        target_h = first_props["height"] if first_props["height"] > 0 else 720
        target_fps = first_props["avg_fps"] if first_props["avg_fps"] > 0 else 30
        if target_fps <= 0:
            target_fps = 30

        for i, video_path in enumerate(video_paths):
            norm_path = os.path.join(temp_dir, f"norm_{i}.mp4")
            try:
                subprocess.run(
                    [
                        FFMPEG_BINARY,
                        "-i",
                        video_path,
                        "-vf",
                        f"scale={target_w}:{target_h}",
                        "-r",
                        str(target_fps),
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "-c:a",
                        "aac",
                        "-y",
                        norm_path,
                    ],
                    check=True,
                    capture_output=True,
                )
                normalized_paths.append(norm_path)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f"Error normalizing video {i}: {e.stderr.decode('utf8') if e.stderr else str(e)}"
                )

        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for path in normalized_paths:
                f.write(f"file '{path}'\n")

        try:
            subprocess.run(
                [
                    FFMPEG_BINARY,
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    concat_list_path,
                    "-c",
                    "copy",
                    "-y",
                    output_video_path,
                ],
                check=True,
                capture_output=True,
            )
            return f"Videos concatenated successfully to {output_video_path}"
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Error during concatenation: {e.stderr.decode('utf8') if e.stderr else str(e)}"
            )
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred during standard concatenation: {str(e)}"
        )
    finally:
        shutil.rmtree(temp_dir)


@mcp.tool()
def change_video_speed(
    video_path: str, output_video_path: str, speed_factor: float
) -> str:
    """改变视频的播放速度（同时处理音频）。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        speed_factor: 倍速因子（>0，例如 2.0 表示 2 倍速，0.5 表示半速）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(video_path, output_video_path)
    if speed_factor <= 0:
        raise RuntimeError("Error: Speed factor must be positive.")
    try:
        atempo_value = speed_factor
        atempo_filters = []
        if speed_factor < 0.5:
            while atempo_value < 0.5:
                atempo_filters.append("atempo=0.5")
                atempo_value *= 2
            if atempo_value < 0.99:
                atempo_filters.append(f"atempo={atempo_value}")
        elif speed_factor > 2.0:
            while atempo_value > 2.0:
                atempo_filters.append("atempo=2.0")
                atempo_value /= 2
            if atempo_value > 1.01:
                atempo_filters.append(f"atempo={atempo_value}")
        else:
            atempo_filters.append(f"atempo={speed_factor}")

        # 检查是否有音频轨
        probe = _ffprobe_probe(video_path)
        has_audio = any(s["codec_type"] == "audio" for s in probe["streams"])

        input_stream = ffmpeg.input(video_path)

        # 使用更精确的PTS调整公式
        # 对于加速播放，PTS需要除以speed_factor
        pts_formula = f"PTS/{speed_factor}"
        video = input_stream.video.filter("setpts", pts_formula)

        if has_audio:
            audio = input_stream.audio
            for filter_str in atempo_filters:
                # 解析每个 atempo 滤镜的具体值
                if filter_str == "atempo=0.5":
                    tempo_val = 0.5
                elif filter_str == "atempo=2.0":
                    tempo_val = 2.0
                elif filter_str.startswith("atempo="):
                    tempo_val = float(filter_str.replace("atempo=", ""))
                else:
                    tempo_val = speed_factor
                audio = audio.filter("atempo", tempo_val)

            # 为音频也设置PTS以确保同步
            audio = audio.filter("asetpts", pts_formula)
            output = ffmpeg.output(
                video, audio, output_video_path, vcodec="libx264", acodec="aac"
            )
        else:
            output = ffmpeg.output(video, output_video_path, vcodec="libx264")

        _ffmpeg_run(output, capture_stdout=True, capture_stderr=True)
        return f"Video speed changed by factor {speed_factor} and saved to {output_video_path}"
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error changing video speed: {error_message}")
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred while changing video speed: {str(e)}"
        )


@mcp.tool()
def remove_silence(
    media_path: str,
    output_media_path: str,
    silence_threshold_db: int = -30,
    min_silence_duration_ms: int = 500,
    padding_seconds: float = 0.2,
) -> str:
    """移除音频/视频中的静音时段。

    Args:
        media_path: 输入媒体文件路径（音频或视频）。
        output_media_path: 输出媒体文件路径。
        silence_threshold_db: 静音判定阈值（dBFS，默认 -30）。
        min_silence_duration_ms: 触发删除的最小静音时长（毫秒，默认 500）。
        padding_seconds: 保留片段前后的缓冲时间（秒，默认 0.1）。

    Returns:
        A status message indicating success or failure.
    """
    # 兼容整数或字符串形式的参数，统一转换为数值类型
    try:
        silence_threshold_db = int(silence_threshold_db)
    except (TypeError, ValueError):
        raise RuntimeError("Error: silence_threshold_db must be an integer value.")
    try:
        min_silence_duration_ms = int(min_silence_duration_ms)
    except (TypeError, ValueError):
        raise RuntimeError("Error: min_silence_duration_ms must be an integer value.")

    _prepare_path(media_path, output_media_path)
    if min_silence_duration_ms <= 0:
        raise RuntimeError("Error: Minimum silence duration must be positive.")

    min_silence_duration_s = min_silence_duration_ms / 1000.0

    try:
        # 获取媒体信息
        probe = _ffprobe_probe(media_path)
        has_video = any(s["codec_type"] == "video" for s in probe["streams"])
        has_audio = any(s["codec_type"] == "audio" for s in probe["streams"])

        if not has_audio:
            # 如果没有音频流，直接复制
            _ffmpeg_run(
                ffmpeg.input(media_path).output(output_media_path, c="copy"),
                capture_stdout=True,
                capture_stderr=True,
            )
            return (
                f"No audio stream found. Original media copied to {output_media_path}."
            )

        # 使用 silenceremove 滤镜直接移除静音，这比手动切割更可靠
        input_stream = ffmpeg.input(media_path)

        # 构建滤镜链
        if has_video and has_audio:
            # 对音频应用 silenceremove 滤镜
            audio_filtered = input_stream.audio.filter(
                "silenceremove",
                start_periods=1,
                start_duration=min_silence_duration_s,
                start_threshold=f"{silence_threshold_db}dB",
                detection="peak",
                stop_periods=-1,
                stop_duration=min_silence_duration_s,
                stop_threshold=f"{silence_threshold_db}dB",
            )

            # 视频需要与音频同步，使用 aselect 和 select 滤镜
            # 先检测静音片段
            silence_detection_process = (
                ffmpeg.input(media_path)
                .filter(
                    "silencedetect",
                    n=f"{silence_threshold_db}dB",
                    d=min_silence_duration_s,
                )
                .output("-", format="null")
                .run_async(pipe_stderr=True, cmd=FFMPEG_BINARY)
            )
            _, stderr_bytes = silence_detection_process.communicate()
            stderr_str = stderr_bytes.decode("utf8")

            # 解析静音时间点
            silence_starts = [
                float(x) for x in re.findall(r"silence_start: (\d+\.?\d*)", stderr_str)
            ]
            silence_ends = [
                float(x) for x in re.findall(r"silence_end: (\d+\.?\d*)", stderr_str)
            ]

            if not silence_starts:
                # 没有检测到静音，直接复制
                _ffmpeg_run(
                    ffmpeg.input(media_path).output(output_media_path, c="copy"),
                    capture_stdout=True,
                    capture_stderr=True,
                )
                return f"No significant silences detected. Original media copied to {output_media_path}."

            # 计算需要保留的时间段
            total_duration = float(probe["format"]["duration"])
            keep_segments = []
            current_pos = 0.0

            # 确保 silence_ends 和 silence_starts 数量匹配
            for i in range(len(silence_starts)):
                silence_start = silence_starts[i]
                silence_end = (
                    silence_ends[i] if i < len(silence_ends) else total_duration
                )

                # 添加静音前的片段，并在前后添加缓冲时间
                if silence_start > current_pos:
                    # 计算带缓冲的片段边界
                    segment_start = max(0.0, current_pos - padding_seconds)
                    segment_end = min(total_duration, silence_start + padding_seconds)

                    # 确保片段有效且不与之前的片段重叠
                    if segment_end > segment_start and (
                        not keep_segments or segment_start >= keep_segments[-1][1]
                    ):
                        keep_segments.append((segment_start, segment_end))
                    elif keep_segments and segment_start < keep_segments[-1][1]:
                        # 如果有重叠，扩展上一个片段的结束时间
                        keep_segments[-1] = (keep_segments[-1][0], segment_end)

                current_pos = silence_end

            # 添加最后一个片段，并添加缓冲时间
            if current_pos < total_duration:
                segment_start = max(0.0, current_pos - padding_seconds)
                segment_end = total_duration

                # 确保片段有效且不与之前的片段重叠
                if segment_end > segment_start and (
                    not keep_segments or segment_start >= keep_segments[-1][1]
                ):
                    keep_segments.append((segment_start, segment_end))
                elif keep_segments and segment_start < keep_segments[-1][1]:
                    # 如果有重叠，扩展上一个片段的结束时间
                    keep_segments[-1] = (keep_segments[-1][0], segment_end)

            if not keep_segments:
                raise RuntimeError(
                    "Error: No audio segments to keep. The media might be entirely silent."
                )

            # 使用 concat 滤镜来连接片段，这样可以确保时长一致
            video_inputs = []
            audio_inputs = []

            for start, end in keep_segments:
                duration = end - start
                if duration > 0.1:  # 只保留大于0.1秒的片段
                    segment_input = ffmpeg.input(media_path, ss=start, t=duration)
                    video_inputs.append(segment_input["v"])
                    audio_inputs.append(segment_input["a"])

            if not video_inputs:
                raise RuntimeError("Error: No valid segments to concatenate.")

            # 连接所有片段
            if len(video_inputs) == 1:
                # 只有一个片段，直接输出
                video_output = video_inputs[0]
                audio_output = audio_inputs[0]
            else:
                # 多个片段，使用 concat 滤镜
                video_output = ffmpeg.filter(
                    video_inputs, "concat", n=len(video_inputs), v=1, a=0
                )
                audio_output = ffmpeg.filter(
                    audio_inputs, "concat", n=len(audio_inputs), v=0, a=1
                )

            # 输出设置
            output_kwargs = {
                "vcodec": "libx264",
                "acodec": "aac",
                "preset": "medium",
                "crf": "23",
            }

            _ffmpeg_run(
                ffmpeg.output(
                    video_output, audio_output, output_media_path, **output_kwargs
                ),
                capture_stdout=True,
                capture_stderr=True,
            )

        elif has_audio:
            # 只有音频的情况
            audio_filtered = input_stream.filter(
                "silenceremove",
                start_periods=1,
                start_duration=min_silence_duration_s,
                start_threshold=f"{silence_threshold_db}dB",
                detection="peak",
                stop_periods=-1,
                stop_duration=min_silence_duration_s,
                stop_threshold=f"{silence_threshold_db}dB",
            )

            _ffmpeg_run(
                ffmpeg.output(audio_filtered, output_media_path, acodec="aac"),
                capture_stdout=True,
                capture_stderr=True,
            )
        else:
            raise RuntimeError(
                "Error: No audio or video streams found in the input file."
            )

        return f"Silent segments removed. Output saved to {output_media_path}"

    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error removing silence: {error_message}")
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred while removing silence: {str(e)}"
        )


def _validate_and_fix_broll_clips(broll_clips) -> list[dict]:
    """验证和修正 B-roll 配置参数，处理模型传递参数错误的问题"""
    if not broll_clips:
        return []

    # 如果传递的是单个字典而不是列表，自动包装为列表
    if isinstance(broll_clips, dict):
        broll_clips = [broll_clips]

    # 如果传递的不是列表，尝试转换
    if not isinstance(broll_clips, list):
        raise ValueError(f"broll_clips 必须是字典列表，收到: {type(broll_clips)}")

    fixed_clips = []
    valid_positions = {
        "fullscreen",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
        "center",
    }

    for i, clip in enumerate(broll_clips):
        if not isinstance(clip, dict):
            raise ValueError(f"broll_clips[{i}] 必须是字典，收到: {type(clip)}")

        fixed_clip = {}

        # 验证并修正必需字段 clip_path
        clip_path = clip.get("clip_path") or clip.get("path") or clip.get("video_path")
        if not clip_path:
            raise ValueError(
                f"broll_clips[{i}] 缺少必需字段 'clip_path'。当前字段: {list(clip.keys())}"
            )
        fixed_clip["clip_path"] = str(clip_path)

        # 验证并修正必需字段 insert_at_timestamp
        timestamp = (
            clip.get("insert_at_timestamp")
            or clip.get("timestamp")
            or clip.get("start_time")
            or clip.get("insert_at")
        )
        if timestamp is None:
            raise ValueError(
                f"broll_clips[{i}] 缺少必需字段 'insert_at_timestamp'。当前字段: {list(clip.keys())}"
            )
        fixed_clip["insert_at_timestamp"] = str(timestamp)

        # 可选字段的修正
        duration = clip.get("duration")
        if duration is not None:
            fixed_clip["duration"] = str(duration)

        position = clip.get("position", "fullscreen")
        if position not in valid_positions:
            print(
                f"警告: broll_clips[{i}] 位置 '{position}' 无效，使用默认值 'fullscreen'"
            )
            position = "fullscreen"
        fixed_clip["position"] = position

        scale = clip.get("scale")
        if scale is not None:
            try:
                fixed_clip["scale"] = float(scale)
            except (ValueError, TypeError):
                print(f"警告: broll_clips[{i}] scale 值 '{scale}' 无效，将使用默认值")

        # 过渡效果
        for trans_field in ["transition_in", "transition_out"]:
            if trans_field in clip:
                fixed_clip[trans_field] = str(clip[trans_field])

        transition_duration = clip.get("transition_duration")
        if transition_duration is not None:
            try:
                fixed_clip["transition_duration"] = float(transition_duration)
            except (ValueError, TypeError):
                print(
                    f"警告: broll_clips[{i}] transition_duration 值 '{transition_duration}' 无效，将使用默认值"
                )

        audio_mix = clip.get("audio_mix")
        if audio_mix is not None:
            try:
                fixed_clip["audio_mix"] = float(audio_mix)
            except (ValueError, TypeError):
                print(
                    f"警告: broll_clips[{i}] audio_mix 值 '{audio_mix}' 无效，将使用默认值"
                )

        fixed_clips.append(fixed_clip)

    return fixed_clips


@mcp.tool()
def add_b_roll(
    main_video_path: str, broll_clips: list[dict], output_video_path: str
) -> str:
    """按时间在主视频上叠加 B-roll 画面。

    Args:
        main_video_path: 主视频文件路径。
        broll_clips: B-roll 配置列表。每项必需键：
            - clip_path: B-roll 视频路径（必需）
            - insert_at_timestamp: 插入时间，秒数或 'HH:MM:SS' 格式（必需）
            可选键：
            - duration: 叠加时长（秒），默认使用整个 B-roll 视频时长
            - position: 叠加位置，可选值: 'fullscreen'(默认)|'top-left'|'top-right'|'bottom-left'|'bottom-right'|'center'
            - scale: 缩放系数（浮点数），全屏默认1.0，其他位置默认0.5
            - transition_in/transition_out: 过渡类型，可选值: 'fade'
            - transition_duration: 过渡时长（秒），默认0.5
            - audio_mix: 音频混合占比（0.0-1.0），0.0表示不混合

        output_video_path: 输出视频文件路径。

    Returns:
        成功或失败的状态消息

    示例用法:
        broll_clips = [
            {
                "clip_path": "/path/to/broll1.mp4",
                "insert_at_timestamp": "00:00:10",
                "duration": 5.0,
                "position": "top-right",
                "scale": 0.3
            }
        ]
    """
    _prepare_path(main_video_path, output_video_path)

    # 验证和修正参数
    try:
        broll_clips = _validate_and_fix_broll_clips(broll_clips)
    except ValueError as e:
        return f"参数错误: {str(e)}\n\n正确的 broll_clips 格式示例:\n[{{\n  'clip_path': '/path/to/video.mp4',\n  'insert_at_timestamp': '00:01:30',\n  'duration': 5.0,\n  'position': 'top-right'\n}}]"
    if not broll_clips:
        try:
            _ffmpeg_run(
                ffmpeg.input(main_video_path).output(output_video_path, c="copy"),
                capture_stdout=True,
                capture_stderr=True,
            )
            return f"No B-roll clips provided. Main video copied to {output_video_path}"
        except ffmpeg.Error as e:
            raise RuntimeError(
                f"No B-roll clips, but error copying main video: {e.stderr.decode('utf8') if e.stderr else str(e)}"
            )

    valid_positions = {
        "fullscreen",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
        "center",
    }
    try:
        temp_dir = tempfile.mkdtemp()
        try:
            main_props = _get_media_properties(main_video_path)
            if not main_props["has_video"]:
                raise RuntimeError(
                    f"Error: Main video {main_video_path} has no video stream."
                )
            main_width = main_props["width"]
            main_height = main_props["height"]

            processed_clips = []
            for i, broll_item in enumerate(
                sorted(
                    broll_clips,
                    key=lambda x: _parse_time_to_seconds(x["insert_at_timestamp"]),
                )
            ):
                clip_path = broll_item["clip_path"]
                if not os.path.exists(clip_path):
                    raise RuntimeError(f"Error: B-roll clip not found at {clip_path}")
                broll_props = _get_media_properties(clip_path)
                if not broll_props["has_video"]:
                    continue

                start_time = _parse_time_to_seconds(broll_item["insert_at_timestamp"])
                duration = _parse_time_to_seconds(
                    broll_item.get("duration", str(broll_props["duration"]))
                )
                position = broll_item.get("position", "fullscreen")
                if position not in valid_positions:
                    raise RuntimeError(
                        f"Error: Invalid position '{position}' for B-roll {clip_path}"
                    )

                temp_clip = os.path.join(temp_dir, f"processed_broll_{i}.mp4")
                scale_factor = broll_item.get(
                    "scale", 1.0 if position == "fullscreen" else 0.5
                )
                scale_filter_parts = []
                if position == "fullscreen":
                    scale_filter_parts.append(f"scale={main_width}:{main_height}")
                else:
                    scale_filter_parts.append(
                        f"scale=iw*{scale_factor}:ih*{scale_factor}"
                    )

                transition_in = broll_item.get("transition_in")
                transition_out = broll_item.get("transition_out")
                transition_duration = float(broll_item.get("transition_duration", 0.5))
                if transition_in == "fade":
                    scale_filter_parts.append(f"fade=t=in:st=0:d={transition_duration}")
                if transition_out == "fade":
                    fade_out_start = max(
                        0, float(broll_props["duration"]) - transition_duration
                    )
                    scale_filter_parts.append(
                        f"fade=t=out:st={fade_out_start}:d={transition_duration}"
                    )
                filter_string = ",".join(scale_filter_parts)

                try:
                    subprocess.run(
                        [
                            FFMPEG_BINARY,
                            "-i",
                            clip_path,
                            "-vf",
                            filter_string,
                            "-c:v",
                            "libx264",
                            "-c:a",
                            "aac",
                            "-y",
                            temp_clip,
                        ],
                        check=True,
                        capture_output=True,
                    )
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(
                        f"Error processing B-roll {i}: {e.stderr.decode('utf8') if e.stderr else str(e)}"
                    )

                overlay_x = "0"
                overlay_y = "0"
                if position == "top-left":
                    overlay_x, overlay_y = "10", "10"
                elif position == "top-right":
                    overlay_x, overlay_y = "main_w-overlay_w-10", "10"
                elif position == "bottom-left":
                    overlay_x, overlay_y = "10", "main_h-overlay_h-10"
                elif position == "bottom-right":
                    overlay_x, overlay_y = "main_w-overlay_w-10", "main_h-overlay_h-10"
                elif position == "center":
                    overlay_x, overlay_y = (
                        "(main_w-overlay_w)/2",
                        "(main_h-overlay_h)/2",
                    )

                processed_clips.append(
                    {
                        "path": temp_clip,
                        "start_time": start_time,
                        "duration": duration,
                        "position": position,
                        "overlay_x": overlay_x,
                        "overlay_y": overlay_y,
                        "transition_in": transition_in,
                        "transition_out": transition_out,
                        "transition_duration": transition_duration,
                        "audio_mix": float(broll_item.get("audio_mix", 0.0)),
                    }
                )

            if not processed_clips:
                try:
                    shutil.copy(main_video_path, output_video_path)
                    return f"No valid B-roll clips to overlay. Main video copied to {output_video_path}"
                except Exception as e:
                    raise RuntimeError(
                        f"No valid B-roll clips, but error copying main video: {str(e)}"
                    )

            filter_parts = []
            main_overlay = "[0:v]"
            for i, clip in enumerate(processed_clips):
                current_label = f"[v{i}]"
                overlay_index = i + 1
                overlay_filter = (
                    f"{main_overlay}[{overlay_index}:v]overlay="
                    f"x={clip['overlay_x']}:y={clip['overlay_y']}:"
                    f"enable='between(t,{clip['start_time']},{clip['start_time'] + clip['duration']})'"
                )
                if i < len(processed_clips) - 1:
                    overlay_filter += current_label
                    main_overlay = current_label
                else:
                    overlay_filter += "[v]"
                filter_parts.append(overlay_filter)

            filter_complex = ";".join(filter_parts)
            audio_output = []
            if main_props["has_audio"]:
                audio_output = ["-map", "0:a"]

            input_files = ["-i", main_video_path]
            for clip in processed_clips:
                input_files.extend(["-i", clip["path"]])

            cmd = [
                FFMPEG_BINARY,
                *input_files,
                "-filter_complex",
                filter_complex,
                "-map",
                "[v]",
                *audio_output,
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-y",
                output_video_path,
            ]
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                return f"B-roll clips added successfully as overlays. Output at {output_video_path}"
            except subprocess.CalledProcessError as e:
                error_message = e.stderr.decode("utf8") if e.stderr else str(e)
                raise RuntimeError(
                    f"Error in final B-roll composition: {error_message}"
                )
        finally:
            shutil.rmtree(temp_dir)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error adding B-roll overlays: {error_message}")
    except ValueError as e:
        raise RuntimeError(f"Error with input values (e.g., time format): {str(e)}")
    except RuntimeError as e:
        raise RuntimeError(f"Runtime error during B-roll processing: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in add_b_roll: {str(e)}")


@mcp.tool()
def add_basic_transitions(
    video_path: str,
    output_video_path: str,
    transition_type: str,
    duration_seconds: float,
) -> str:
    """为整段视频添加淡入或淡出过渡效果。

    Args:
        video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径。
        transition_type: 过渡类型，'fade_in' 或 'fade_out'。
        duration_seconds: 过渡时长（秒，>0）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(video_path, output_video_path)
    if duration_seconds <= 0:
        raise RuntimeError("Error: Transition duration must be positive.")
    try:
        props = _get_media_properties(video_path)
        video_total_duration = props["duration"]
        if duration_seconds > video_total_duration:
            raise RuntimeError(
                f"Error: Transition duration ({duration_seconds}s) cannot exceed video duration ({video_total_duration}s)."
            )
        input_stream = ffmpeg.input(video_path)
        video_stream = input_stream.video
        audio_stream = input_stream.audio
        if transition_type == "fade_in" or transition_type == "crossfade_from_black":
            processed_video = video_stream.filter(
                "fade", type="in", start_time=0, duration=duration_seconds
            )
        elif transition_type == "fade_out" or transition_type == "crossfade_to_black":
            fade_start_time = video_total_duration - duration_seconds
            processed_video = video_stream.filter(
                "fade",
                type="out",
                start_time=fade_start_time,
                duration=duration_seconds,
            )
        else:
            raise RuntimeError(
                f"Error: Unsupported transition_type '{transition_type}'. Supported: 'fade_in', 'fade_out'."
            )

        output_streams = []
        if props["has_video"]:
            output_streams.append(processed_video)
        if props["has_audio"]:
            output_streams.append(audio_stream)
        if not output_streams:
            raise RuntimeError(
                "Error: No suitable video or audio streams found to apply transition."
            )
        try:
            output_kwargs = {"vcodec": "libx264", "pix_fmt": "yuv420p"}
            if props["has_audio"]:
                output_kwargs["acodec"] = "copy"
            _ffmpeg_run(
                ffmpeg.output(*output_streams, output_video_path, **output_kwargs),
                capture_stdout=True,
                capture_stderr=True,
            )
            return f"Transition '{transition_type}' applied successfully. Output: {output_video_path}"
        except ffmpeg.Error as e_acopy:
            try:
                _ffmpeg_run(
                    ffmpeg.output(
                        *output_streams,
                        output_video_path,
                        vcodec="libx264",
                        pix_fmt="yuv420p",
                    ),
                    capture_stdout=True,
                    capture_stderr=True,
                )
                return f"Transition '{transition_type}' applied successfully. Output: {output_video_path}"
            except ffmpeg.Error as e_recode:
                err_acopy = (
                    e_acopy.stderr.decode("utf8") if e_acopy.stderr else str(e_acopy)
                )
                err_recode = (
                    e_recode.stderr.decode("utf8") if e_recode.stderr else str(e_recode)
                )
                raise RuntimeError(
                    f"Error applying transition. Audio copy failed: {err_acopy}. Full re-encode failed: {err_recode}."
                )
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error applying basic transition: {error_message}")
    except ValueError as e:
        raise RuntimeError(f"Error with input values: {str(e)}")
    except RuntimeError as e:
        raise RuntimeError(f"Runtime error during transition processing: {str(e)}")
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred in add_basic_transitions: {str(e)}"
        )


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
