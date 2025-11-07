from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from .pc import Path

def output(data) -> None:
    """
    Print the data to the terminal as hexidecimal, then exit
    """
    from .text import hex
    from .pc import cls

    cls()
    print(';' + hex.encode(data) + ';')
    exit()

def input() -> list:
    """
    Decode Command Line Arguements
    """
    from .__init__ import args
    from .text import hex

    return hex.decode(args()[0])

def when_modified(*modules:'Module') -> Generator['WatchFile']:
    """
    Wait for any Watch File to be modified

    EXAMPLE:
    m1 = Module('C:/module1/')
    m2 = Module('C:/module2/')

    gen = modules.when_modified(m1, m2)

    for watchfile in gen:
        {Code to run when a watchfile is modified}
    """
    from .time import sleep

    watch_files: list['WatchFile'] = []

    for module in modules:
        watch_files += module.watch_files

    while True:
        for wf in watch_files:
            if wf.modified():
                yield wf

        sleep(.25)

def fetch() -> Generator['Module']:
    """
    Fetch all modules in the 'E:/' directory
    """
    from .pc import Path
    
    path = Path('E:/')
    
    for p in path.children():
    
        m = Module(p.name())
    
        if m.enabled:
            yield m

class Module:
    """
    Allows for easy interaction with other languages in a directory

    Make sure to add a file labed 'Module.yaml' in the directory
    'Module.yaml' needs to be configured with the following syntax:
    \"""
        enabled: False
        packages: []
        watch_files: []
    \"""

    EXAMPLE:
    
    m = Module('E:/testmodule')

    # Runs any script with a path starting with "E:/testmodule/main.###"
    # Handlers for the extensions are automatically interpreted
    m.run('main')

    # 'E:/testmodule/sub/script.###'
    m.run('sub', 'script')
    m.run('sub/script')
    """

    def __init__(self,
        module: 'str | Path'
    ):
        from .pc import Path
        from .file import YAML

        self.dir = Path(module)
        self.name = self.dir.name()

        config = YAML(
            path = self.dir.child('module.yaml'),
            default = {
                'enabled' : False,
                'packages' : [],
                'watch_files' : []
            }
        ).read()

        self.enabled = config['enabled']

        self.packages: list[str] = config['packages']

        self.watch_files: list[WatchFile] = []
        for WFpath in config['watch_files']:
            self.watch_files += [WatchFile(
                module = self,
                path = WFpath
            )]

    def run(self, *args, hide:bool=False) -> 'None | Process':
        """
        Execute a new Process and wait for it to finish
        """
        if self.enabled:
            return Process(
                module = self,
                args = list(args),
                hide = hide,
                wait = True
            )

    def start(self, *args, hide:bool=False) -> 'None | Process':
        """
        Execute a new Process simultaneously with the current execution
        """
        if self.enabled:
            return Process(
                module = self,
                args = list(args),
                hide = hide,
                wait = False
            )

    def file(self, *name:str) -> 'Path':
        """
        Find a file by it's name

        Returns FileNotFoundError if file does not exist

        EXAMPLE:

        # "run.py"
        m.file('run')

        # "web/script.js"
        m.file('web', 'script')
        m/file('web/script')
        """

        parts: list[str] = []
        for n in name:
            parts += n.split('/')
        
        dir = self.dir.child('/'.join(parts[:-1]))

        for p in dir.children():
            if (p.name().lower()) == (parts[-1].lower()):
                return p

        raise FileNotFoundError(dir.path + '.*')

    def install(self, hide:bool=True) -> None:
        """
        Install and Upgrade all python packages
        """
        from .__init__ import run

        for pkg in self.packages:
            run(
                args = ['pip', 'install', '--upgrade', pkg],
                wait = True,
                terminal = 'pym',
                hide = hide
            )

    def watch(self) -> 'when_modified':
        """
        Returns a modules.when_modified generator for the current module
        """
        return when_modified(self)

class Process:
    """
    Wrapper for Subprocesses started by a Module
    """

    def __init__(self,
        module: Module,
        args: list[str],
        hide: bool,
        wait: bool
    ):
        from .text import hex
        from .__init__ import run

        file = module.file(args[0])
        args[0] = file.path

        self.__isPY = (file.ext() == 'py')
        if self.__isPY:
            args = [args[0], hex.encode(args[1:])]

        self.__p = run(
            args = args,
            wait = wait,
            hide = hide,
            terminal = 'ext',
            cores = 3
        )

        self.start    = self.__p.start
        self.stop     = self.__p.stop
        self.restart  = self.__p.restart
        self.finished = self.__p.finished
        self.output   = self.__p.output

class WatchFile:
    """
    Watch File for Module
    """

    def __init__(self,
        module: 'Module',
        path: str
    ):
        from .pc import Path
        
        if path.startswith('/'):
            self.path = module.dir.child(path)
        else:
            self.path = Path(path)

        self.module = module

        self.__mtime = self.path.var('__mtime__')
        
        self.__mtime.save(
            value = self.path.mtime.get()
        )

    def modified(self) -> bool:
        """Check if the file has been modified since declaration"""
        
        return (self.__mtime.read() != self.path.mtime.get())
