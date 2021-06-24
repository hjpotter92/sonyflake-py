from typing import Dict

MAJOR: int = 1
MINOR: int = 3
PATCH: int = 0
SUFFIX: str = ""

NAME: str = "sonyflake-py"

AUTHOR: Dict[str, str] = {
    "name": "hjpotter92",
    "email": f"{NAME}@pypi.hjpotter92.email",
}
MAINTAINER: Dict[str, str] = AUTHOR

__version__: str = f"{MAJOR}.{MINOR}.{PATCH}"

if SUFFIX:
    __version__ += f"-{SUFFIX}"

VERSION = __version__
