from typing import Callable, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from .file import JSON, PKL
    from .pc import _var

class List[_T]:
    """
    List/Tuple Wrapper

    Stores data to the local disk instead of memory
    """

    def __init__(self,
        array: 'list | tuple | Self | JSON | _var | PKL' = []
    ):
        from .file import JSON, PKL, temp
        from .pc import _var

        if isinstance(array, (JSON, _var, PKL)):
            self.var = array

        elif isinstance(array, List):
            self.var = array.var

        elif isinstance(array, (list, tuple)):
            self.var = PKL(
                temp('array', 'pkl')
            )
            self.var.save(list(array))

        self.save = self.var.save
        """Save data"""

        self.read: Callable[[], _T] = self.var.read
        """Read data"""

    def append(self, item:_T):
        self.save(
            self.read() + [item]
        )

    def remove(self, item):
        
        arr: list = self.read()

        if item in arr:
            arr.remove(item)
            self.save(arr)

    def rm_duplicates(self):
        data = self.read()
        data_ = []
        for item in data:
            if item not in data_:
                data_.append(item)
        self.save(data_)

    def __iter__(self):
        self._data:list = self.read()
        return self

    def __next__(self) -> _T:
        if len(self._data) == 0:
            raise StopIteration
        else:
            value = self._data[0]
            self._data = self._data[1:]
            return value

    def __len__(self):
        return len(self.read())
    
    def __getitem__(self, key) -> _T:
        return self.read()[key]

    def __setitem__(self, key, value):
        data = self.read()
        data[key] = value
        self.save(data)

    def __delitem__(self, key):
        self.remove(self.read()[key])

    def __iadd__(self, value):
        self.append(value)
        return self

    def __isub__(self, value):

        if isinstance(value, (list, tuple)):
            for item in value:
                self.remove(item)
        else:
            self.remove(value)

        return self

    def __contains__(self, value):
        return value in self.read()

    def sorted(self, func:Callable[[_T], Self]=lambda x: x) -> 'List[_T]':
        data = sort(self.read(), func)
        return List(data)

    def sort(self, func:Callable[[_T], Self]=lambda x: x) -> None:
        self.save( self.sorted(func).read() )

    def max(self, func:Callable[[_T], Self]=lambda x: x) -> None | _T:
        if len(self) > 0:
            return max(self.read(), func)
    
    def filtered(self, func:Callable[[_T], Self]=lambda x: x) -> 'List[_T]':
        data = filter(self.read(), func)
        return List(data)
    
    def filter(self, func:Callable[[_T], Self]=lambda x: x) -> None:
        self.save( filter(self.read(), func) )

    def random(self, n:int=1) -> 'List[_T]':
        data = random.sample(self.read(), n)
        return List(data)

    def shuffle(self) -> None:
        self.save(self.shuffled().read())
    
    def shuffled(self) -> 'List[_T]':
        return self.random(len(self.read()))

    def __str__(self):
        from json import dumps

        return dumps(self.read(), indent=2)

l: List[str] = List() 

l.read()

def stringify(array:list) -> list[str]:

    array = array.copy()

    for x, item in enumerate(array):
        array[x] = str(item)

    return array

def intify(array:list) -> list[int]:

    array = array.copy()

    for x, item in enumerate(array):
        array[x] = str(item)

    return array

def auto_convert(array:list):
    from .text import auto_convert

    array = array.copy()

    for x, a in enumerate(array):
        array[x] = auto_convert(a)

    return array

def generate(generator):
    return [x for x in generator]

def priority(
    _1: int,
    _2: int,
    reverse: bool = False
):  
    
    if _1 is None:
        _1 = 0

    if _2 is None:
        _2 = 0

    p = _1 + (_2 / (1000**1000))
    
    if reverse:
        p *= -1

    return p

class random:

    def sample[T](
        array: list[T],
        n: int = 1
    ):
        from random import sample

        if len(array) == 0:
            return None
        elif n > len(array):
            n = len(array)

        return sample(array, n)

    def choice[T](
        array: list[T]    
    ):
        from random import choice

        if len(array) > 0:
            return choice(array)

def filter[T](
    array: list[T],
    func: Callable[[T], bool] = lambda x: x
):
    from builtins import filter

    return list(filter(func, array))

def sort[T](
    array: list[T],
    func: Callable[[T], int|float] = lambda x: x
):
    return sorted(array, key=func)

def max[T](
    array: list[T],
    func: Callable[[T], int|float] = lambda x: x
):
    if len(array) > 0:
        return sort(
            array = array,
            func = func
        )[0]

def rm_duplicates[T](
    array: list[T]
):
    array1 = array.copy()
    array2 = []

    for x, value in enumerate(array1):
        
        if value in array2:
            del array1[x]
        
        else:
            array2 += [value]

    return array1

def value_in_common(
    array1: list,
    array2: list
) -> bool:
    
    for v in array1:
        if v in array2:
            return True
    
    return False
