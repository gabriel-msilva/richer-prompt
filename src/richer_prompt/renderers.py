from typing import Final, Protocol

from rich.console import Group, RenderableType
from rich.style import Style
from rich.text import Text, TextType

from richer_prompt.models import (
    MultiSelectionModel,
    SelectionModel,
    SingleSelectionModel,
)

LEFT_POINTER: Final = "❮"
RIGHT_POINTER: Final = "❯"

LEFT_ARROW: Final = "←"
RIGHT_ARROW: Final = "→"
UP_ARROW: Final = "↑"
DOWN_ARROW: Final = "↓"

BULLET: Final = "•"
MIDDLE_DOT: Final = "·"

BALLOT_BOX: Final = "☐"
BALLOT_BOX_WITH_CHECK: Final = "☑"
BALLOT_BOX_WITH_X: Final = "☒"

CHECK_MARK: Final = "✓"
BALLOT_X: Final = "✗"


class Renderer(Protocol):
    def render(self, model: SelectionModel) -> RenderableType: ...

    def get_answer(self, model: SelectionModel) -> Text: ...


class SingleSelectRenderer:
    def __init__(
        self,
        message: TextType,
        *,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool = True,
        show_hint: bool = True,
    ):
        self.message = ensure_text(message, default_style="richer_prompt.title")
        self.cursor_pointer = cursor_pointer
        self.numbered = numbered
        self.show_hint = show_hint

    def render(self, model: SingleSelectionModel) -> Group:
        rows: list[Text] = []

        message = self.message.copy().append(":")
        rows.append(message)
        rows.append(Text())

        max_number_length = len(str(len(model.options)))

        for i, option in enumerate(model.options):
            is_focused = i == model.cursor

            cursor = (
                Text(self.cursor_pointer, style="richer_prompt.cursor")
                if is_focused
                else Text(" " * len(self.cursor_pointer))
            )

            number = (
                Text(
                    f"{i + 1}. ".rjust(max_number_length + 2),
                    style="richer_prompt.description",
                )
                if self.numbered
                else Text()
            )

            label = Text(
                option.display,
                style="richer_prompt.cursor" if is_focused else "richer_prompt.option",
            )

            row = Text.assemble(cursor, " ", number, label)
            if option.description:
                row.append("  ")
                row.append(option.description, style="richer_prompt.description")

            rows.append(row)

        if self.show_hint:
            rows.append(Text())
            rows.append(
                format_hint(
                    f"{UP_ARROW}{DOWN_ARROW} to navigate",
                    "Enter to select",
                )
            )

        return Group(*rows)

    def get_answer(self, model: SingleSelectionModel) -> Text:
        return (
            self.message.copy()
            .append(": ")
            .append(model.current.display, style="richer_prompt.cursor")
        )


class MultiSelectRenderer:
    def __init__(
        self,
        message: TextType,
        *,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool = True,
        show_hint: bool = True,
    ):
        self.message = ensure_text(message, default_style="richer_prompt.title")
        self.cursor_pointer = cursor_pointer
        self.numbered = numbered
        self.show_hint = show_hint

    def render(self, model: MultiSelectionModel) -> Group:
        rows: list[Text] = []

        message = self.message.copy().append(":")
        rows.append(message)
        rows.append(Text())

        max_number_length = len(str(len(model.options)))

        for i, option in enumerate(model.options):
            is_focused = i == model.cursor
            is_selected = i in model.selected

            cursor = (
                Text(self.cursor_pointer, style="richer_prompt.cursor")
                if is_focused
                else Text(" " * len(self.cursor_pointer))
            )

            number = (
                Text(
                    f"{i + 1}. ".rjust(max_number_length + 2),
                    style="richer_prompt.description",
                )
                if self.numbered
                else Text()
            )

            checkbox = (
                Text(f"[{CHECK_MARK}]", style="richer_prompt.checkbox.checked")
                if is_selected
                else Text("[ ]", style="richer_prompt.checkbox")
            )

            label = Text(
                option.display,
                style="richer_prompt.cursor" if is_focused else "richer_prompt.option",
            )

            row = Text.assemble(cursor, " ", number, checkbox, " ", label)

            if option.description:
                row.append("  ")
                row.append(option.description, style="richer_prompt.description")

            rows.append(row)

        submit_cursor = (
            Text(self.cursor_pointer, style="richer_prompt.cursor")
            if model.is_on_submit()
            else Text(" " * len(self.cursor_pointer))
        )
        submit_label = Text(
            "Submit",
            style="richer_prompt.cursor"
            if model.is_on_submit()
            else "richer_prompt.option",
        )
        padding = " " * (max_number_length + 2) if self.numbered else ""

        rows.append(Text.assemble(submit_cursor, " ", padding, submit_label))

        if self.show_hint:
            rows.append(Text())
            rows.append(
                format_hint(
                    f"{UP_ARROW}{DOWN_ARROW} to navigate",
                    "Enter to select",
                    "Submit to finish",
                )
            )

        return Group(*rows)

    def get_answer(self, model: MultiSelectionModel) -> Text:
        message = self.message.copy().append(": ")

        values = ", ".join(x.display for x in model.selected_values)
        if values:
            return message.append(values, style="richer_prompt.cursor")

        return message.append("(none)", style="richer_prompt.description")


class TabsRenderer:
    def __init__(self, message: TextType):
        self.message = ensure_text(message, default_style="richer_prompt.title")

    def render(self, model: SingleSelectionModel) -> Group:
        rows: list[Text] = []

        message = self.message.copy().append(":")
        rows.append(message)
        rows.append(Text())

        tabs = Text()

        tabs.append(LEFT_ARROW, style="dim" if model.cursor == 0 else "")
        tabs.append(" ")

        for i, option in enumerate(model.options):
            if i > 0:
                tabs.append(" ")

            is_focused = i == model.cursor

            tabs.append(
                f" {option.display} ",
                style="richer_prompt.tab.active" if is_focused else "richer_prompt.tab",
            )

        tabs.append(" ")
        tabs.append(
            RIGHT_ARROW,
            style="dim" if model.cursor == len(model.options) - 1 else "",
        )

        rows.append(tabs)
        rows.append(Text(model.current.description, style="richer_prompt.description"))

        return Group(*rows)

    def get_answer(self, model: SingleSelectionModel) -> Text:
        return (
            self.message.copy()
            .append(": ")
            .append(model.current.display, style="richer_prompt.cursor")
        )


def ensure_text(value: TextType, default_style: str | Style = "") -> Text:
    return (
        value
        if isinstance(value, Text)
        else Text.from_markup(value, style=default_style)
    )


def format_hint(*parts: str) -> Text:
    return Text(f" {MIDDLE_DOT} ".join(parts), style="richer_prompt.hint")
