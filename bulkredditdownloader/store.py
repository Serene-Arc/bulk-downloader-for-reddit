#!/usr/bin/env python3

from os import path


class Store:
    def __init__(self, directory: str = None):
        self.directory = directory
        if self.directory:
            if path.exists(directory):
                with open(directory, 'r') as f:
                    self.list = f.read().split("\n")
            else:
                with open(self.directory, 'a'):
                    pass
                self.list = []
        else:
            self.list = []

    def __call__(self) -> list:
        return self.list

    def add(self, data: dict):
        self.list.append(data)
        if self.directory:
            with open(self.directory, 'a') as f:
                f.write("{data}\n".format(data=data))
