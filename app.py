from time import sleep

import PySimpleGUI as sg

from documents import Documents
from pdf import PdfDocument

__APP_VERSION__ = "1.2"

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
    LIST_FILTER_ALL = 'list_filter_all'
    LIST_FILTER_AUDIO_ONLY = 'list_filter_audio_only'
    LIST_FILTER_PDF_ONLY = 'list_filter_pdf_only'
    LIST_AUDIO_PDF = 'list_audio_pdf'

    def __init__(self):
        self.__documents = None
        self.__player = Player()
        self.__pdf = None
        self.__main_window = None
        self.__progress_thread = None
        self.__is_playing = False
        self.__is_pause = False
        self.__DPI = 90

    def run(self):
        """Run application"""
        self.__load_documents()
        items = self.__documents.get_entries()
        self.__build_main_window(items)
        self.__ui_loop()
        self.__player.stop()
        self.__main_window.close()
        self.__stop_player()

    def __load_documents(self):
        self.__documents = Documents()
        self.__documents.load()

    def __build_main_window(self, items):
        sg.set_options(font=("Arial", 15))
        listbox = sg.Listbox(items, expand_x=True, expand_y=True)
        rd_all = sg.Radio('all', 'list_filter', key=App.LIST_FILTER_ALL, default=True,
                          enable_events=True)
        rd_audio_only = sg.Radio('audio only', 'list_filter', key=App.LIST_FILTER_AUDIO_ONLY,
                                 enable_events=True)
        rd_pdf_only = sg.Radio('PDF only', 'list_filter', key=App.LIST_FILTER_PDF_ONLY,
                               enable_events=True)
        rd_both = sg.Radio('audio & PDF', 'list_filter', key=App.LIST_AUDIO_PDF, enable_events=True)
        console = sg.Multiline("", disabled=True, autoscroll=True, write_only=False, size=(20, 5),
                               expand_x=True, expand_y=False)
        progress_bar = sg.ProgressBar(size=(10,15), expand_x=True, max_value=0)
        btn_run = sg.Button('Run', size=(10, 1), auto_size_button=False)
        btn_pause = sg.Button('Pause', disabled=True, size=(10, 1), auto_size_button=False)
        btn_stop = sg.Button('Stop', disabled=True, size=(10, 1), auto_size_button=False)
        btn_up = sg.Button('⬆️', key='Up', disabled=True, size=(5, 1), auto_size_button=False)
        btn_down = sg.Button('⬇️', key='Down', disabled=True, size=(5, 1), auto_size_button=False)
        btn_zoom_in = sg.Button('➕', key='ZoomIn', disabled=True, size=(5, 1), auto_size_button=False)
        btn_zoom_out = sg.Button('➖', key='ZoomOut', disabled=True, size=(5, 1), auto_size_button=False)

        win_size = sg.Window.get_screen_size()
        win_size = (win_size[0] - 10, win_size[1] - 70)

        column1 = sg.Column(layout=[
            [sg.Text('Pickup any song/tune from the list')],
            [sg.Text('Filter:'), rd_all, rd_both, rd_audio_only, rd_pdf_only],
            [listbox],
            [console],
            [progress_bar],
            [btn_run, btn_pause, btn_stop, sg.Push(), btn_zoom_in, btn_zoom_out,btn_up, btn_down]
        ], expand_x=True, expand_y=True, pad=(0, 0), vertical_alignment='top')

        img_pdf = sg.Image(size=(int(win_size[0]*0.7), win_size[1]), expand_x=True, expand_y=True)
        column2 = sg.Column(layout=[
            [img_pdf]
        ], expand_x=True, expand_y=True, pad=(0, 0))

        layout = [[column1, column2]]
        window = sg.Window(f'Music Practice Helper v {__APP_VERSION__}', layout,
                           return_keyboard_events=True,
                           location=(0, 0), size=win_size,
                           resizable=True, scaling=True,
                           auto_size_buttons=False, no_titlebar=False, finalize=True)

        window.rd_all = rd_all
        window.rd_audio_only = rd_audio_only
        window.rd_pdf_only = rd_pdf_only
        window.rd_both = rd_both
        window.listbox = listbox
        window.console = console
        window.btn_stop = btn_stop
        window.btn_pause = btn_pause
        window.btn_up = btn_up
        window.btn_down = btn_down
        window.btn_zoom_in = btn_zoom_in
        window.btn_zoom_out = btn_zoom_out
        window.progress_bar = progress_bar
        window.img_pdf = img_pdf
        window.frame1 = column1
        window.frame2 = column2
        self.__main_window = window
        return window

    def __show_pdf_page(self):
        pdf = self.__pdf
        if pdf is None:
            return
        img_pdf = self.__main_window.img_pdf
        img_x, img_y = img_pdf.Widget.winfo_width(), img_pdf.Widget.winfo_height()
        png = pdf.get_pdf_page((img_x, img_y))
        img_pdf.update(data=png.tobytes())

    def __load_pdf(self, file_path):
        self.__pdf = PdfDocument(file_path)
        self.__show_pdf_page()

    def __run_doc(self, doc_path):
        expanded_path = self.__documents.expand_path(doc_path)
        self.__load_pdf(expanded_path)

    def __run_process(self, code):
        self.__stop_player()
        if code not in self.__documents.get_items().keys():
            print('Cannot find document')
            return
        document = self.__documents.get_items()[code]

        if 'pdf' in document.keys():
            doc_path = document['pdf']
            self.__main_window.console.print('Opening PDF: {}'.format(doc_path))
            self.__run_doc(doc_path)
        else:
            self.__main_window.console.print('Cannot find PDF')

        if 'audio' in document.keys():
            self.__main_window.console.print('Preparation wait ({} seconds)...'.format(App.AUDIO_WAIT))
            self.__main_window.refresh()
            sleep(App.AUDIO_WAIT)
            audio_path = self.__documents.expand_path(document['audio'])
            self.__player.stop()
            self.__player.play(audio_path)
            self.__is_playing = True

    def __stop_player(self):
        self.__player.stop()
        self.__is_playing = False

    def __ui_loop(self):
        window = self.__main_window
        while True:
            try:
                event, values = window.read()
                if event == 'Run':
                    self.__run_item()
                elif event == 'Stop':
                    self.__stop_item()
                elif event == 'Pause':
                    self.__pause_item()
                elif event == 'Up' or event == 'Prior:112':
                    self.__next_page()
                elif event == 'Down' or event == 'Next:117':
                    self.__prev_page()
                elif event == 'ZoomIn' or event == 'KP_Add:86':
                    self.__zoom_in()
                elif event == 'ZoomOut' or event == 'KP_Subtract:82':
                    self.__zoom_out()
                elif event == 'UPDATE_PROGRESS':
                    self.__update_progress()
                elif event == App.LIST_FILTER_ALL:
                    self.__filter_documents()
                elif event == App.LIST_FILTER_AUDIO_ONLY:
                    self.__filter_documents(audio=True, pdf=False)
                elif event == App.LIST_FILTER_PDF_ONLY:
                    self.__filter_documents(audio=False, pdf=True)
                elif event == App.LIST_AUDIO_PDF:
                    self.__filter_documents(audio=True, pdf=True)
                elif event == sg.WIN_CLOSED:
                    break
            except Exception as ex:
                sg.popup(f'Error: {ex}')

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
        self.__stop_player()
        self.__is_playing = False
        console.print('Finished\n')
        window.progress_bar.update(0)
        self.__main_window.img_pdf.update(data=None)
        self.__update_ui_states()
        window.refresh()

    def __pause_item(self):
        window = self.__main_window
        console = window.console
        self.__player.pause()  # or unpause (if it's paused already)
        self.__is_pause = self.__player.is_paused()
        console.Update('Paused..\n' if self.__player.is_paused() else 'Playing..\n')
        self.__update_ui_states()

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
            window.btn_pause.update(disabled=False)
            self.__progress_thread = ThreadUpdater(window)
            window.start_thread(lambda: self.__progress_thread.run(), end_key='UPDATE_PROGRESS_END')
            self.__is_playing = True
            self.__update_ui_states()
        except Exception as ex:
            window.btn_stop.update(disabled=True)
            window.btn_pause.update(disabled=True)
            window.refresh()
            sg.popup(f'Error {ex}')

    def __update_ui_states(self):
        window = self.__main_window
        window.btn_stop.update(disabled=not self.__is_playing)
        window.btn_pause.update(disabled=not self.__is_playing)
        window.rd_all.update(disabled=self.__is_playing)
        window.rd_audio_only.update(disabled=self.__is_playing)
        window.rd_pdf_only.update(disabled=self.__is_playing)
        window.rd_both.update(disabled=self.__is_playing)
        window.btn_up.update(disabled=not self.__is_playing)
        window.btn_down.update(disabled=not self.__is_playing)
        window.btn_zoom_in.update(disabled=not self.__is_playing)
        window.btn_zoom_out.update(disabled=not self.__is_playing)
        window.refresh()

    def __filter_documents(self, audio=None, pdf=None):
        listbox = self.__main_window.listbox
        items = self.__documents.get_entries()
        result_items = []
        for item in items:
            if audio is not None:
                if audio != item.is_audio:
                    continue
            if pdf is not None:
                if pdf != item.is_pdf:
                    continue
            result_items.append(item)
        listbox.update(result_items)
        self.__main_window.refresh()

    def __next_page(self):
        pdf = self.__pdf
        if not pdf:
            return
        pdf.prev_page()
        self.__show_pdf_page()

    def __prev_page(self):
        pdf = self.__pdf
        if not pdf:
            return
        pdf.next_page()
        self.__show_pdf_page()

    def __zoom_in(self):
        pdf = self.__pdf
        if not pdf:
            return
        pdf.zoom_in()
        self.__show_pdf_page()

    def __zoom_out(self):
        pdf = self.__pdf
        if not pdf:
            return
        pdf.zoom_out()
        self.__show_pdf_page()
