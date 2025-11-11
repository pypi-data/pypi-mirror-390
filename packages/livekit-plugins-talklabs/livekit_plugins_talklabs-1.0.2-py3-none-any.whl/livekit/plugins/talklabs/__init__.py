"""
TalkLabs TTS plugin for LiveKit Agents

High-quality Portuguese text-to-speech synthesis for LiveKit applications.
"""

from .tts import TalkLabsTTS, TalkLabsStream
from .version import __version__

__all__ = [
    "TalkLabsTTS",
    "TalkLabsStream",
    "__version__",
]

# Namespace package declaration for LiveKit plugins
__path__ = __import__("pkgutil").extend_path(__path__, __name__)