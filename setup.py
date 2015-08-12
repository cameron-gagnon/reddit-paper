import sys
from cx_Freeze import setup, Executable

executables = [Executable("gui.py",  
                          icon = "./images/rp_sq_48.ico",
                          targetName = "Reddit Paper.exe",
                          shortcutName = "Reddit Paper",
                          shortcutDir = "DesktopFolder")]
                          #base = ("Win32GUI" if sys.platform == 'win32' else None))]
included_files = ["images/a_c.png",
                  "images/a_u.png",
                  "images/c_c.png",
                  "images/c_u.png",
                  "images/error.png",
                  "images/p_c.png",
                  "images/p_u.png",
                  "images/rp_sq.png",
                  "images/rp_sq_48.ico",
                  "images/s_c.png",
                  "images/s_u.png",
                  "redditpaper.py",
                  "C:\\Python34\\Lib\\abc.py",
                  "C:\\Python34\\Lib\\argparse.py",
                  "C:\\Python34\\Lib\\ast.py",
                  "C:\\Python34\\Lib\\base64.py",
                  "C:\\Python34\\Lib\\bisect.py",
                  "C:\\Python34\\Lib\\calendar.py",
                  "C:\\Python34\\Lib\\cgi.py",
                  "C:\\Python34\\Lib\\codecs.py",
                  "C:\\Python34\\Lib\\configparser.py",
                  "C:\\Python34\\Lib\\contextlib.py",
                  "C:\\Python34\\Lib\\copy.py",
                  "C:\\Python34\\Lib\\copyreg.py",
                  "C:\\Python34\\Lib\\datetime.py",
                  "C:\\Python34\\Lib\\enum.py",
                  "C:\\Python34\\Lib\\fnmatch.py",
                  "C:\\Python34\\Lib\\functools.py",
                  "C:\\Python34\\Lib\\genericpath.py",
                  "C:\\Python34\\Lib\\gettext.py",
                  "C:\\Python34\\Lib\\hashlib.py",
                  "C:\\Python34\\Lib\\heapq.py",
                  "C:\\Python34\\Lib\\hmac.py",
                  "C:\\Python34\\Lib\\inspect.py",
                  "C:\\Python34\\Lib\\io.py",
                  "C:\\Python34\\Lib\\keyword.py",
                  "C:\\Python34\\Lib\\linecache.py",
                  "C:\\Python34\\Lib\\locale.py",
                  "C:\\Python34\\Lib\\mimetypes.py",
                  "C:\\Python34\\Lib\\ntpath.py",
                  "C:\\Python34\\Lib\\nturl2path.py",
                  "C:\\Python34\\Lib\\numbers.py",
                  "C:\\Python34\\Lib\\operator.py",
                  "C:\\Python34\\Lib\\os.py",
                  "C:\\Python34\\Lib\\pickle.py",
                  "C:\\Python34\\Lib\\pickletools.py",
                  "C:\\Python34\\Lib\\platform.py",
                  "C:\\Python34\\Lib\\posixpath.py",
                  "C:\\Python34\\Lib\\pprint.py",
                  "C:\\Python34\\Lib\\queue.py",
                  "C:\\Python34\\Lib\\quopri.py",
                  "C:\\Python34\\Lib\\random.py",
                  "C:\\Python34\\Lib\\re.py",
                  "C:\\Python34\\Lib\\reprlib.py",
                  "C:\\Python34\\Lib\\shutil.py",
                  "C:\\Python34\\Lib\\site.py",
                  "C:\\Python34\\Lib\\socket.py",
                  "C:\\Python34\\Lib\\socketserver.py",
                  "C:\\Python34\\Lib\\sre_compile.py",
                  "C:\\Python34\\Lib\\sre_constants.py",
                  "C:\\Python34\\Lib\\sre_parse.py",
                  "C:\\Python34\\Lib\\ssl.py",
                  "C:\\Python34\\Lib\\stat.py",
                  "C:\\Python34\\Lib\\string.py",
                  "C:\\Python34\\Lib\\stringprep.py",
                  "C:\\Python34\\Lib\\struct.py",
                  "C:\\Python34\\Lib\\subprocess.py",
                  "C:\\Python34\\Lib\\sysconfig.py",
                  "C:\\Python34\\Lib\\tarfile.py",
                  "C:\\Python34\\Lib\\tempfile.py",
                  "C:\\Python34\\Lib\\textwrap.py",
                  "C:\\Python34\\Lib\\threading.py",
                  "C:\\Python34\\Lib\\timeit.py",
                  "C:\\Python34\\Lib\\token.py",
                  "C:\\Python34\\Lib\\tokenize.py",
                  "C:\\Python34\\Lib\\traceback.py",
                  "C:\\Python34\\Lib\\types.py",
                  "C:\\Python34\\Lib\\uu.py",
                  "C:\\Python34\\Lib\\uuid.py",
                  "C:\\Python34\\Lib\\warnings.py",
                  "C:\\Python34\\Lib\\weakref.py",
                  "C:\\Python34\\Lib\\webbrowser.py",
                  "C:\\Python34\\Lib\\_bootlocale.py",
                  "C:\\Python34\\Lib\\_collections_abc.py",
                  "C:\\Python34\\Lib\\_compat_pickle.py",
                  "C:\\Python34\\Lib\\_markupbase.py",
                  "C:\\Python34\\Lib\\_sitebuiltins.py",
                  "C:\\Python34\\Lib\\_strptime.py",
                  "C:\\Python34\\Lib\\_weakrefset.py",
                  "C:\\Python34\\Lib\\__future__.py",
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
                  "C:\\Python34\\Lib\\sqlite3",
                  "C:\\Python34\\tcl",
                  "C:\\Python34\\tcl\\tk8.6",
                  "C:\\Python34\\Lib\\tkinter",
                  "C:\\Python34\\Lib\\urllib",
                  "C:\\Python34\\Lib\\site-packages\\six.py",
                  "C:\\Python34\\Lib\\site-packages\\update_checker.py",
                  "C:\\Python34\\Lib\\site-packages\\PIL",
                  "C:\\Python34\\Lib\\site-packages\\praw",
                  "C:\\Python34\\Lib\\site-packages\\praw\\praw.ini",
                  "C:\\Python34\\Lib\\site-packages\\requests",
                  # needed for ssl authentication
                  "cacert.pem",
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
