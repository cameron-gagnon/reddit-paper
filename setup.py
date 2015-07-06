import sys
from cx_Freeze import setup, Executable

executables = [Executable("gui.py",  icon = "./images/rp_sq_48.ico", targetName = "Reddit Paper.exe")] #base = ("Win32GUI" if sys.platform == 'win32' else None),]
included_files = ["./images", "redditpaper.py", "detools",
		          "C:\\Python34\\Lib\\site-packages\\praw\\praw.ini",
                  "cacert.pem"]

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
