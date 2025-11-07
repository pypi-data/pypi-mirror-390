from typing import Self

def sleep(
    s: int,
    show: bool = False
):
    """
    Wrapper for time.Sleep function

    If show is True, then '#/# seconds' will print to the console each second
    """
    from time import sleep as __sleep

    if show:
    
        print('Waiting ...')
    
        for x in range(1, s+1):
            print('{}/{} seconds'.format(x, s))
            __sleep(1)

    else:
        __sleep(s)
    
    return True

class every:
    """
    Repeat every {s} seconds

    EXAMPLE:
    for _ in every(1):
        print('1 second has passed')
    """
    
    from sys import maxsize
    def __init__(self,
        s: int,
        max_iters: int = maxsize
    ):
        self.s = s
        self.max_iters = max_iters

    def __iter__(self):
        self.x = 0
        return self
    
    def __next__(self):
        from time import sleep as __sleep

        if self.x == self.max_iters:
            raise StopIteration
        else:
            __sleep(self.s)
            return

def toHMS(stamp:int) -> str:
    """
    Convert a unix time stamp to 'hh:mm:ss'
    """

    m, s = divmod(stamp, 60)
    h, m = divmod(m, 60)
    return ':'.join([
        strDigit(h), # TODO
        strDigit(m),
        strDigit(s)
    ])

class Stopwatch:
    """
    Keeps track of time
    """

    def __init__(self):
        from time import perf_counter

        self.start_time = None
        self.end_time = None
        self.running = False
        self.now = perf_counter

    def elapsed(self) -> int:
        """
        Get the # of seconds between now or the stop time, and the start time
        """

        if self.running:
            elapsed = self.now() - self.start_time
        else:
            elapsed = self.end_time - self.start_time

        return elapsed

    def start(self) -> Self:
        """
        Start the stopwatch at 0
        """
        
        self.start_time = self.now()
        self.end_time = None
        self.running = True

        return self

    def stop(self) -> Self:
        """
        Stop the stopwatch
        """

        self.end_time = self.now()
        self.running = False
        
        return self

class from_stamp:
    """
    Handler for a unix time stamp
    """

    def __init__(self, stamp:int):
        from datetime import timezone, timedelta, datetime

        self.__dt = datetime.fromtimestamp(
            timestamp = stamp,
            tz = timezone(
                offset = timedelta(hours=-4)
            )
        )

        self.year:  int = self.__dt.year
        """Year (####)"""

        self.month: int = self.__dt.month
        """Month (1-12)"""
        
        self.day:   int = self.__dt.day
        """Day of the Month (1-31)"""
        
        self.hour:  int = self.__dt.hour
        """Hour (0-23)"""
        
        self.minute:int = self.__dt.minute
        """Minute (0-59)"""
        
        self.second:int = self.__dt.second
        """Second (0-59)"""

        self.unix:  int = stamp
        """Unix Time Stamp"""

        self.stamp = self.__dt.strftime
        """Get Formatted Time Stamp"""

def now() -> from_stamp:
    """
    Get details of the current time
    """
    from time import time

    return from_stamp(time())

def from_string(
    string: str,
    separator:str = '/',
    order:str = 'YMD'
) -> from_stamp:
    """
    Get details of time string
    """
    from datetime import datetime

    split = string.split(separator)

    order = order.lower()
    Y = split[order.index('y')]
    M = split[order.index('m')]
    D = split[order.index('d')]

    dt = datetime.strptime(f'{Y}-{M}-{D}', "%Y-%m-%d")

    return from_stamp(dt.timestamp())

def from_ymdhms(
    year:   int,
    month:  int,
    day:    int,
    hour:   int,
    minute: int,
    second: int,
) -> from_stamp:
    """
    Get details of time from year, month, day, hour, minute, & second
    """
    from datetime import datetime

    t = datetime(
        year,
        month,
        day,
        hour,
        minute,
        second
    )

    return from_stamp(t.timestamp())
