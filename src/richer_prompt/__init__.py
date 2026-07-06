from richer_prompt._version import get_version_dict
from richer_prompt.choices import Choice
from richer_prompt.prompt.multiselect import MultiSelect
from richer_prompt.prompt.select import Select
from richer_prompt.prompt.tabs import Tabs

__all__ = [
    "__version__",
    "Select",
    "MultiSelect",
    "Tabs",
    "Choice",
]

__version__ = get_version_dict()["version"]

del get_version_dict
