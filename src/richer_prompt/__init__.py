from richer_prompt._version import get_version_dict
from richer_prompt.default_styles import inject_styles
from richer_prompt.options import Option
from richer_prompt.prompt.multiselect import MultiSelect
from richer_prompt.prompt.select import Select
from richer_prompt.prompt.tabs import Tabs

__all__ = [
    "__version__",
    "Select",
    "MultiSelect",
    "Tabs",
    "Option",
]

__version__ = get_version_dict()["version"]


inject_styles()
del get_version_dict, inject_styles
