# filename: capabilities.py
# @Time    : 2025/11/7 13:56
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
模型能力定义 / Model capability definitions
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelCapabilities:
    """
    模型能力描述 / Model capability description

    使用 frozen=True 使其不可变，确保能力配置的稳定性
    Using frozen=True to make it immutable, ensuring stability of capability configuration
    """

    # 基础能力 / Basic capabilities
    supports_thinking: bool = False  # 是否支持思考（推理）模式 / Whether thinking (reasoning) mode is supported
    supports_vision: bool = False  # 是否支持图片输入 / Whether image input is supported
    supports_audio: bool = False  # 是否支持音频输入 / Whether audio input is supported
    supports_video: bool = False  # 是否支持视频输入 / Whether video input is supported
    supports_pdf: bool = False  # 是否支持PDF输入 / Whether PDF input is supported
    supports_function_calling: bool = False  # 是否支持函数调用 / Whether function calling is supported
    supports_structured_outputs: bool = True  # 是否支持结构化输出 / Whether structured outputs are supported
    supports_json_outputs: bool = True  # 是否支持Json输出，注意这个区别于结构化输出，结构化输出是指可以指定JSONSchema，而Json输出仅仅限制结果为Json形式
    supports_streaming: bool = True  # 是否支持流式输出 / Whether streaming output is supported
    supports_fine_tuning: bool = False  # 是否支持微调 / Whether fine-tuning is supported
    supports_distillation: bool = False  # 是否支持蒸馏 / Whether distillation is supported
    supports_predicted_outputs: bool = False  # 是否支持预测输出 / Whether predicted outputs are supported
    supports_web_search: bool = False  # 是否支持联网搜索工具 / Whether web search tool is supported
    supports_file_search: bool = False  # 是否支持文件检索 / Whether file search tool is supported
    supports_image_generation: bool = False  # 是否支持图像生成工具 / Whether image generation tool is supported
    supports_code_interpreter: bool = False  # 是否支持代码解释器 / Whether code interpreter tool is supported
    supports_computer_use: bool = False  # 是否支持电脑远程操作 / Whether computer use tool is supported
    supports_mcp: bool = False  # 是否支持 MCP / Whether MCP integration is supported

    # 通用限制 / General limitations
    max_tokens: int | None = None  # 最大token数 / Maximum number of tokens
    context_window: int | None = None  # 上下文窗口大小 / Context window size

    # 图片相关限制 / Image-related limitations
    max_image_size_mb: float | None = None  # 最大图片大小(MB) / Maximum image size in MB
    max_image_pixels: tuple[int, int] | None = None  # 最大图片像素(宽, 高) / Maximum image pixels (width, height)
    supported_image_mime_type: list[str] = field(
        default_factory=lambda: ["image/jpeg", "image/png"]
    )  # 支持的图片MIME类型 / Supported image MIME types
    supports_image_base64: bool = True  # 是否支持base64编码的图片 / Whether base64-encoded images are supported

    # 视频相关限制 / Video-related limitations
    max_video_size_mb: float | None = None  # 最大视频大小(MB) / Maximum video size in MB
    max_video_duration_seconds: int | None = None  # 最大视频时长(秒) / Maximum video duration in seconds
    supported_video_mime_type: list[str] = field(
        default_factory=lambda: ["video/mp4", "video/x-msvideo", "video/quicktime"]
    )  # 支持的视频MIME类型 / Supported video MIME types

    # 音频相关限制 / Audio-related limitations
    max_audio_size_mb: float | None = None  # 最大音频大小(MB) / Maximum audio size in MB
    max_audio_duration_seconds: int | None = None  # 最大音频时长(秒) / Maximum audio duration in seconds
    supported_audio_mime_type: list[str] = field(
        default_factory=lambda: ["audio/mpeg", "audio/wav", "audio/mp4"]
    )  # 支持的音频MIME类型 / Supported audio MIME types
