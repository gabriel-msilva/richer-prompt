from rich.style import Style

RICHER_PROMPT_STYLES: dict[str, Style] = {
    "richer_prompt.title": Style(bold=True),
    "richer_prompt.description": Style(dim=True),
    "richer_prompt.hint": Style(dim=True),
    "richer_prompt.choice": Style.null(),
    "richer_prompt.choice.description": Style(dim=True),
    "richer_prompt.cursor": Style(color="light_steel_blue"),
    "richer_prompt.cursor.submit": Style(bold=True),
    "richer_prompt.checkbox": Style.null(),
    "richer_prompt.checkbox.checked": Style(color="green"),
    "richer_prompt.tab": Style.null(),
    "richer_prompt.tab.active": Style(color="light_steel_blue", reverse=True),
}


def inject_styles() -> None:
    from rich import themes
    from rich.default_styles import DEFAULT_STYLES

    for name, style in RICHER_PROMPT_STYLES.items():
        themes.DEFAULT.styles.setdefault(name, style)
        DEFAULT_STYLES.setdefault(name, style)
