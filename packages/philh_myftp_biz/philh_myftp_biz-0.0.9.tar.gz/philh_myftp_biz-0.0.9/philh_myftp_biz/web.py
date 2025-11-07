from typing import Literal, Self, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from .pc import Path
    from requests import Response
    from bs4 import BeautifulSoup
    from qbittorrentapi import Client, TorrentDictionary, TorrentFile
    from paramiko.channel import ChannelFile, ChannelStderrFile

def IP(
    method: Literal['local', 'public'] = 'local'
) -> str | None:
    """
    Get the IP Address of the local computer
    """
    from socket import gethostname, gethostbyname

    if not online():
        pass

    elif method == 'local':
        return gethostbyname(gethostname())
    
    elif method == 'public':
        return get('https://api.ipify.org').text

online = lambda: ping('1.1.1.1')
"""Check if the local computer is connected to the internet"""

def ping(
    addr: str,
    timeout: int = 3
) -> bool:
    """
    Ping a network address

    Returns true if ping reached destination
    """
    from ping3 import ping as __ping

    try:

        p = __ping(
            dest_addr = addr,
            timeout = timeout
        )

        return bool(p)
    
    except OSError:
        return False

class Port:
    """
    Details of a port on a network device
    """

    def __init__(self,
        host: str,
        port: int
    ):
        from socket import error, SHUT_RDWR
        from quicksocketpy import socket
        self.port = port

        s = socket()

        try:
            s.connect((host, port))
            s.shutdown(SHUT_RDWR)
            self.listening = True
            """Port is listening"""
            
        except error:
            self.listening = False
            """Port is listening"""
        
        finally:
            s.close()

    def __int__(self) -> int:
        return self.port

def find_open_port(min:int, max:int) -> None | int:
    """
    Find an open port in a range on a network device
    """

    for x in range(min, max+1):
        
        port = Port(IP(), x)
        
        if not port.listening:
            return int(port)

class ssh:
    """
    SSH Client

    Wrapper for paramiko.SSHClient
    """

    class __Response:
        

        def __init__(self,
            stdout: 'ChannelFile',
            stderr: 'ChannelStderrFile'
        ):
            self.output = stdout.read().decode()
            """stdout"""

            self.error = stderr.read().decode()
            """stderr"""

    def __init__(self,
        ip: str,
        username: str,
        password: str,
        timeout: int = None,
        port: int = 22
    ):
        from paramiko import SSHClient, AutoAddPolicy

        self.__client = SSHClient()
        self.__client.set_missing_host_key_policy(AutoAddPolicy())
        self.__client.connect(ip, port, username, password, timeout=timeout)

        self.close = self.__client.close
        """Close the connection to the remote computer"""

    def run(self, command:str) -> __Response:
        """
        Send a command to the remote computer
        """

        # Execute a command
        stdout, stderr = self.__client.exec_command(command)[1:]

        return self.__Response(stdout, stderr)

class Magnet:
    """
    Handler for MAGNET URLs
    """

    __qualities = {
        'hdtv': 0,
        'tvrip': 0,
        '2160p': 2160,
        '1440p': 1440,
        '1080p': 1080,
        '720p': 720,
        '480p': 480,
        '360p': 360,
        '4K': 2160
    }
    """
    QUALITY LOOKUP TABLE

    Find quality in magnet title
    """

    def __init__(self,
        title: str,
        seeders: int,
        leechers: int,
        url: str,
        size: str,
        qbit: 'api.qBitTorrent' = None
    ):
            
        self.title = title.lower()
        self.seeders = seeders
        self.leechers = leechers
        self.url = url
        self.size = size
        self.__qbit = qbit

        self.quality = 0
        for term in self.__qualities:
            if term in title.lower():
                self.quality = self.__qualities[term]

    def start(self, path:str=None):
        self.__qbit.start(self, path)

    def stop(self, rm_files:bool=True):
        self.__qbit.stop(self, rm_files)

    def restart(self):
        self.__qbit.restart(self)
    
    def files(self):
        return self.__qbit.files(self)
    
    def finished(self):
        return self.__qbit.finished(self)
    
    def errored(self):
        return self.__qbit.errored(self)
    
    def downloading(self):
        return self.__qbit.downloading(self)
    
    def exists(self):
        return self.__qbit.exists(self)

