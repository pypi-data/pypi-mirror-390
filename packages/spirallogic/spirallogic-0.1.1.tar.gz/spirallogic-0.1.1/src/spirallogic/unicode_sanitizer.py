#!/usr/bin/env python3
"""
Unicode sanitizer for Windows terminal compatibility
Strips problematic Unicode characters that cause encoding errors
"""

import re

def sanitize_for_windows_terminal(text):
    """
    Sanitize text for Windows terminal output by removing/replacing problematic Unicode
    
    Args:
        text: Input text that may contain Unicode characters
        
    Returns:
        Sanitized text safe for Windows console output
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Replace common emoji with text equivalents
    emoji_replacements = {
        '🔮': '[CRYSTAL]',
        '✨': '[SPARKLE]',
        '🚨': '[CRISIS]',
        '✅': '[CHECK]',
        '❌': '[X]',
        '🆔': '[ID]',
        '🗣️': '[VOICE]',
        '🎯': '[TARGET]',
        '📋': '[CLIPBOARD]',
        '📄': '[PAGE]',
        '👤': '[USER]',
        '📝': '[NOTE]',
        '🔗': '[LINK]',
        '💾': '[SAVE]',
        '📊': '[CHART]',
        '⚠️': '[WARNING]',
        '🍳': '[COOK]',
        '🔥': '[FIRE]',
        '💀': '[SKULL]',
        '😂': '[LAUGH]',
        '🌅': '[SUNRISE]',
    }
    
    # Apply replacements
    for emoji, replacement in emoji_replacements.items():
        text = text.replace(emoji, replacement)
    
    # Remove any remaining non-ASCII characters that might cause issues
    # Keep basic punctuation and accented characters
    text = re.sub(r'[^\x20-\x7E\u00A0-\u024F]', '?', text)
    
    return text