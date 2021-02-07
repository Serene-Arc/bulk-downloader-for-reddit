#!C:\Users\Ali\AppData\Local\Programs\Python\Python36\python.exe

## python setup.py build
import sys
from cx_Freeze import setup, Executable
from bulkredditdownloader.__main__ import __version__

options = {
    "build_exe": {
        "packages":[
            "idna", "praw", "requests", "multiprocessing"
        ]
    }
}

if sys.platform == "win32":
    executables = [Executable(
        "script.py", 
        targetName="bulk-downloader-for-reddit.exe",
        shortcutName="Bulk Downloader for Reddit",
        shortcutDir="DesktopFolder"
    )]

elif sys.platform == "linux":
    executables = [Executable(
        "script.py", 
        targetName="bulk-downloader-for-reddit",
        shortcutName="Bulk Downloader for Reddit",
        shortcutDir="DesktopFolder"
    )]

setup(
    name = "Bulk Downloader for Reddit",
    version = __version__,
    description = "Bulk Downloader for Reddit",
    author = "Ali Parlakci",
    author_email="parlakciali@gmail.com",
    url="https://github.com/aliparlakci/bulk-downloader-for-reddit",
    classifiers=(
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
            "Natural Language :: English",
            "Environment :: Console",
            "Operating System :: OS Independent",
    ),
    executables = executables,
    options = options
)