def get(
    url: str,
    params: dict = {},
    headers: dict = {},
    stream: bool = None,
    cookies = None
) -> 'Response':
    """
    Wrapper for requests.get
    """
    from requests import get as __get
    from requests.exceptions import ConnectionError
    from .pc import warn

    headers['User-Agent'] = 'Mozilla/5.0'
    headers['Accept-Language'] = 'en-US,en;q=0.5'

    while True:
        try:
            return __get(
                url = url,
                params = params,
                headers = headers,
                stream = stream,
                cookies = cookies
            )
        except ConnectionError as e:
            warn(e)

class api:
    """
    Wrappers for several APIs
    """

    class omdb:
        """
        OMDB API

        'https://www.omdbapi.com/{url}'
        """

        def __init__(self):
            self.__url = 'https://www.omdbapi.com/'
            self.__apikey = 'dc888719'

        class __data:
            def __init__(self,
                Title: str,
                Year: int,
                Seasons: dict[str, list[str]] = None
            ):
                self.Title = Title
                self.Year = Year
                self.Seasons = Seasons

        def movie(self,
            title: str,
            year: int
        ) -> None | __data:

            r: dict[str, str] = get(
                url = self.__url,
                params = {
                    't': title,
                    'y': year,
                    'apikey': self.__apikey
                }
            ).json()

            if bool(r['Response']) and (r['Type'] == 'movie'):
                return self.__data(
                    Title = r['Title'],
                    Year = int(r['Year'])
                )

        def show(self,
            title: str,
            year: int
        ) -> None | __data:

            r: dict[str, str] = get(
                url = self.__url,
                params = {
                    't': title,
                    'y': year,
                    'apikey': self.__apikey
                }
            ).json()

            if bool(r['Response']) and (r['Type'] == 'series'):

                Seasons: dict[str, int] = {}

                for season in range(1, int(r['totalSeasons'])+1):

                    r_: dict[str, str] = get(
                        url = self.__url,
                        params = {
                            't': title,
                            'y': year,
                            'Season': season,
                            'apikey': self.__apikey
                        }
                    ).json()

                    x = str(season).zfill(2)
                    Seasons[x] = []

                    for e in r_['Episodes']:
                        Seasons[x] += [str(e['Episode']).zfill(2)]

                return self.__data(
                    Title = r['Title'],
                    Year = int(r['Year'].split(r'–')[0]),
                    Seasons = Seasons
                )
    
    def numista(url:str='', params:list=[]):
        """
        Numista API

        'https://api.numista.com/v3/{url}'
        """
        return get(
            url = f'https://api.numista.com/v3/{url}',
            params = params,
            headers = {'Numista-API-Key': 'KzxGDZXGQ9aOQQHwnZSSDoj3S8dGcmJO9SLXxYk1'},
        ).json()
    
    def mojang(url:str='', params:list=[]):
        """
        Mojang API

        'https://api.mojang.com/{url}'
        """
        return get(
            url = f'https://api.mojang.com/{url}',
            params = params
        ).json()
    
    def geysermc(url:str='', params:list=[]):
        """
        GeyserMC API

        'https://api.geysermc.org/v2/{url}'        
        """
        return get(
            url = f'https://api.geysermc.org/v2/{url}',
            params = params
        ).json()

    class qBitTorrent:
        """
        Client for qBitTorrent Web Server
        """

        class File:

            def __init__(self,
                torrent: 'TorrentDictionary',
                file: 'TorrentFile'
            ):
                from .pc import Path

                self.path = Path(f'{torrent.save_path}/{file.name}')
                self.size: float = file.size

                self.__file = file
                self.__torrent = torrent

            def start(self,
                priority: Literal['Low', 'Med', 'High'] = 'Med'
            ):
                self.__torrent.file_priority(
                    file_ids = self.__file.id,
                    priority = {
                        'Low': 1,
                        'Med': 2,
                        'High': 3
                    }[priority]
                )

            def stop(self):
                self.__torrent.file_priority(
                    file_ids = self.__file.id,
                    priority = 0
                )

            def finished(self) -> bool:
                return (self.__file.progress == 1.0)

        def __init__(self,
            host: str,
            username: str,
            password: str,
            port: int = 8080
        ):
            from qbittorrentapi import Client

            self.__rclient = Client(
                host = host,
                port = port,
                username = username,
                password = password,
                VERIFY_WEBUI_CERTIFICATE = False
            )

        def _client(self) -> 'Client':
            """
            Wait for server connection, then return qbittorrentapi.Client
            """
            from qbittorrentapi import LoginFailed, Forbidden403Error

            while True:

                try:
                    self.__rclient.auth_log_in()
                    return self.__rclient
                
                except (LoginFailed, Forbidden403Error):
                    pass

        def start(self,
            magnet: Magnet,
            path: str = None
        ) -> None:
            """
            Start Downloading a Magnet
            """

            self._client().torrents_add(
                urls = [magnet.url],
                save_path = path,
                tags = magnet.url
            )

        def restart(self,
            magnet: Magnet
        ) -> None:
            """
            Restart Downloading a Magnet
            """

            self.stop(magnet)
            self.start(magnet)

        def files(self,
            magnet: Magnet
        ) -> Generator[File]:
            """
            List all files in Magnet Download

            EXAMPLE:

            qbt = qBitTorrent(*args)

            for file in qbit.files():
            
                file['path'] # Path of the downloaded file
                file['size'] # Full File Size
            
            """

            #
            for t in self._client().torrents_info():
                
                #
                if magnet.url in t.tags:
                    
                    #
                    for f in t.files:
                        
                        #
                        yield self.File(t, f)

                    break

        def stop(self,
            magnet: Magnet,
            rm_files: bool = True
        ) -> None:
            """
            Stop downloading a Magnet
            """
            for t in self._client().torrents_info():
                if magnet.url in t.tags:
                    t.delete(rm_files)
                    return

        def clear(self, rm_files:bool=True) -> None:
            """
            Remove all Magnets from the download queue
            """
            for t in self._client().torrents_info():
                t.delete(rm_files)

        def sort(self) -> None:
            """
            Automatically Sort the Download Queue
            """
            from .array import sort, priority
            from qbittorrentapi import TorrentDictionary

            # Get sorted list of torrents
            items: list[TorrentDictionary] = sort(

                list(self._client().torrents_info()), # All torrents in queue
                
                lambda t: priority(
                    _1 = t.num_complete, # Seeders
                    _2 = (t.size - t.downloaded) # Remaining
                )

            )

            # Loop through all items
            for t in items:

                # Move to the top of the queue
                t.top_priority()

        def finished(self,
            magnet: Magnet
        ) -> None | bool:
            """
            Check if a magnet is finished downloading
            """
            
            for t in self._client().torrents_info():
                if magnet.url in t.tags:
                    return (t.state_enum.is_uploading or t.state_enum.is_complete)

        def errored(self,
            magnet: Magnet
        ) -> None | bool:
            """
            Check if a magnet is errored
            """
            for t in self._client().torrents_info():
                if magnet.url in t.tags:
                    return t.state_enum.is_errored

        def downloading(self,
            magnet: Magnet
        ) -> bool:
            for t in self._client().torrents_info():
                if magnet.url in t.tags:
                    return t.state_enum.is_downloading
            return False
        
        def exists(self,
            magnet: Magnet
        ) -> bool:
            for t in self._client().torrents_info():
                if magnet.url in t.tags:
                    return True
            return False

    class thePirateBay:
        """
        thePirateBay

        'https://thepiratebay0.org/'
        """
        
        def __init__(self):
            self.__url = "https://thepiratebay.org/search.php?q={}&video=on"

        def search(self,
            *queries: str,
            driver: 'Driver' = None,
            qbit: 'api.qBitTorrent' = None
        ) -> Generator[Magnet]:
            """
            Search thePirateBay for magnets

            EXAMPLE:
            for magnet in thePirateBay.search('term1', 'term2'):
                magnet
            """
            from urllib3.exceptions import ReadTimeoutError
            from .text import rm
            from .db import size

            # Initialize new driver if not given
            if driver is None:
                driver = Driver()

            # Iter through queries
            for query in queries:

                # Remove all "." & "'" from query
                query = rm(query, '.', "'")

                # Open the search in a url
                try:
                    driver.open(
                        url = self.__url.format(query)
                    )
                except ReadTimeoutError:
                    continue

                # Set driver var 'lines' to a list of lines
                driver.run("window.lines = document.getElementsByClassName('list-entry')")

                # Iter from 0 to # of lines
                for x in range(0, driver.run('return lines.length')):

                    # 
                    start = f"return lines[{x}]"

                    try:

                        # Yield a magnet instance
                        yield Magnet(
                        
                            title = driver.run(start+".children[1].children[0].text"),

                            seeders = int(driver.run(start+".children[5].textContent")),

                            leechers = int(driver.run(start+".children[6].textContent")),

                            url = driver.run(start+".children[3].children[0].href"),
                            
                            size = size.to_bytes(driver.run(start+".children[4].textContent")),

                            qbit = qbit

                        )

                    except KeyError:
                        pass

