"""
NeuroBUS - Universal Neuro-Semantic Event Bus

The cognitive communication substrate for AI systems.
"""

from neurobus.__version__ import __version__
from neurobus.core.bus import NeuroBus
from neurobus.core.event import Event
from neurobus.core.subscription import Subscription

__all__ = [
    "__version__",
    "NeuroBus",
    "Event",
    "Subscription",
]
