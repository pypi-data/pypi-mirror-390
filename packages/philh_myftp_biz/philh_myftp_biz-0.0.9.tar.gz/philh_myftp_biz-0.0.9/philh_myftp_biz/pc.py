from typing import Literal, Self, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from .db import colors
    from psutil import Process

def NAME() -> str:
    """
    Get the hostname of the local computer
    """
    from socket import gethostname

    hn = gethostname()
    
    return hn

def SERVER_LAN() -> bool:
    """
    Check if the local computer is on the same lan as 'PC-1 [192.168.1.2]' 
    """
    from .web import ping

    p = ping('192.168.1.2')

    return p

def OS() -> Literal['windows', 'unix']:
    """
    Get the Operating System type (windows/unix)
    """
    from os import name

    return {
        True: 'windows',
        False: 'unix'
    } [name == 'nt']

class Path:
    """
    File/Folder
    """

    def __init__(self, *input):
        from pathlib import Path as libPath, PurePath
        from os import path

        # ==================================

        if len(input) > 1:
            joined: str = path.join(*input)
            self.path = joined.replace('\\', '/')

        elif isinstance(input[0], Path):
            self.path = input[0].path

        elif isinstance(input[0], str):
            self.path = libPath(input[0]).absolute().as_posix()

        elif isinstance(input[0], PurePath):
            self.path = input[0].as_posix()

        elif isinstance(input[0], libPath):
            self.path = input[0].as_posix()

        # ==================================

        # Declare path string
        self.path: str = self.path.replace('\\', '/')
        """File Path with forward slashes"""

        # Declare 'pathlib.Path' attribute
        self.__Path = libPath(self.path)

        # Link 'exists', 'isfile', & 'isdir' functions from 'self.__Path'
        self.exists = self.__Path.exists
        """Check if path exists"""

        self.isfile = self.__Path.is_file
        """Check if path is a file"""
        
        self.isdir = self.__Path.is_dir
        """Check if path is a folder"""

        # Declare 'set_access'
        self.set_access = _set_access(self)
        """Filesystem Access"""

        # Declare 'mtime'
        self.mtime = _mtime(self)
        """Modified Time"""

        # ==================================

        # Add trailing '/'
        if (not self.path.endswith('/')) and self.isdir():
            self.path += '/'

        # ==================================

    def cd(self) -> '_cd':
        """
        Change the working directory to path
        
        If path is a file, then it will change to the file's parent directory
        """
        if self.isfile():
            return _cd(self.parent().path)
        else:
            return _cd(self.path)
    
    def resolute(self) -> Self:
        """
        Get path with Symbolic Links Resolved
        """
        return Path(self.__Path.resolve(True))
    
    def child(self, *name:str) -> Self:
        """
        Get child of path
        
        Note: Will raise TypeError if path is a file
        """

        if self.isfile():
            raise TypeError("Parent path cannot be a file")
        
        elif len(name) > 1:
            return Path(self.path + '/'.join(name))
        
        elif name[0].startswith('/'):
            return Path(self.path + name[0][1:])
            
        else:
            return Path(self.path + name[0])

    def __str__(self) -> str:
        return self.path

    def __eq__(self, other) -> bool:

        if isinstance(other, Path):
            return (self.path == other.path)
        else:
            return False

    def islink(self) -> bool:
        """
        Check if path is Symbolic Link or Directory Junction
        """

        return (self.__Path.is_symlink() or self.__Path.is_junction())

    def size(self) -> int:
        """
        Get File Size

        Note: Will return TypeError is path is folder
        """
        from os import path

        if self.isfile():
            return path.getsize(self.path)
        else:
            raise TypeError("Cannot get size of a folder")

    def children(self) -> Generator[Self]:
        """
        Get children of current directory

        Curdir - |
                 | - Child
                 |
                 | - Child
        """
        for p in self.__Path.iterdir():
            yield Path(p)

    def descendants(self) -> Generator[Self]:
        """
        Get descendants of current directory

        Curdir - |           | - Descendant
                 | - Child - |
                 |           |
                 |           | - Descendant
                 |
                 | - Child - |
                             | - Descendant
        """
        for root, dirs, files in self.__Path.walk():
            for item in (dirs + files):
                yield Path(root, item)

    def parent(self) -> Self:
        """
        Get parent of current path
        """
        return Path(self.__Path.parent)

    def var(self, name:str, default=None) -> '_var':
        """
        Get Variable Object for storing custom metadata
        """
        return _var(self, name, default)
    
    def sibling(self, item) -> Self:
        """
        Get sibling of current path

        CurPath - |
                  |
        Sibling - |
                  |
        """
        return self.parent().child(item)
    
    def ext(self) -> str:
        """
        Get file extension of path
        """
        from os import path

        ext = path.splitext(self.path)[1][1:]
        if len(ext) > 0:
            return ext.lower()

    def type(self) -> str:
        """
        Get mime type of path
        """
        from .db import mime_types

        types = mime_types

        if self.isdir():
            return 'dir'

        elif self.ext() in types:
            return types[self.ext()]

    def delete(self) -> None:
        """
        Delete the current path

        Uses the 'send2trash' package.
        Will use 'os.remove' if send2trash raises an OSError.
        """
        from send2trash import send2trash
        from shutil import rmtree
        from os import remove

        if self.exists():
            
            self.set_access.full()

            try:
                send2trash(self.path)

            except OSError:

                if self.isdir():
                    rmtree(self.path)
                else:
                    remove(self.path)

    def rename(self, dst, overwrite:bool=True) -> None:
        """
        Change the name of the current path
        """
        from os import rename

        src = self
        dst = Path(dst)

        if dst.ext() is None:
            dst.chext(self.ext())
        
        with src.cd():
            try:
                rename(src.path, dst.path)
            except FileExistsError as e:
                if overwrite:
                    dst.delete()
                    rename(src, dst)
                else:
                    raise e

    def name(self) -> str:
        """
        Get the name of the current path

        Ex: 'C:/example.txt' -> 'example' 
        """

        name = self.__Path.name

        # Check if file has ext
        if self.ext():
            # Return name without ext
            return name[:name.rfind('.')]

        else:
            # Return filename
            return name

    def seg(self, i:int=-1) -> str:
        """
        Returns segment of path split by '/'

        Ex: Path('C:/example/test.log').seg(-1) -> 'test.log'
        """
        return self.path.split('/') [i]

    def copy(
        self,
        dst: 'Path'
    ) -> None:
        """
        Copy the path to another location
        """
        from shutil import copyfile, copytree

        try:
            
            mkdir(dst.parent())

            if self.isfile():

                if dst.isdir():
                    dst = dst.child(self.seg())

                if dst.exists():
                    dst.delete()

                copyfile(
                    src = self.path, 
                    dst = dst.path
                )

            else:
                copytree(
                    src = self.path,
                    dst = dst.path,
                    dirs_exist_ok = True
                )

        except Exception as e:
            print('Undoing ...')
            dst.delete()
            raise e

    def move(self, dst) -> None:
        """
        Move the path to another location
        """
        self.copy(dst)
        self.delete()

    def inuse(self) -> bool:
        """
        Check if path is in use by another process
        """
        from os import rename

        if self.exists():
            try:
                rename(self.path, self.path)
                return False
            except PermissionError:
                return True
        else:
            return False

    def open(self, mode='r'):
        """
        Open the current file

        Works the same as: open(self.Path)
        """
        return open(self.path, mode)

