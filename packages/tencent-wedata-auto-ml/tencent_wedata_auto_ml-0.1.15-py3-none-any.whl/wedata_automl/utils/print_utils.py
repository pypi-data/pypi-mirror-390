"""
Print utilities for better visibility in Notebook environments.
"""
from datetime import datetime
from typing import Any


def safe_print(msg: str, level: str = "INFO", **kwargs: Any) -> None:
    """
    Print with timestamp and level indicator, safe for Notebook environments.
    
    Args:
        msg: Message to print
        level: Log level (INFO, WARNING, ERROR, SUCCESS, DEBUG)
        **kwargs: Additional arguments passed to print()
    
    Examples:
        safe_print("Training started", level="INFO")
        safe_print("Model registered successfully", level="SUCCESS")
        safe_print("Registration failed", level="ERROR")
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Level indicators with emojis for better visibility
    level_indicators = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️ ",
        "DEBUG": "🔍",
        "START": "🚀",
        "COMPLETE": "🎉",
    }
    
    indicator = level_indicators.get(level.upper(), "  ")
    formatted_msg = f"[{timestamp}] {indicator} {msg}"
    
    print(formatted_msg, **kwargs)


def print_section(title: str, width: int = 80) -> None:
    """
    Print a section header with separator lines.
    
    Args:
        title: Section title
        width: Width of the separator line
    
    Examples:
        print_section("Model Registration")
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] {'='*width}")
    print(f"[{timestamp}] {title}")
    print(f"[{timestamp}] {'='*width}")


def print_dict(data: dict, indent: int = 2) -> None:
    """
    Print a dictionary in a readable format with timestamp.
    
    Args:
        data: Dictionary to print
        indent: Indentation spaces
    
    Examples:
        print_dict({"model": "lgbm", "accuracy": 0.95})
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    indent_str = " " * indent
    for key, value in data.items():
        print(f"[{timestamp}] {indent_str}{key}: {value}")