class Soup:
    """
    Wrapper for bs4.BeautifulSoup

    Uses 'html.parser'
    """

    def __init__(self,
        soup: 'str | BeautifulSoup | bytes'
    ):
        from lxml.etree import _Element, HTML
        from bs4 import BeautifulSoup

        if isinstance(soup, BeautifulSoup):
            self.__soup = soup
        
        elif isinstance(soup, (str, bytes)):
            self.__soup = BeautifulSoup(
                soup,
                'html.parser'
            )

        self.select = self.__soup.select
        """Perform a CSS selection operation on the current element."""

        self.select_one = self.__soup.select_one
        """Perform a CSS selection operation on the current element."""

        self.__dom:_Element = HTML(str(soup))

    def element(self,
        by: Literal['class', 'id', 'xpath', 'name', 'attr'],
        name: str
    ) -> list[Self]:
        """
        Get List of Elements by query
        """

        by = by.lower()

        if by in ['class', 'classname', 'class_name']:
            items = self.__soup.select(f'.{name}')

        elif by in ['id']:
            items = self.__soup.find_all(id=name)

        elif by in ['xpath']:
            items = self.__dom.xpath(name)

        elif by in ['name']:
            items = self.__soup.find_all(name=name)

        elif by in ['attr', 'attribute']:
            t, c = name.split('=')
            items = self.__soup.find_all(attrs={t: c})

        return [Soup(i) for i in items]

