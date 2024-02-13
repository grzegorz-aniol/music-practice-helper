import json
import os

class DocumentEntry:

    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __str__(self):
        return self.name


class Documents:
    """
    Store for document locations. Each document entry may consist:
     * pdf path
     * audio file path
     * or both paths
    Document locations are stored in local json file 'documents.json'
    """
    FILE_NAME = 'documents.json'

    def __init__(self):
        self.documents = None
        self.tools = {}
        self.paths = {}

    def load(self):
        locations = ['.', os.getenv('HOME')+'/.music-practice']
        for location in locations:
            file_path = f'{location}/{Documents.FILE_NAME}'
            if os.path.isfile(file_path):
                with open(file_path) as input_file:
                    self.documents = json.load(input_file)
                break

        if self.documents is None:
            raise Exception(f'Cannot find database file {Documents.FILE_NAME}')

        self.tools = self.documents['tools']
        self.paths = self.documents['paths']

    def get_codes_and_names(self):
        return [DocumentEntry(key, self.documents['items'][key]['name']) for key in self.documents['items'].keys()]

    def expand_path(self, path):
        res = path
        for key, value in self.paths.items():
            if key in path:
                res = res.replace(key, value)
                print('replaced', res)
        return res

    def get_items(self):
        return self.documents['items']

    def get_tools(self):
        return self.tools

