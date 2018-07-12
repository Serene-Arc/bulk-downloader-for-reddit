#!C:\Users\Ali\AppData\Local\Programs\Python\Python36\python.exe

## python setup.py build
import sys
from cx_Freeze import setup, Executable

setup(
        name = "Bulk Downloader for Reddit",
        version = "1.1.0",
        description = "Bulk Downloader for Reddit",
        author = "Ali Parlakci",
        executables = [Executable("script.py")],
        options = {"build_exe": {"packages":["idna","imgurpython", "praw", "requests"]}})


