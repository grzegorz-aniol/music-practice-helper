import subprocess
import PySimpleGUI as sg
from documents import Documents
from time import sleep

__APP_VERSION__ = "1.0"

from player import Player


class ThreadUpdater:
    """
        Thread that sends in regular periods notification to update progress bar
    """

    def __init__(self, window):
        self.started = False
        self.terminated = False
        self.window = window

    def stop(self, wait_to_finish=True):
        self.terminated = True
        if not wait_to_finish:
            return
        while self.started:
            sleep(1)

    def run(self):
        while not self.terminated:
            self.window.write_event_value('UPDATE_PROGRESS', value=None)
            sleep(1)
        self.started = False


class App:
    """
    Main application
    """

    AUDIO_WAIT = 3

    def __init__(self):
        self.__documents = None
        self.__opened_processes = []
        self.__player = Player()
        self.__main_window = None
        self.__progress_thread = None

    def run(self):
        """Run application"""
        self.__documents = Documents()
        self.__documents.load()
        items = self.__documents.get_codes_and_names()
        self.__build_main_window(items)
        self.__ui_loop()
        self.__player.stop()
        self.__main_window.close()
        self.__close_processes()

    def __build_main_window(self, items):
        sg.set_options(font=("Arial", 15))
        listbox = sg.Listbox(items, size=(50, 20), expand_x=True, expand_y=True)
        console = sg.Multiline("", disabled=True, autoscroll=True, write_only=False, size=(50, 5), expand_x=True,
                               expand_y=True)
        progress_bar = sg.ProgressBar(size=(50, 10), max_value=0)
        btn_stop = sg.Button('Stop', disabled=True)
        layout = [[sg.Text('Pickup any song/tune from the list')],
                  [listbox],
                  [console],
                  [progress_bar],
                  [sg.Button('Run'), btn_stop]]
        window = sg.Window(f'Music Practice Helper v {__APP_VERSION__}', layout, resizable=True, scaling=True)
        window.listbox = listbox
        window.console = console
        window.btn_stop = btn_stop
        window.progress_bar = progress_bar
        self.__main_window = window
        return window

    def __run_doc(self, tool, path):
        return subprocess.Popen([tool['path'], self.__documents.expand_path(path)])

    def __run_process(self, code):
        self.__close_processes()
        if code not in self.__documents.get_items().keys():
            print('Cannot find document')
            return
        document = self.__documents.get_items()[code]
        self.__opened_processes = []
        if 'pdf' in document.keys():
            self.__opened_processes.append(self.__run_doc(self.__documents.get_tools()['pdf'], document['pdf']))
        if 'audio' in document.keys():
            self.__main_window.console.print('Preparation wait ({} seconds)...'.format(App.AUDIO_WAIT))
            self.__main_window.refresh()
            sleep(App.AUDIO_WAIT)
            audio_path = self.__documents.expand_path(document['audio'])
            self.__player.stop()
            self.__player.play(audio_path)

    def __close_processes(self):
        for pr in self.__opened_processes:
            pr.terminate()
        self.__opened_processes = []
        self.__player.stop()

    def __ui_loop(self):
        window = self.__main_window
        while True:
            event, values = window.read()
            if event == 'Run':
                self.__run_item()
            elif event == 'Stop':
                self.__stop_item()
            elif event == 'UPDATE_PROGRESS':
                self.__update_progress()
            elif event == sg.WIN_CLOSED:
                break

    def __update_progress(self):
        position = self.__player.get_pos()
        max_position = self.__player.get_len()
        if position is not None:
            self.__main_window.progress_bar.update(position, max=max_position)

    def __stop_item(self):
        if self.__progress_thread:
            self.__progress_thread.stop()
        self.__progress_thread = None
        window = self.__main_window
        console = window.console
        console.Update('Stopping...\n')
        window.refresh()
        self.__close_processes()
        console.print('Done.\n')
        window.btn_stop.update(disabled=True)
        window.progress_bar.update(0)
        window.refresh()

    def __run_item(self):
        window = self.__main_window
        console = window.console
        selected = window.listbox.get()
        if selected is None or len(selected) == 0:
            sg.popup('Nothing is selected in the list')
            return
        try:
            code = selected[0].code
            name = selected[0].name
            console.Update(f'Running {name}...\n')
            window.refresh()
            self.__run_process(code)
            console.print('In progress...')
            audio_len = self.__player.get_len()
            window.progress_bar.update(max=audio_len)
            window.btn_stop.update(disabled=False)
            window.refresh()
            self.__progress_thread = ThreadUpdater(window)
            window.start_thread(lambda: self.__progress_thread.run(), end_key='UPDATE_PROGRESS_END')
        except Exception as ex:
            window.btn_stop.update(disabled=True)
            window.refresh()
            sg.popup(f'Error {ex}')
