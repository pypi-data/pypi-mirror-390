"""
LiveKit n8n Plugin

Integrates n8n webhooks with LiveKit agents for voice AI applications.
"""

from .llm import LLM, LLMStream
from .version import __version__

__all__ = ["LLM", "LLMStream", "__version__"]

from livekit.agents import Plugin
from .log import logger


class N8nPlugin(Plugin):
    def __init__(self):
        super().__init__(__name__, __version__, __package__, logger)


Plugin.register_plugin(N8nPlugin())

# Cleanup docs of unexported modules
_module = dir()
NOT_IN_ALL = [m for m in _module if m not in __all__]

__pdoc__ = {}

for n in NOT_IN_ALL:
    __pdoc__[n] = False