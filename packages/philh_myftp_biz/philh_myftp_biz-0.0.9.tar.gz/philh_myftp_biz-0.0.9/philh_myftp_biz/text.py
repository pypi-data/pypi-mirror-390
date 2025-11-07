
def split(value:str, sep:str=None) -> list[str]:
    """
    Automatic String Splitter

    If sep is None, then shlex.split is used.
    If sep is defined, then str.split is used
    """
    import shlex
    
    if sep:
        return value.split(str(sep))
    else:
        return shlex.split(value)

def int_stripper(string:str) -> int:
    """
    Remove all non-numerical characters from an alphanumeric string
    """
    from .num import valid

    for char in string:
        if not valid.int(char):
            string = string.replace(char, '')

    return int(string)

def trimbychar(string:str, x:int, char:str):
    for _ in range(0, x):
        string = string[:string.rfind(char)]
    return string

class contains:
    """
    Functions to check if text contains value(s) with list as input
    """

    def any (
        string: str,
        values: list[str]
    ) -> bool:
        """
        Check if string contains any of the values
        """
        for v in values:
            if v in string:
                return True
        return False
    
    def all (
        string: str,
        values: list[str]
    ) -> bool:
        """
        Check if string contains all of the values
        """

        for v in values:
            if v not in string:
                return False
        return True

def auto_convert(string:str) -> int | float | bool | dict | str:
    """
    Automatically convert string

    Input Types:
        - int
        - float
        - bool
        - hex (dill)
        - dict
        - str
    """

    from . import num, json

    if num.valid.int(string):
        return int(string)
    
    elif num.valid.float(string):
        return float(string)
    
    elif string.lower() in ['true', 'false']:
        return bool(string)
    
    elif hex.valid(string):
        return hex.decode(string)
    
    elif json.valid(string):
        return json.loads(string)
 
    else:
        return string

def rm(string:str, *values:str):
    """
    Remove all values from a string
    """
    for value in values:
        string = string.replace(value, '')
    return string

class hex:
    """
    Wrapper for hexadecimal via dill
    """

    def valid(string:str) -> bool:
        """
        Check if string is a valid dill hexadecimal dump
        """

        try:
            hex.decode(string)
            return True
        except (EOFError, ValueError):
            return False

    def decode(value:str):
        """
        Convert hexadecimal string back into original value

        Trims input by ';' before processing
        Ex: 'abc;defg;hij' -> 'defg'

        """
        from dill import loads

        if ';' in value:
            value = value.split(';')[1]

        return loads(bytes.fromhex(value))

    def encode(value) -> str:
        """
        Convert any pickleable object into a string
        """
        from dill import dumps
        
        return dumps(value).hex()

def random(length:int) -> str:
    """
    Get a string with random characters

    Ex: random(6) -> 'JAIOEN'
    """
    from random import choices
    from string import ascii_uppercase, digits

    return ''.join(choices(
        population = ascii_uppercase + digits,
        k = length
    ))

def starts_with_any (
    text: str,
    values: list[str]
) -> bool:
    """
    Check if string starts with any of values
    """
    return True in [text.startswith(v) for v in values]

def ends_with_any (
    text: str,
    values: list[str]
) -> bool:
    """
    Check if string ends with any of values
    """

    return True in [text.endswith(v) for v in values]

def rm_emojis(
    text: str,
    sub: str = ''
):
    """
    Remove all emojis from a string
    """
    from re import compile, UNICODE

    regex = compile(
        "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags = UNICODE
    )

    return regex.sub(
        repl = sub.encode('unicode_escape').decode(),
        string = text.encode('utf-8').decode()
    )

