import ast
import contextlib
import io
from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from rich import errors
from rich.console import Console, RenderableType
from rich.theme import Theme

from richer_prompt import Choice, Form, MultiSelect, Select, Tabs
from richer_prompt.default_styles import RICHER_PROMPT_STYLES

CONSOLE_WIDTH = 79


class SnapshotDirective(Directive):
    has_content = True
    option_spec = {"title": directives.unchanged, "hide-code": directives.flag}

    def run(self) -> list[nodes.Node]:
        expression = "\n".join(self.content).strip()
        if not expression:
            raise self.error("snapshot directive requires content")

        prompt, index, default = parse_prompt_expression(expression)
        renderable = render_initial_prompt(prompt, index=index, default=default)

        svg = render_svg(
            renderable,
            title=self.options.get("title") or f"{prompt.__class__.__name__.lower()}",
            console=getattr(prompt, "console", None),
        )

        output: list[nodes.Node] = []

        if "hide-code" not in self.options:
            code_lines = [".. code-block:: python", ""]
            code_lines.extend(f"   {line}" for line in expression.splitlines())

            code_container = nodes.container()
            self.state.nested_parse(
                StringList(code_lines),
                self.content_offset,
                code_container,
            )
            output.extend(code_container.children)

        output.append(nodes.raw("", svg, format="html"))

        return output


def parse_prompt_expression(expression: str) -> tuple[Any, int, set[int] | None]:
    tree = ast.parse(expression, mode="exec")
    if not tree.body:
        raise ValueError("snapshot directive requires content")

    namespace = {
        "Select": Select,
        "MultiSelect": MultiSelect,
        "Tabs": Tabs,
        "Form": Form,
        "Choice": Choice,
    }

    setup_statements = tree.body[:-1]
    if setup_statements:
        setup_module = ast.Module(body=setup_statements, type_ignores=[])
        setup_module = ast.fix_missing_locations(setup_module)

        exec(compile(setup_module, "<snapshot>", "exec"), namespace, namespace)

    final_statement = tree.body[-1]
    if not isinstance(final_statement, ast.Expr):
        raise ValueError(
            "snapshot expects the last statement to be a prompt expression"
        )

    final_expr = final_statement.value
    if isinstance(final_expr, ast.Call):
        return _evaluate_prompt_call(final_expr, namespace)

    prompt = _safe_eval(final_expr, namespace)

    return prompt, 0, None


def _evaluate_prompt_call(
    call: ast.Call, namespace: dict[str, Any]
) -> tuple[Any, int, set[int] | None]:
    namespace = dict(namespace)
    index = 0
    default: set[int] | None = None

    if isinstance(call.func, ast.Attribute) and call.func.attr == "ask":
        for keyword in call.keywords:
            if keyword.arg == "index":
                index = int(_safe_eval(keyword.value, namespace))
            elif keyword.arg == "default":
                default_value = _safe_eval(keyword.value, namespace)
                default = None if default_value is None else set(default_value)

        ctor_call = ast.Call(
            func=call.func.value,
            args=call.args,
            keywords=[kw for kw in call.keywords if kw.arg not in {"index", "default"}],
        )
        ctor_call = ast.fix_missing_locations(ast.copy_location(ctor_call, call))
        prompt = _safe_eval(ctor_call, namespace)
    else:
        prompt = _safe_eval(call, namespace)

    return prompt, index, default


def _safe_eval(node, namespace: dict[str, Any]) -> Any:
    return eval(
        compile(ast.Expression(node), "<snapshot>", "eval"), namespace, namespace
    )


def render_initial_prompt(
    prompt: Any, *, index: int, default: set[int] | None
) -> RenderableType:
    if isinstance(prompt, MultiSelect):
        return prompt._build_widget(index=index, default=default).render()

    if isinstance(prompt, (Select, Tabs, Form)):
        return prompt._build_widget(index=index).render()

    raise ValueError("snapshot only supports Select, MultiSelect, and Tabs prompts")


def render_svg(
    renderable: RenderableType,
    *,
    title: str,
    console: Console | None,
) -> str:
    console = _build_snapshot_console(console)
    console.print(renderable)

    return console.export_svg(title=title)


def _build_snapshot_console(console: Console | None = None) -> Console:
    styles = dict(RICHER_PROMPT_STYLES)

    if console is not None:
        for style_name in RICHER_PROMPT_STYLES:
            with contextlib.suppress(errors.MissingStyle):
                styles[style_name] = console.get_style(style_name)

    return Console(
        file=io.StringIO(),
        record=True,
        force_terminal=True,
        color_system="truecolor",
        width=CONSOLE_WIDTH,
        theme=Theme(styles),
    )


def setup(app):
    app.add_directive("snapshot", SnapshotDirective)

    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
