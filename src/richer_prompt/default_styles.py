from rich import errors
from rich.console import Console
from rich.style import Style

RICHER_PROMPT_STYLES: dict[str, Style] = {
    "richer_prompt.title": Style(bold=True),
    "richer_prompt.description": Style(dim=True),
    "richer_prompt.hint": Style(dim=True),
    "richer_prompt.choice": Style.null(),
    "richer_prompt.cursor": Style(color="magenta"),
    "richer_prompt.checkbox": Style.null(),
    "richer_prompt.checkbox.checked": Style(color="green"),
    "richer_prompt.tab": Style.null(),
    "richer_prompt.tab.active": Style(color="magenta", reverse=True),
}


def missing_styles(console: Console) -> dict[str, Style]:
    """Default styles for style names not defined by the console's theme."""
    missing = {}

    for name, style in RICHER_PROMPT_STYLES.items():
        try:
            console.get_style(name)
        except errors.MissingStyle:
            missing[name] = style

    return missing
