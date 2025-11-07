from mcp.server.fastmcp import FastMCP, Context
import ffmpeg
import os  # For checking file existence if needed, though ffmpeg handles it
import shutil  # For cleaning up temporary directories
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import tempfile
import json
import platform
import urllib.parse
import subprocess
import time

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 防止 basicConfig 被早期初始化抵消

package = "audio-processor-mcp"

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

FFMPEG_BINARY = os.environ.get("FFMPEG_BINARY")
FFPROBE_BINARY = os.environ.get("FFPROBE_BINARY")


# --- ffmpeg/ffprobe helpers that always use resolved binaries ---
def _ffmpeg_run(stream_spec, **kwargs):
    """Run ffmpeg with an explicit binary path to avoid env propagation issues."""
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BINARY, **kwargs)


def _ffprobe_probe(path: str, **kwargs):
    """Probe media with explicit ffprobe binary."""
    return ffmpeg.probe(path, cmd=FFPROBE_BINARY, **kwargs)


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


# Create an MCP server instance
mcp = FastMCP("AudioProcessing")


@mcp.tool()
def convert_audio_properties(
    input_audio_path: str,
    output_audio_path: str,
    target_format: str,
    bitrate: str | None = None,
    sample_rate: int | None = None,
    channels: int | None = None,
    sample_format: str | None = None,
    ctx: Context = None,
) -> str:
    """Convert audio format and properties (bitrate/sample_rate/channels). WAV doesn't support bitrate, use sample_format instead.

    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the converted audio file.
        target_format: Desired output audio format (e.g., 'mp3', 'wav', 'aac').
        bitrate: Target audio bitrate (e.g., '128k', '192k'). Optional. Not applicable to WAV/PCM.
        sample_rate: Target audio sample rate in Hz (e.g., 44100, 48000). Optional.
        channels: Number of audio channels (1 for mono, 2 for stereo). Optional.
        sample_format: For WAV/PCM, choose sample format such as 's16'|'s24'|'s32'|'flt'. Optional.
    Returns:
        A status message indicating success or failure.
    """
    execution_start_time = time.time()
    try:
        _prepare_path(input_audio_path, output_audio_path)

        stream = ffmpeg.input(input_audio_path)
        kwargs: dict = {}

        tgt_fmt = (target_format or "").lower()
        is_wav = tgt_fmt in {"wav", "wave"} or output_audio_path.lower().endswith(
            ".wav"
        )

        if is_wav and bitrate:
            raise RuntimeError(
                "Error: WAV/PCM doesn't support bitrate; please use sample_format (e.g., 's16'/'s24'/'s32'/'flt')"
            )

        # 通用属性
        if sample_rate:
            kwargs["ar"] = sample_rate
        if channels:
            kwargs["ac"] = channels
        kwargs["format"] = target_format

        # Sample format/encoder mapping for WAV
        if is_wav and sample_format:
            sf = sample_format.lower()
            pcm_map = {
                "s16": "pcm_s16le",
                "s24": "pcm_s24le",
                "s32": "pcm_s32le",
                "flt": "pcm_f32le",
            }
            if sf in pcm_map:
                kwargs["acodec"] = pcm_map[sf]
            else:
                # Pass sample_fmt directly, let ffmpeg decide appropriate pcm_*
                kwargs["sample_fmt"] = sf
        else:
            # Non-WAV formats support bitrate
            if bitrate:
                kwargs["audio_bitrate"] = bitrate

        output_stream = stream.output(output_audio_path, **kwargs)
        _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)

        # 计算执行时间
        execution_time = time.time() - execution_start_time
        result_message = f"Audio converted successfully to {output_audio_path} with format {target_format} and specified properties. Execution time: {execution_time:.2f} seconds."

        # 只有执行时间超过1秒才调用 _open_aido_link
        if execution_time > 1:
            _open_aido_link(ctx, output_audio_path)

        return result_message
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        logger.error(f"FFmpeg error in convert_audio_properties: {error_message}")
        raise RuntimeError(f"Error converting audio properties: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in convert_audio_properties: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in convert_audio_properties: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


# --- Granular Audio Property Tools ---
@mcp.tool()
def convert_audio_format(
    input_audio_path: str,
    output_audio_path: str,
    target_format: str,
    ctx: Context = None,
) -> str:
    """Converts an audio file to the specified target format with appropriate codec.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the converted audio file.
        target_format: Desired output audio format (e.g., 'mp3', 'wav', 'aac', 'm4a', 'wma', 'flac', 'ogg').
    Returns:
        A status message indicating success or failure.
    """
    execution_start_time = time.time()
    try:
        _prepare_path(input_audio_path, output_audio_path)

        # Format to codec mapping
        format_codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "m4a": "aac",  # M4A typically uses AAC codec
            "wma": "wmav2",  # Windows Media Audio v2
            "wav": "pcm_s16le",  # WAV with 16-bit PCM
            "flac": "flac",
            "ogg": "libvorbis",
            "opus": "libopus",
        }

        # Get appropriate codec for the target format
        codec = format_codec_map.get(target_format.lower())

        # Build output parameters
        output_params = {}

        if codec:
            output_params["acodec"] = codec

        # Special container format handling
        if target_format.lower() == "m4a":
            output_params["f"] = "mp4"  # M4A is AAC in MP4 container
        elif target_format.lower() == "aac":
            output_params["f"] = "adts"  # AAC files use ADTS container
        elif target_format.lower() == "wma":
            output_params["f"] = "asf"  # WMA is in ASF container
        # For other formats, use the target_format as container format
        else:
            output_params["f"] = target_format.lower()

        # Convert the audio
        stream = ffmpeg.input(input_audio_path)
        output_stream = stream.output(output_audio_path, **output_params)
        _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)

        # 计算执行时间
        execution_time = time.time() - execution_start_time
        result_message = f"Audio format converted to {target_format} and saved to {output_audio_path}. Execution time: {execution_time:.2f} seconds."

        # 只有执行时间超过1秒才调用 _open_aido_link
        if execution_time > 1:
            _open_aido_link(ctx, output_audio_path)

        return result_message

    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        logger.error(f"FFmpeg error in convert_audio_format: {error_message}")
        raise RuntimeError(f"Error converting audio format: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in convert_audio_format: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in convert_audio_format: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def set_audio_bitrate(
    input_audio_path: str, output_audio_path: str, bitrate: str, ctx: Context = None
) -> str:
    """Sets the bitrate for an audio file with appropriate codec selection.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new bitrate.
        bitrate: Target audio bitrate (e.g., '128k', '192k', '320k').
    Returns:
        A status message indicating success or failure.
    """
    execution_start_time = time.time()
    try:
        _prepare_path(input_audio_path, output_audio_path)

        # Validate bitrate format
        import re

        if not re.match(r"^\d+[kmKM]?$", bitrate):
            raise RuntimeError(
                f"Error: Invalid bitrate format '{bitrate}'. Use format like '128k', '192k', '320k'"
            )

        # Check if output format supports bitrate
        lossless_extensions = [".wav", ".flac", ".ape", ".alac"]
        input_ext = os.path.splitext(input_audio_path)[1].lower()
        output_ext = os.path.splitext(output_audio_path)[1].lower()

        if output_ext in lossless_extensions:
            raise RuntimeError(
                f"Error: {output_ext.upper()} format doesn't support bitrate; please use convert_audio_properties with sample_format instead"
            )

        # Detect input codec to preserve original format when possible
        input_codec = None
        try:
            probe_info = _ffprobe_probe(input_audio_path)
            streams = probe_info.get("streams", [])
            for stream in streams:
                if stream.get("codec_type") == "audio":
                    input_codec = stream.get("codec_name")
                    logger.info(f"Detected input codec: {input_codec}")
                    break
        except Exception as e:
            logger.warning(f"Could not detect input codec: {str(e)}")

        # Determine appropriate codec based on output format
        format_codec_map = {
            ".mp3": "libmp3lame",
            ".aac": "aac",
            ".m4a": "aac",
            ".wma": "wmav2",
            ".ogg": "libvorbis",
            ".opus": "libopus",
        }

        output_params = {"audio_bitrate": bitrate}

        # Preserve original codec if input and output extensions match
        if input_ext == output_ext and input_codec:
            # Map common codec names to ffmpeg encoder names
            codec_encoder_map = {
                "opus": "libopus",
                "vorbis": "libvorbis",
                "mp3": "libmp3lame",
                "aac": "aac",
                "wmav2": "wmav2",
            }
            if input_codec in codec_encoder_map:
                output_params["acodec"] = codec_encoder_map[input_codec]
                logger.info(f"Preserving original codec: {input_codec} -> {codec_encoder_map[input_codec]}")
            else:
                logger.warning(f"Unknown codec {input_codec}, using default mapping")
                if output_ext in format_codec_map:
                    output_params["acodec"] = format_codec_map[output_ext]
        # Use format mapping if extensions differ or codec detection failed
        elif output_ext in format_codec_map:
            output_params["acodec"] = format_codec_map[output_ext]

        # Special container format handling
        if output_ext == ".m4a":
            output_params["f"] = "mp4"
        elif output_ext == ".wma":
            output_params["f"] = "asf"

        _ffmpeg_run(
            ffmpeg.input(input_audio_path).output(output_audio_path, **output_params),
            capture_stdout=True,
            capture_stderr=True,
        )

        # 计算执行时间
        execution_time = time.time() - execution_start_time
        result_message = f"Audio bitrate set to {bitrate} and saved to {output_audio_path}. Execution time: {execution_time:.2f} seconds."

        # 只有执行时间超过1秒才调用 _open_aido_link
        if execution_time > 1:
            _open_aido_link(ctx, output_audio_path)

        return result_message

    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        logger.error(f"FFmpeg error in set_audio_bitrate: {error_message}")
        raise RuntimeError(f"Error setting audio bitrate: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in set_audio_bitrate: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in set_audio_bitrate: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def set_audio_sample_rate(
    input_audio_path: str, output_audio_path: str, sample_rate: int, ctx: Context = None
) -> str:
    """Sets the sample rate for an audio file.
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new sample rate.
        sample_rate: Target audio sample rate in Hz (e.g., 44100, 48000).
    Returns:
        A status message indicating success or failure.
    """
    execution_start_time = time.time()
    try:
        _prepare_path(input_audio_path, output_audio_path)

        # Validate input file exists
        if not os.path.exists(input_audio_path):
            raise RuntimeError(
                f"Error: Input audio file not found at {input_audio_path}"
            )

        # Validate sample rate
        if sample_rate <= 0 or sample_rate > 384000:  # Reasonable upper limit
            raise RuntimeError(
                f"Error: Invalid sample rate {sample_rate}. Must be between 1 and 384000 Hz"
            )

        # Common sample rates validation
        common_rates = [
            8000,
            11025,
            16000,
            22050,
            32000,
            44100,
            48000,
            88200,
            96000,
            176400,
            192000,
            384000,
        ]
        if sample_rate not in common_rates:
            logger.warning(
                f"Uncommon sample rate {sample_rate} Hz specified. Common rates are: {common_rates}"
            )

        _ffmpeg_run(
            ffmpeg.input(input_audio_path).output(output_audio_path, ar=sample_rate),
            capture_stdout=True,
            capture_stderr=True,
        )

        # 计算执行时间
        execution_time = time.time() - execution_start_time
        result_message = f"Audio sample rate set to {sample_rate} Hz and saved to {output_audio_path}. Execution time: {execution_time:.2f} seconds."

        # 只有执行时间超过1秒才调用 _open_aido_link
        if execution_time > 1:
            _open_aido_link(ctx, output_audio_path)

        return result_message

    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        logger.error(f"FFmpeg error in set_audio_sample_rate: {error_message}")
        raise RuntimeError(f"Error setting audio sample rate: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in set_audio_sample_rate: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in set_audio_sample_rate: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def set_audio_channels(
    input_audio_path: str, output_audio_path: str, channels: int, ctx: Context = None
) -> str:
    """Sets the number of channels for an audio file (1 for mono, 2 for stereo, etc.).
    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the audio file with the new channel layout.
        channels: Number of audio channels (1=mono, 2=stereo, 6=5.1, 8=7.1).
    Returns:
        A status message indicating success or failure.
    """
    execution_start_time = time.time()
    try:
        _prepare_path(input_audio_path, output_audio_path)
        # Check if output file already exists
        if os.path.exists(output_audio_path):
            raise RuntimeError(
                f"Error: Output file already exists at {output_audio_path}. Please choose a different path or delete the existing file."
            )

        # Validate input file exists
        if not os.path.exists(input_audio_path):
            raise RuntimeError(
                f"Error: Input audio file not found at {input_audio_path}"
            )

        # Validate channel count
        if channels <= 0 or channels > 32:  # Reasonable upper limit
            raise RuntimeError(
                f"Error: Invalid channel count {channels}. Must be between 1 and 32"
            )

        # Common channel configurations
        channel_descriptions = {
            1: "mono",
            2: "stereo",
            3: "3.0 (L, R, C)",
            4: "4.0 surround",
            5: "5.0 surround",
            6: "5.1 surround",
            7: "7.0 surround",
            8: "7.1 surround",
        }

        description = channel_descriptions.get(channels, f"{channels}-channel")
        logger.info(f"Converting to {description} audio")

        _ffmpeg_run(
            ffmpeg.input(input_audio_path).output(output_audio_path, ac=channels),
            capture_stdout=True,
            capture_stderr=True,
        )

        # 计算执行时间
        execution_time = time.time() - execution_start_time
        result_message = f"Audio channels set to {channels} ({description}) and saved to {output_audio_path}. Execution time: {execution_time:.2f} seconds."

        # 只有执行时间超过1秒才调用 _open_aido_link
        if execution_time > 1:
            _open_aido_link(ctx, output_audio_path)

        return result_message

    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        logger.error(f"FFmpeg error in set_audio_channels: {error_message}")
        raise RuntimeError(f"Error setting audio channels: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in set_audio_channels: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in set_audio_channels: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def slice_audio(
    input_audio_path: str,
    output_audio_path: str,
    start_time: str,
    end_time: str,
    copy_codec: bool = True,
    ctx: Context = None,
) -> str:
    """Extract a segment from an audio file between specified start and end times.

    Args:
        input_audio_path: Path to the source audio file.
        output_audio_path: Path to save the sliced audio segment.
        start_time: Start time in format 'HH:MM:SS', 'MM:SS', or seconds (e.g., '00:01:30', '90', '1:30').
        end_time: End time in same format as start_time (e.g., '00:02:45', '165', '2:45').
        copy_codec: If True, copy codec without re-encoding (faster). If False, re-encode (default: True).

    Returns:
        A status message indicating success or failure.
    """
    execution_start_time = time.time()
    try:
        _prepare_path(input_audio_path, output_audio_path)

        # Validate time format and convert to seconds if needed
        def parse_time(time_str: str) -> float:
            """Parse time string to seconds."""
            time_str = time_str.strip()

            # If it's just a number, treat as seconds
            try:
                return float(time_str)
            except ValueError:
                pass

            # Parse HH:MM:SS or MM:SS format
            parts = time_str.split(":")
            if len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = parts
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
            elif len(parts) == 2:  # MM:SS
                minutes, seconds = parts
                return int(minutes) * 60 + float(seconds)
            else:
                raise ValueError(f"Invalid time format: {time_str}")

        start_seconds = parse_time(start_time)
        end_seconds = parse_time(end_time)

        # Validate time range
        if start_seconds < 0:
            raise RuntimeError(f"Error: Start time cannot be negative: {start_time}")
        if end_seconds <= start_seconds:
            raise RuntimeError(
                f"Error: End time ({end_time}) must be greater than start time ({start_time})"
            )

        # Get audio duration to validate end time
        probe_info = _ffprobe_probe(input_audio_path)
        duration = float(probe_info.get("format", {}).get("duration", 0))

        if duration > 0 and end_seconds > duration:
            logger.warning(
                f"End time {end_seconds}s exceeds audio duration {duration}s. Will trim to end of file."
            )

        # Calculate duration of the slice
        slice_duration = end_seconds - start_seconds

        # Build ffmpeg command
        stream = ffmpeg.input(input_audio_path, ss=start_seconds)

        output_params = {"t": slice_duration}

        if copy_codec:
            # Copy codec without re-encoding (faster)
            output_params["acodec"] = "copy"

        output_stream = stream.output(output_audio_path, **output_params)
        _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)

        # 计算执行时间
        execution_time = time.time() - execution_start_time
        result_message = f"Audio sliced successfully from {start_time} to {end_time} (duration: {slice_duration:.2f}s) and saved to {output_audio_path}. Execution time: {execution_time:.2f} seconds."

        # 只有执行时间超过1秒才调用 _open_aido_link
        if execution_time > 1:
            _open_aido_link(ctx, output_audio_path)

        return result_message

    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        logger.error(f"FFmpeg error in slice_audio: {error_message}")
        raise RuntimeError(f"Error slicing audio: {error_message}")
    except FileNotFoundError:
        logger.error(f"File not found in slice_audio: {input_audio_path}")
        raise RuntimeError(f"Error: Input audio file not found at {input_audio_path}")
    except ValueError as e:
        logger.error(f"Time format error in slice_audio: {str(e)}")
        raise RuntimeError(f"Error parsing time format: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in slice_audio: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


@mcp.tool()
def get_audio_info(audio_path: str) -> str:
    """Get detailed information about an audio file using ffprobe.

    Args:
        audio_path: Path to the audio file to analyze.

    Returns:
        A JSON string containing detailed audio file information including format, streams, metadata, etc.
    """
    try:
        if not os.path.exists(audio_path):
            raise RuntimeError(f"Error: Audio file not found at {audio_path}")

        # Use ffprobe to get detailed information
        # Note: ffmpeg.probe already returns JSON by default, so we don't need print_format='json'
        info = _ffprobe_probe(audio_path)

        # Extract key information for better readability
        format_info = info.get("format", {})
        streams = info.get("streams", [])

        # Find audio stream
        audio_stream = None
        for stream in streams:
            if stream.get("codec_type") == "audio":
                audio_stream = stream
                break

        # Build a summary with consistent format
        audio_data = {
            "file_path": audio_path,
            "format": {
                "format_name": format_info.get("format_name", "Unknown"),
                "duration": format_info.get("duration", "Unknown"),
                "size": format_info.get("size", "Unknown"),
                "bit_rate": format_info.get("bit_rate", "Unknown"),
                "tags": format_info.get("tags", {}),
            },
            "audio_stream": {
                "codec_name": audio_stream.get("codec_name", "Unknown")
                if audio_stream
                else "No audio stream",
                "codec_long_name": audio_stream.get("codec_long_name", "Unknown")
                if audio_stream
                else "No audio stream",
                "sample_rate": audio_stream.get("sample_rate", "Unknown")
                if audio_stream
                else "No audio stream",
                "channels": audio_stream.get("channels", "Unknown")
                if audio_stream
                else "No audio stream",
                "channel_layout": audio_stream.get("channel_layout", "Unknown")
                if audio_stream
                else "No audio stream",
                "bit_rate": audio_stream.get("bit_rate", "Unknown")
                if audio_stream
                else "No audio stream",
                "sample_fmt": audio_stream.get("sample_fmt", "Unknown")
                if audio_stream
                else "No audio stream",
            }
            if audio_stream
            else None,
            "raw_info": info,  # Include full raw information
        }

        # Return with consistent format including isError field
        summary = {"isError": False, "data": audio_data}

        return json.dumps(summary, indent=2, ensure_ascii=False)

    except ffmpeg.Error as e:
        stderr_output = e.stderr.decode("utf8") if e.stderr else "No stderr output"
        error_message = f"ffprobe failed. Command: {e.cmd}. Return code: {e.returncode}. Stderr: {stderr_output}."
        logger.error(f"FFmpeg error in get_audio_info: {error_message}")
        raise RuntimeError(
            f"Error getting audio info: ffprobe failed - {stderr_output}"
        )
    except FileNotFoundError:
        logger.error(f"File not found in get_audio_info: {audio_path}")
        raise RuntimeError(f"Error: Audio file not found at {audio_path}")
    except Exception as e:
        logger.error(f"Unexpected error in get_audio_info: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred in get_audio_info: {str(e)}")


def main():
    """Main entry point for the MCP server."""
    mcp.run()


# Main execution block to run the server
if __name__ == "__main__":
    main()
