import sys
from cx_Freeze import setup, Executable

executables = [Executable("gui.py",  
                          icon = "./images/rp_sq_48.ico",
                          targetName = "Reddit Paper.exe",
                          shortcutName = "Reddit Paper",
                          shortcutDir = "DesktopFolder")]
                          #base = ("Win32GUI" if sys.platform == 'win32' else None))]
included_files = ["./images", "redditpaper.py",
		              "C:\\Python34\\Lib\\site-packages\\praw\\praw.ini",
                  "cacert.pem",
                  "C:\\Python34\\lib\\abc.py",
                  "C:\\Python34\\lib\\argparse.py",
                  "C:\\Python34\\lib\\ast.py",
                  "C:\\Python34\\lib\\base64.py",
                  "C:\\Python34\\lib\\bisect.py",
                  "C:\\Python34\\lib\\calendar.py",
                  "C:\\Python34\\lib\\cgi.py",
                  "C:\\Python34\\lib\\codecs.py",
                  "C:\\Python34\\lib\\configparser.py",
                  "C:\\Python34\\lib\\contextlib.py",
                  "C:\\Python34\\lib\\copy.py",
                  "C:\\Python34\\lib\\copyreg.py",
                  "C:\\Python34\\lib\\datetime.py",
                  "C:\\Python34\\lib\\enum.py",
                  "C:\\Python34\\lib\\fnmatch.py",
                  "C:\\Python34\\lib\\functools.py",
                  "C:\\Python34\\lib\\genericpath.py",
                  "C:\\Python34\\lib\\gettext.py",
                  "C:\\Python34\\lib\\hashlib.py",
                  "C:\\Python34\\lib\\heapq.py",
                  "C:\\Python34\\lib\\hmac.py",
                  "C:\\Python34\\lib\\inspect.py",
                  "C:\\Python34\\lib\\io.py",
                  "C:\\Python34\\lib\\keyword.py",
                  "C:\\Python34\\lib\\linecache.py",
                  "C:\\Python34\\lib\\locale.py",
                  "C:\\Python34\\lib\\mimetypes.py",
                  "C:\\Python34\\lib\\ntpath.py",
                  "C:\\Python34\\lib\\nturl2path.py",
                  "C:\\Python34\\lib\\numbers.py",
                  "C:\\Python34\\lib\\operator.py",
                  "C:\\Python34\\lib\\os.py",
                  "C:\\Python34\\lib\\pickle.py",
                  "C:\\Python34\\lib\\pickletools.py",
                  "C:\\Python34\\lib\\platform.py",
                  "C:\\Python34\\lib\\posixpath.py",
                  "C:\\Python34\\lib\\pprint.py",
                  "C:\\Python34\\lib\\queue.py",
                  "C:\\Python34\\lib\\quopri.py",
                  "C:\\Python34\\lib\\random.py",
                  "C:\\Python34\\lib\\re.py",
                  "C:\\Python34\\lib\\reprlib.py",
                  "C:\\Python34\\lib\\shutil.py",
                  "C:\\Python34\\lib\\site.py",
                  "C:\\Python34\\lib\\site-packages\\six.py",
                  "C:\\Python34\\lib\\socket.py",
                  "C:\\Python34\\lib\\socketserver.py",
                  "C:\\Python34\\lib\\sre_compile.py",
                  "C:\\Python34\\lib\\sre_constants.py",
                  "C:\\Python34\\lib\\sre_parse.py",
                  "C:\\Python34\\lib\\ssl.py",
                  "C:\\Python34\\lib\\stat.py",
                  "C:\\Python34\\lib\\string.py",
                  "C:\\Python34\\lib\\stringprep.py",
                  "C:\\Python34\\lib\\struct.py",
                  "C:\\Python34\\lib\\subprocess.py",
                  "C:\\Python34\\lib\\sysconfig.py",
                  "C:\\Python34\\lib\\tarfile.py",
                  "C:\\Python34\\lib\\tempfile.py",
                  "C:\\Python34\\lib\\textwrap.py",
                  "C:\\Python34\\lib\\threading.py",
                  "C:\\Python34\\lib\\timeit.py",
                  "C:\\Python34\\lib\\token.py",
                  "C:\\Python34\\lib\\tokenize.py",
                  "C:\\Python34\\lib\\traceback.py",
                  "C:\\Python34\\lib\\types.py",
                  "C:\\Python34\\lib\\site-packages\\update_checker.py",
                  "C:\\Python34\\lib\\uu.py",
                  "C:\\Python34\\lib\\uuid.py",
                  "C:\\Python34\\lib\\warnings.py",
                  "C:\\Python34\\lib\\weakref.py",
                  "C:\\Python34\\lib\\webbrowser.py",
                  "C:\\Python34\\lib\\_bootlocale.py",
                  "C:\\Python34\\lib\\_collections_abc.py",
                  "C:\\Python34\\lib\\_compat_pickle.py",
                  "C:\\Python34\\lib\\_markupbase.py",
                  "C:\\Python34\\lib\\_sitebuiltins.py",
                  "C:\\Python34\\lib\\_strptime.py",
                  "C:\\Python34\\lib\\_weakrefset.py",
                  "C:\\Python34\\lib\\__future__.py",
                  "C:\\Python34\\Lib\\__phello__.foo.py",
                  "C:\\Python34\\Lib\\site-packages\\bs4",
                  "C:\\Python34\\Lib\\collections",
                  "C:\\Python34\\Lib\\ctypes",
                  "C:\\Python34\\Lib\\email",
                  "C:\\Python34\\Lib\\encodings",
                  "C:\\Python34\\Lib\\html",
                  "C:\\Python34\\Lib\\http",
                  "C:\\Python34\\Lib\\importlib",
                  "C:\\Python34\\Lib\\json",
                  "C:\\Python34\\Lib\\logging",
                  "C:\\Python34\\Lib\\site-packages\\PIL",
                  "C:\\Python34\\Lib\\site-packages\\praw",
                  "C:\\Python34\\Lib\\site-packages\\requests",
                  "C:\\Python34\\Lib\\sqlite3",
                  "C:\\Python34\\tcl",
                  "C:\\Python34\\tcl\\tk8.6",
                  "C:\\Python34\\Lib\\tkinter",
                  "C:\\Python34\\Lib\\urllib",
                  "C:\\Python34\\Lib\\__pycache__",
                  # for the call to redditpaper with subprocess
                  "C:\\Python34\\python.exe"]

install_requires = ["praw", "urllib.request", "bs4", "PIL", "sqlite3", "tkinter", "os", "site", "io", "encodings"]

build_exe_options = {
        "include_files": included_files,
        "packages": install_requires,
        "include_msvcr": True
}

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "DTI Playlist",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]playlist.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

msi_data = {"Shortcut": shortcut_table}
bdist_msi_options = {'data': msi_data}

setup(
        name = "Reddit Paper",
        version = "1.1",
        author = "Cameron Gagnon",
        author_email = 'cameron.gagnon@gmail.com',
        url = "http://github.com/cameron-gagnon/reddit-paper",
        executables = executables,
        options = {"build_exe": build_exe_options}
)	
