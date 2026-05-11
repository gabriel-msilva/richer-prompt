from richer_prompt._version import get_version_dict
from richer_prompt.default_styles import inject_styles

__version__ = get_version_dict()["version"]

inject_styles()
del get_version_dict