def cwd() -> Path:
    """
    Get the Current Working Directory
    """
    from os import getcwd

    return Path(getcwd())

def pause():
    """
    Pause the execution and wait for user input
    """
    from os import system

    if OS() == 'windows':
        system('pause')
    else:
        pass # TODO

class _cd:
    """
    Advanced Options for Change Directory
    """

    def __enter__(self):
        self.__via_with = True

    def __exit__(self, *_):
        if self.__via_with:
            self.back()

    def __init__(self, path:'Path'):
        
        self.__via_with = False

        self.__target = path

        self.open()

    def open(self) -> None:
        """
        Change CWD to the given path

        Saves CWD for easy return with cd.back()
        """
        from os import getcwd, chdir

        self.__back = getcwd()

        chdir(self.__target.path)

    def back(self) -> None:
        """
        Change CWD to the previous path
        """
        from os import chdir
        
        chdir(self.__back)

class terminal:
    """
    Misc. Functions for the Terminal/Console
    """
    
    def width() -> int:
        """
        Get the # of columns in the terminal
        """
        from shutil import get_terminal_size
        return get_terminal_size().columns

    def write(
        text,
        stream: Literal['out', 'err'] = 'out',
        flush: bool = True
    ) -> None:
        """
        Write text to the sys.stdout or sys.stderr buffer
        """
        from io import StringIO
        import sys
        
        stream: StringIO = getattr(sys, 'std'+stream)
        
        stream.write(text)
    
        if flush:
            stream.flush()

    def del_last_line() -> None:
        """
        Clear the previous line in the terminal
        """
        spaces = (' ' * terminal.width())
        print("\033[A{}\033[A".format(spaces), end='')

    def is_elevated() -> bool:
        """
        Check if the current execution has Administrator Access
        """
        try:
            from ctypes import windll
            return windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def elevate() -> None:
        """
        Restart the current execution as Administrator
        """
        from elevate import elevate

        if not terminal.is_elevated():
            elevate()

    def dash(p:int=100) -> None:
        """
        Print dashes to the terminal

        (p is the % of the terminal width)

        Ex: dash(50) -> |-------------             |

        """
        print(terminal.width() * (p//100) * '-')

def cls() -> None:
    """
    Clear the terminal window

    (Prints a hexidecimal value so the philh.myftp.biz.run can send the signal up from a subprocess)
    """
    from .text import hex
    from os import system

    print(hex.encode('*** Clear Terminal ***'))
    
    if OS() == 'windows':
        system('cls')
    else:
        system('clear')

class power:
    """
    Computer Power Controls
    """

    def restart(t:int=30) -> None:
        """
        Restart the computer after {t} seconds
        """
        from . import run

        run(
            args = ['shutdown', '/r', '/t', t],
            wait = True
        )

    def shutdown(t:int=30) -> None:
        """
        Shutdown the computer after {t} seconds
        """
        from . import run
        
        run(
            args = ['shutdown', '/s', '/t', t],
            wait = True
        )

    def abort() -> None:
        """
        Abort any pending shutdowns/restarts
        """
        from . import run
        
        run(
            args = ['shutdown', '/a'],
            wait = True
        )

def print(
    *args,
    pause: bool = False,
    color: 'colors.names' = 'DEFAULT',
    sep: str = ' ',
    end: str = '\n',
    overwrite: bool = False
) -> None:
    """
    Wrapper for built-in print function
    """
    from .db import colors
    
    if overwrite:
        end = ''
        terminal.del_last_line()
    
    message = colors.values[color.upper()]
    for arg in args:
        message += str(arg) + sep

    message = message[:-1] + colors.values['DEFAULT'] + end

    if pause:
        input(message)
    else:
        terminal.write(message)

def script_dir(__file__) -> 'Path':
    """
    Get the directory of the current script
    """
    from os import path

    return Path(path.abspath(__file__)).parent()

class _mtime:

    def __init__(self, path:Path):
        self.path = path

    def set(self, mtime=None):
        from .time import now
        from os import utime

        if mtime:
            utime(self.path.path, (mtime, mtime))
        else:
            now = now().unix
            utime(self.path.path, (now, now))

    def get(self):
        from os import path

        return path.getmtime(self.path.path)
    
    def stopwatch(self):
        from .time import Stopwatch
        SW = Stopwatch()
        SW.start_time = self.get()
        return SW

class _var:

    def __init__(self,
        file: Path,
        title: str,
        default = None
    ):
        from .text import hex

        self.file = file
        self.title = title
        self.default = default

        self.path = file.path + ':' + hex.encode(title)

        file.set_access.full()

    def read(self):
        from .text import hex

        try:
            value = open(self.path).read()
            return hex.decode(value)
        except OSError:
            return self.default
        
    def save(self, value):
        from .text import hex
        
        try:
            m = _mtime(self.file).get()

            open(self.path, 'w').write(
                hex.encode(value)
            )

            _mtime(self.file).set(m)
        except OSError:
            print(
                f"Error setting var '{self.title}' at '{str(self.file)}'",
                color = 'RED'
            )

class _set_access:

    def __init__(self, path:'Path'):
        self.path = path

    def __paths(self) -> Generator['Path']:

        yield self.path

        if self.path.isdir():
            for path in self.path.descendants():
                yield path
    
    def readonly(self):
        from os import chmod

        for path in self.__paths():
            chmod(str(path), 0o644)

    def full(self):
        from os import chmod

        for path in self.__paths():
            chmod(str(path), 0o777)

def mkdir(path:str|Path) -> None:
    """
    Make a Directory
    """
    from os import makedirs

    makedirs(str(path), exist_ok=True)

def link(src:Path, dst:Path) -> None:
    """
    Create a Symbolic Link
    """
    from os import link

    if dst.exists():
        dst.delete()

    mkdir(dst.parent())

    link(
        src = str(src),
        dst = str(dst)
    )

def relscan(
    src: Path,
    dst: Path
) -> list[dict[Literal['src', 'dst'], Path]]:
    """
    Relatively Scan two directories

    EXAMPLE:

    C:/ - |
    (src) |
          | - Child1

    relscan(Path('C:/'), Path('D:/')) -> [{
        'src': Path('C:/Child1')
        'dst': Path('D:/Child1')
    }]
    """
    from os import listdir

    items = []

    def scanner(src_:Path, dst_:Path):
        for item in listdir(src.path):

            s = src_.child(item)
            d = dst_.child(item)

            if s.isfile():
                items.append({
                    'src': s,
                    'dst': d
                })

            elif s.isdir():
                scanner(s, d)
            
    scanner(src, dst)
    
    return items

def warn(exc: Exception) -> None:
    """
    Print an exception to the terminal without stopping the execution
    """
    from io import StringIO
    from traceback import print_exception
    
    IO = StringIO()

    print_exception(exc, file=IO)
    terminal.write(IO.getvalue(), 'err')

def input[D] (
    prompt: str,
    timeout: int = None,
    default: D = None
) -> D | str:
    """
    Ask for user input from the terminal

    Will return default upon timeout
    """
    from inputimeout import inputimeout, TimeoutOccurred
    from builtins import input

    if timeout:

        try:
            return inputimeout(
                prompt = prompt,
                timeout = timeout
            )
        except TimeoutOccurred:
            return default
    
    else:
        return input(prompt)

class Task:
    """
    System Task

    Wrapper for psutil.Process
    """

    def __init__(self, id:str|int):

        self.id = id
        """PID / IM"""

    def __scanner(self) -> Generator['Process']:
        """
        Scan for the main process any of it's children
        """
        from psutil import process_iter, Process, NoSuchProcess

        main = None

        if isinstance(self.id, int):
            try:
                main = Process(self.id)
            except NoSuchProcess:
                pass

        elif isinstance(self.id, str):
            for proc in process_iter():
                if proc.name().lower() == self.id.lower():
                    main = Process(proc.pid)
                    break

        if main and main.is_running():
            try:

                for child in main.children(True):
                    if child.is_running():
                        yield child

            except NoSuchProcess:
                pass

    def cores(self, *cores:int) -> bool:
        """
        Set CPU Affinity

        Returns True upon success, and false upon failure

        Ex: Task.cores(0, 2, 4) -> Process will only use CPU cores 0, 2, & 4
        """
        from psutil import NoSuchProcess, AccessDenied

        for p in self.__scanner():
            try:
                p.cpu_affinity(cores)
                return True
            except (NoSuchProcess, AccessDenied):
                return False

    def stop(self) -> None:
        """
        Stop Process and all of it's children
        """
        for p in self.__scanner():
            p.terminate()

    def exists(self):
        """
        Check if the process is running
        """
        
        processes = list(self.__scanner())
        
        return len(processes) > 0
