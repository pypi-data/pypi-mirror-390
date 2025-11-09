from typing import Union, Dict, TypedDict

ArgType = Union["Argument", "Operand", "Flag", None]

class ArgDict(TypedDict):
    args: Dict[str, ArgType]
    kwargs: Dict[str, ArgType]