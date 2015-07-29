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
                  "C:\\Python34\\Lib\\codecs.py",
                  "C:\\Python34\\Lib\\encodings",
                  # for the call to redditpaper with subprocess
                  "C:\\Python34\\python.exe"]

install_requires = ["praw", "urllib.request", "bs4", "PIL", "sqlite3", "tkinter"]

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