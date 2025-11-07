from typing import TYPE_CHECKING, Self
from json import load, loads, dump, dumps

if TYPE_CHECKING:
    from .file import JSON, PKL
    from .pc import _var

def valid(value:str):
    """
    Check if a string contains valid json data
    """
    from json import decoder

    try:
        loads(value)
        return True
    except decoder.JSONDecodeError:
        return False

class Dict:
    """
    Dict/Json Wrapper

    Stores data to the local disk instead of memory
    """

    def __init__(self,
        table: 'dict | Self | JSON | _var | PKL' = {}
    ):
        from .file import JSON, PKL, temp
        from .pc import _var

        if isinstance(table, (JSON, _var, PKL)):
            self.var = table

        elif isinstance(table, Dict):
            self.var = table.var

        elif isinstance(table, dict):
            self.var = JSON(
                path = temp('table', 'json'),
                default = table,
                encode = True
            )

        self.save = self.var.save
        """Save data"""

        self.read = self.var.read
        """Read Data"""

        super().__init__()

    def remove(self, item):
        arr = self.read()
        del arr[item]
        self.save(arr)

    def names(self):
        return list(self.read())

    def values(self):
        data = self.read()
        return [data[x] for x in self.names()]

    def inverted(self):
        data = self.read()
        data_ = {}
        for x in data:
            data_[data[x]] = x
        return Dict(data_)

    def __iter__(self):
        self._names:list = self.names()
        self._values:list = self.values()
        self.x = 0
        return self

    def __next__(self):
        if self.x == len(self._names):
            raise StopIteration
        else:
            name = self._names[self.x]
            value = self._values[self.x]
            self.x += 1
            return name, value

    def __len__(self):
        return len(self.names())
    
    def __getitem__(self, key):
        try:
            return self.read()[key]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        data = self.read()
        data[key] = value
        self.save(data)

    def __delitem__(self, key):
        self.remove(self.read()[key])

    def __contains__(self, value):
        return (value in self.names()) or (value in self.values())
    
    def __iadd__(self, dict):
        data = self.read()
        for name in dict:
            data[name] = dict[name]
        self.save(data)
        return self

    def filtered(self, func=lambda x: x): #TODO
        data = filter(self.read(), func)
        return Dict(data)
    
    def filter(self, func=lambda x: x): #TODO
        self.save( filter(self.read(), func) )
        return self

    def __str__(self):
        return dumps(self.read(), indent=2)