class Driver:
    """
    Firefox Web Driver
    
    Wrapper for FireFox Selenium Session
    """
    from selenium.webdriver.remote.webelement import WebElement
            
    def __init__(
        self,
        headless: bool = True,
        cookies: (list[dict] | None) = None,
        debug: bool = False
    ):
        from selenium.webdriver import FirefoxService, FirefoxOptions, Firefox
        from selenium.common.exceptions import InvalidCookieDomainException
        from subprocess import CREATE_NO_WINDOW
        
        self.__via_with = False
        self.__debug_enabled = debug

        service = FirefoxService()
        service.creation_flags = CREATE_NO_WINDOW

        options = FirefoxOptions()
        options.add_argument("--disable-search-engine-choice-screen")        
        if headless:
            options.add_argument("--headless")

        # Start Chrome Session with options
        self.__session = Firefox(options, service)

        if cookies:
            for cookie in cookies:
                try:
                    self.__session.add_cookie(cookie)
                except InvalidCookieDomainException:
                    pass

        self.current_url = self.__session.current_url
        """URL of the Current Page"""

        self.reload = self.__session.refresh
        """Reload the Current Page"""

        self.run = self.__session.execute_script
        """Run JavaScript Code on the Current Page"""

    def __enter__(self):
        self.__via_with = True
        return self

    def __exit__(self, *_):
        if self.__via_with:
            self.close()
    
    def __debug(self,
        title: str,
        data: dict ={}
        ) -> None:
        """
        Print a message if debugging is enabled
        """
        from .json import dumps
        
        if self.__debug_enabled:
            print()
            print(title, dumps(data))

    def element(self,
        by: Literal['class', 'id', 'xpath', 'name', 'attr'],
        name: str,
        wait: bool = True
    ) -> list[WebElement]:
        """
        Get List of Elements by query
        """
        from selenium.webdriver.common.by import By

        # Force 'by' input to lowercase
        by = by.lower()

        # Check if by is 'class'
        if by == 'class':
            
            if isinstance(name, list):
                name = '.'.join(name)

            _by = By.CLASS_NAME

        # Check if by is 'id'
        if by == 'id':
            _by = By.ID

        # Check if by is 'xpath'
        if by == 'xpath':
            _by = By.XPATH

        # Check if by is 'name'
        if by == 'name':
            _by = By.NAME

        # Check if by is 'attr'
        if by == 'attr':
            _by = By.CSS_SELECTOR
            t, c = name.split('=')
            name = f"a[{t}='{c}']"

        self.__debug(
            title = "Finding Element", 
            data = {'by': by, 'name':name}
        )

        if wait:

            while True:

                elements = self.__session.find_elements(_by, name)

                if len(elements) > 0:
                    return elements

        else:
            return self.__session.find_elements(_by, name)

    def open(self,
        url: str
    ) -> None:
        """
        Open a url

        Waits for page to fully load
        """
        
        # Open the url
        self.__session.get(url)

        # Print Debug Messsage
        self.__debug(
            title = "Opening", 
            data = {'url':url}
        )

        # Wait until page is loaded
        while self.run("return document.readyState") != "complete":
            pass

    def close(self) -> None:
        """
        Close the Session
        """
        from selenium.common.exceptions import InvalidSessionIdException
        
        # Print Debug Message
        self.__debug('Closing Session')

        try:
            # Exit Session
            self.__session.close()
        except InvalidSessionIdException:
            pass

    def soup(self) -> 'Soup':
        """
        Get a soup of the current page
        """
        return Soup(
            self.__session.page_source
        )

def static(url) -> Soup:
    """
    Save a webpage as a static soup
    """

    return Soup(get(url).content)

def dynamic(
    url: str,
    driver: 'Driver' = None
) -> 'Soup':
    """
    Open a webpage in a webdriver and return a soup of the contents
    """
    from bs4 import BeautifulSoup
    
    if driver is None:
        driver = Driver()

    driver.open(url, True)

    return driver.soup()

def download(
    url: str,
    path: 'Path',
    show_progress: bool = True,
    cookies = None
) -> None:
    """
    Download file to disk
    """
    from tqdm import tqdm
    from urllib.request import urlretrieve

    if show_progress:

        r = get(
            url = url,
            stream = True,
            cookies = cookies
        )

        file = path.open('wb')

        pbar = tqdm(
            total = int(r.headers.get("content-length", 0)), # Total Download Size
            unit = "B",
            unit_scale = True
        )

        with pbar:
            for data in r.iter_content(1024):
                pbar.update(len(data))
                file.write(data)

    else:
        urlretrieve(url, str(path))
