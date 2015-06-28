import sys
from cx_Freeze import setup, Executable

executables = [Executable("gui.pyw", base = ("Win32GUI" if sys.platform == 'win32' else None), icon = "./images/redditicon_48.ico", targetName = "Reddit Paper.exe")]
included_files = ["./images", "redditpaper.pyw", "detools",
		  "C:\\Python34\\Lib\\site-packages\\praw\\praw.ini"]

install_requires = ["praw", "urllib.request", "bs4", "PIL", "sqlite3", "tkinter"]

build_exe_options = {
                        "include_files": included_files,
                        "packages": install_requires,
                        "include_msvcr": True
}

setup(
        name = "Reddit Paper",
        version = "1.0",
        author = "Cameron Gagnon",
        author_email = 'cameron.gagnon@gmail.com',
        url = "http://github.com/cameron-gagnon/reddit-paper",
        executables = executables,
        options = {"build_exe": build_exe_options}
)	
