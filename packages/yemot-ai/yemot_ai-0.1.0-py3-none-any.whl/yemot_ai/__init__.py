"""
yemot-ai: חבילת Python לחיבור סוכני AI למערכות ימות המשיח

חבילה זו מספקת שכבת אינטגרציה בין yemot-flow לבין סוכני AI,
ומאפשרת לנהל שיחות רציפות עם AI דרך מערכת IVR של ימות המשיח.
"""

__version__ = "0.1.0"
__author__ = "Heskishar F."
__email__ = "heskisharf@gmail.com"

from .core import YemotAI as AI
from .session_store import SessionStore, MemorySessionStore, JSONSessionStore
from .providers import AIProvider, CodexCLIProvider, MockAIProvider

__all__ = [
    "AI",
    "YemotAI",  # שמירה על תאימות לאחור
    "SessionStore", 
    "MemorySessionStore",
    "JSONSessionStore",
    "AIProvider",
    "CodexCLIProvider",
    "MockAIProvider",
]

# שמירה על תאימות לאחור
YemotAI = AI