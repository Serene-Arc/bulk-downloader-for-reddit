from os import path

class Store:
    def __init__(self,directory=None):
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

    def __call__(self):
        return self.list

    def add(self, filehash):
        self.list.append(filehash)
        if self.directory:
            with open(self.directory, 'a') as f:
                f.write("{filehash}\n".format(filehash=filehash))