import os
from os import getcwd

import PySimpleGUI as sg


class EntryEditor:
    field_name = "FIELD_NAME"
    field_pdf = "FIELD_PDF"
    field_audio = "FIELD_AUDIO"
    field_alto = "FIELD_ALTO"
    field_tenor = "FIELD_TENOR"
    initial_folder = getcwd()

    def __init__(self):
        sg.set_options(font='Arial 14')
        self.pdf_browser = sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),), initial_folder=EntryEditor.initial_folder)
        self.audio_browser = sg.FileBrowse(file_types=(("Mp3 Files", "*.mp3"),), initial_folder=EntryEditor.initial_folder)
        self.layout = [
            [sg.Text('Name'), sg.InputText('', key=EntryEditor.field_name)],
            [sg.Text('PDF'), sg.InputText('', key=EntryEditor.field_pdf), self.pdf_browser],
            [sg.Text('Audio'), sg.InputText('', key=EntryEditor.field_audio), self.audio_browser],
            [sg.Text('Tags'), sg.Checkbox('Alto', key=EntryEditor.field_alto), sg.Checkbox('Tenor', key=EntryEditor.field_tenor)],
            [sg.Button('Save'), sg.Button('Cancel')]
        ]

    def add_new_entry(self):
        window = sg.Window('Add New Entry', self.layout, modal=True, finalize=True, location=(None, None))
        event, values = window.read()
        if event == 'Save':
            self._validate(values)
            entry_key = values[EntryEditor.field_name].lower().replace(' ', '_')
            tags = []
            if values[EntryEditor.field_alto]:
                tags.append('Alto')
            if values[EntryEditor.field_tenor]:
                tags.append('Tenor')
            new_entry = {
                'name': values[EntryEditor.field_name],
                'pdf': values[EntryEditor.field_pdf] or '',
                'audio': values[EntryEditor.field_audio] or '',
                'tags': [tag.lower().strip() for tag in tags]
            }
            EntryEditor.initial_folder = os.path.dirname(
                values[EntryEditor.field_pdf] or values[EntryEditor.field_audio])
            window.close()
            return entry_key, new_entry
        window.close()

    def edit_entry(self, entry_key, entry_value):
        window = sg.Window('Edit Entry', self.layout, modal=True, finalize=True, location=(None, None))
        window[EntryEditor.field_name].update(value=entry_value['name'] if 'name' in entry_value else '')
        window[EntryEditor.field_pdf].update(value=entry_value['pdf'] if 'pdf' in entry_value else '')
        window[EntryEditor.field_audio].update(value=entry_value['audio'] if 'audio' in entry_value else '')
        if 'tags' in entry_value:
            window[EntryEditor.field_alto].update(value='alto' in entry_value['tags'])
            window[EntryEditor.field_tenor].update(value='tenor' in entry_value['tags'])
        window.refresh()
        event, values = window.read()
        if event == 'Save':
            self._validate(values)
            tags = []
            if values[EntryEditor.field_alto]:
                tags.append('Alto')
            if values[EntryEditor.field_tenor]:
                tags.append('Tenor')
            entry_value = {
                'name': values[EntryEditor.field_name],
                'pdf': values[EntryEditor.field_pdf] or '',
                'audio': values[EntryEditor.field_audio] or '',
                'tags': [tag.lower().strip() for tag in tags]
            }
            EntryEditor.initial_folder = os.path.dirname(
                values[EntryEditor.field_pdf] or values[EntryEditor.field_audio])
            window.close()
            return entry_key, entry_value
        window.close()

    def _validate(self, values):
        if len(values[EntryEditor.field_name]) == 0:
            raise Exception('Name is required')