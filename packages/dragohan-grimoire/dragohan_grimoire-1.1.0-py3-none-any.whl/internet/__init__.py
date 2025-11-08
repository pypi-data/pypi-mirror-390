"""
Internet - HTTP requests that just WORK

Usage:
    from internet import *
    
    url = "https://api.example.com"
    data = get.data(url)  # Always returns JSON
"""

from .getter import get

__version__ = "0.2.0"
__all__ = ['get']
