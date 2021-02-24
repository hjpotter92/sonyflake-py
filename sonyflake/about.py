from typing import Dict

MAJOR: int = 1
MINOR: int = 1
PATCH: int = 0
SUFFIX: str = ""

NAME: str = "sonyflake-py"

AUTHOR: Dict[str, str] = {
    "name": "hjpotter92",
    "email": "hjpotter92+pypi@gmail.com",
}
MAINTAINER: Dict[str, str] = AUTHOR

__version__: str = f"{MAJOR}.{MINOR}.{PATCH}"

if SUFFIX:
    __version__ += SUFFIX

VERSION = __version__
