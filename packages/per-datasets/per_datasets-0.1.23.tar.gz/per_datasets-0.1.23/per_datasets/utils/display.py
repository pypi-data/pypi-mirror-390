"""
Display utilities for the per_datasets module
"""

import os


def digital_screen(text: str) -> None:
    """Display text in a digital screen format"""
    os.system("cls" if os.name == "nt" else "clear")  # Clear terminal
    
    # Split text into lines
    lines = text.split('\n')
    
    # Find the longest line to determine width
    max_length = max(len(line) for line in lines) if lines else 0
    width = max(max_length + 4, 50)  # Minimum width of 50, plus padding
    
    # Print top border
    print("\033[1;42m" + " " * (width + 2) + "\033[0m")  # Green background
    
    # Print empty line for padding
    print("\033[1;42m" + " " + " " * width + " " + "\033[0m")
    
    # Print each line with left alignment and padding
    for line in lines:
        # Add left padding of 2 spaces and right padding to fill the container
        padded_line = "  " + line  # 2 spaces for left padding
        right_padding = width - len(padded_line)
        print("\033[1;42m" + " " + padded_line + " " * right_padding + " " + "\033[0m")
    
    # Print empty line for padding
    print("\033[1;42m" + " " + " " * width + " " + "\033[0m")
    
    # Print bottom border
    print("\033[1;42m" + " " * (width + 2) + "\033[0m")