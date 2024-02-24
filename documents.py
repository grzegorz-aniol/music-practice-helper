import json
import os


class DocumentEntry:

    def __init__(self, code, name, is_audio=False, is_pdf=False):
        self.code = code
        self.name = name
        self.is_audio = is_audio
        self.is_pdf = is_pdf

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
        locations = ['.', os.getenv('HOME') + '/.music-practice']
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

    def get_entries(self):
        output = []
        for key in self.documents['items'].keys():
            doc = self.documents['items'][key]
            is_audio = 'audio' in doc
            is_pdf = 'pdf' in doc
            is_audio_only = ' (audio only)' if is_audio and not is_pdf else ''
            is_pdf_only = ' (pdf only)' if is_pdf and not is_audio else ''
            output.append(DocumentEntry(key, name=f"{doc['name']}{is_audio_only}{is_pdf_only}",
                          is_audio=is_audio, is_pdf=is_pdf))
        return sorted(output, key=lambda item: item.name)

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
