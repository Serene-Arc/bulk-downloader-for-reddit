#!C:\Users\Ali\AppData\Local\Programs\Python\Python36\python.exe
import sys
from cx_Freeze import setup, Executable

setup(
    name = "Bulk Downloader for Reddit",
    version = "1.0.1",
    description = "Bulk Downloader for Reddit",
    executables = [Executable("script.py")],
    options = {"build_exe": {"packages":["idna","imgurpython", "praw", "requests"]}})

