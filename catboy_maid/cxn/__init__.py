"""
The main interface plugging the actual platform APIs into Catboy Maid.
Generally, each module will have two halves:

- Running clients to feed events into `..pipeline`
- Providing normalized API access to propagate actions back to platforms
"""

from . import discord
