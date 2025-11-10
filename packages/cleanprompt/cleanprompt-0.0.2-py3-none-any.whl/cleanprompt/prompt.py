"""Functions to cleanup prompts before sending them an LLM model."""

import textwrap
from typing import Literal

# Define the type for the mode
StripMode = Literal["both", "leading", "trailing", "none"]


def clean(input_prompt: str, strip_mode: StripMode = "both") -> str:
    """Cleans a raw prompt string by dedenting and optionally stripping whitespace.

    Args:
        input_prompt (str): The raw prompt string to be cleaned.
        strip_mode (Literal["both", "leading", "trailing", "none"]): The mode for stripping whitespace.
            - "both": Strip whitespace from both ends (default).
            - "leading": Strip whitespace from the beginning only.
            - "trailing": Strip whitespace from the end only.
            - "none": Do not strip any whitespace.

    Returns:
        str: The cleaned prompt string.

    Raises:
        ValueError: If an invalid strip_mode is provided.
    """
    dedented = textwrap.dedent(input_prompt)

    match strip_mode:
        case "both":
            return dedented.strip()
        case "leading":
            return dedented.lstrip()
        case "trailing":
            return dedented.rstrip()
        case "none":
            return dedented

    raise ValueError(f"Invalid strip_mode: {strip_mode}")


# Alias for stripping 'leading' only (e.g., few-shot prompts)
def clean_leading(input_prompt: str) -> str:
    """Cleans a raw prompt string by dedenting and stripping leading whitespace only.

    Args:
        input_prompt (str): The raw prompt string to be cleaned.

    Returns:
        str: The cleaned prompt string.
    """
    return clean(input_prompt, strip_mode="leading")


# Alias for stripping 'trailing' only (e.g., system prompts)
def clean_trailing(input_prompt: str) -> str:
    """Cleans a raw prompt string by dedenting and stripping trailing whitespace only.

    Args:
        input_prompt (str): The raw prompt string to be cleaned.

    Returns:
        str: The cleaned prompt string.
    """
    return clean(input_prompt, strip_mode="trailing")


# Alias for 'none' (just dedent)
def clean_nostrip(input_prompt: str) -> str:
    """Cleans a raw prompt string by dedenting without stripping any whitespace.

    Args:
        input_prompt (str): The raw prompt string to be cleaned.

    Returns:
        str: The cleaned prompt string.
    """
    return clean(input_prompt, strip_mode="none")
