from time import sleep

import PySimpleGUI as sg

from . import __version__
from .documents import Documents
from .entry_editor import EntryEditor
from .pdf import PdfDocument
from .player import Player


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


class Application:
    """
    Main application
    """

    LIST_ANY = "TAG_ANY"
    LIST_ALTO = "TAG_ALTO"
    LIST_TENOR = "TAG_TENOR"
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
        # sg.theme("Default 1")
        sg.set_options(font='Arial 14')
        listbox = sg.Listbox(items, expand_x=True, expand_y=True)
        rd_all = sg.Radio('all', 'list_filter', key=Application.LIST_FILTER_ALL, default=True,
                          enable_events=True)
        rd_audio_only = sg.Radio('audio only', 'list_filter', key=Application.LIST_FILTER_AUDIO_ONLY,
                                 enable_events=True)
        rd_pdf_only = sg.Radio('PDF only', 'list_filter', key=Application.LIST_FILTER_PDF_ONLY,
                               enable_events=True)
        rd_both = sg.Radio('audio & PDF', 'list_filter', key=Application.LIST_AUDIO_PDF, enable_events=True)
        rd_any_tag = sg.Radio('Any', 'tag_filter', key=Application.LIST_ANY, default=True, enable_events=True)
        rd_alto = sg.Radio('Alto', 'tag_filter', key=Application.LIST_ALTO, enable_events=True)
        rd_tenor = sg.Radio('Tenor', 'tag_filter', key=Application.LIST_TENOR, enable_events=True)
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
        btn_edit = sg.Button('Edit', size=(10, 1), auto_size_button=False)
        btn_add_new = sg.Button('Add', size=(10, 1), auto_size_button=False)


        win_size = sg.Window.get_screen_size()
        win_size = (win_size[0] - 30, win_size[1] - 70)

        controls_column = sg.Column(layout=[
            [sg.Text('Pickup any song/tune from the list')],
            [sg.Text('Filter:'), rd_all, rd_both, rd_audio_only, rd_pdf_only],
            [sg.Text('Tags:'), rd_any_tag, rd_alto, rd_tenor],
            [btn_add_new, btn_edit],
            [listbox],
            [console],
            [progress_bar],
            [btn_run, btn_pause, btn_stop, sg.Push(), btn_zoom_in, btn_zoom_out, btn_up, btn_down]
        ], expand_x=True, expand_y=True, pad=(0, 0), vertical_alignment='top')

        pdf_width = int(0.3 * win_size[0])
        img_pdf1 = sg.Image(size=(pdf_width, win_size[1]), expand_x=True, expand_y=True)
        img_pdf2 = sg.Image(size=(pdf_width, win_size[1]), expand_x=True, expand_y=True)
        pdfs_column = sg.Column(layout=[
            [img_pdf1, img_pdf2]
        ], expand_x=True, expand_y=True, pad=(0, 0))

        layout = [[controls_column, sg.Push(), pdfs_column]]
        window = sg.Window(f'Music Practice Helper v {__version__}', layout,
                           return_keyboard_events=True,
                           location=(0, 0), size=win_size,
                           resizable=True, scaling=True,
                           auto_size_buttons=False, no_titlebar=False, finalize=True)

        window.rd_all = rd_all
        window.rd_audio_only = rd_audio_only
        window.rd_pdf_only = rd_pdf_only
        window.rd_both = rd_both
        window.rd_any = rd_any_tag
        window.rd_alto = rd_alto
        window.rd_tenor = rd_tenor
        window.listbox = listbox
        window.console = console
        window.btn_stop = btn_stop
        window.btn_pause = btn_pause
        window.btn_up = btn_up
        window.btn_down = btn_down
        window.btn_zoom_in = btn_zoom_in
        window.btn_zoom_out = btn_zoom_out
        window.btn_edit = btn_edit
        window.btn_add_new = btn_add_new
        window.progress_bar = progress_bar
        window.img_pdf1 = img_pdf1
        window.img_pdf2 = img_pdf2
        window.frame1 = controls_column
        window.frame2 = pdfs_column
        self.__main_window = window


        return window

    def __show_pdf_pages(self):
        pdf = self.__pdf
        if pdf is None:
            return
        img_pdf1 = self.__main_window.img_pdf1
        img_pdf2 = self.__main_window.img_pdf2
        win_width, win_height = self.__main_window.size
        panel_width, panel_height = self.__main_window.listbox.get_size()
        win_width = max(10, win_width - panel_width - 30)
        win_height = max(10, win_height - 30)
        pdf_width = int(0.5 * win_width)
        pdf_height = win_height
        # crop PDF width and height to keep A4 page ratio
        pdf_height = min(pdf_height, int(pdf_width * 1.414))
        pdf_width = min(pdf_width, int(pdf_height / 1.414))
        img_x, img_y = pdf_width, pdf_height
        png = pdf.get_pdf_page((img_x, img_y))
        img_pdf1.update(data=png.tobytes())
        if (pdf.current_page_num() + 1) < len(pdf):
            png = pdf.get_pdf_page((img_x, img_y), page_offset=1)
            if png is not None:
                img_pdf2.update(data=png.tobytes())

    def __load_pdf(self, file_path: str, start_page_num: int):
        self.__pdf = PdfDocument(file_path)
        self.__pdf.go_to_page(start_page_num)
        self.__show_pdf_pages()

    def __run_doc(self, doc_path, start_page_num: int):
        expanded_path = self.__documents.expand_path(doc_path)
        self.__load_pdf(expanded_path, start_page_num)

    def __run_process(self, code):
        self.__stop_player()
        if code not in self.__documents.get_items().keys():
            print('Cannot find document')
            return
        document = self.__documents.get_items()[code]
        self.__main_window.img_pdf1.update(data=None)
        self.__main_window.img_pdf2.update(data=None)

        if 'pdf' in document.keys() and len(document['pdf'])>0:
            doc_path = document['pdf']
            start_page_num = document['page_num'] if 'page_num' in document else 0
            self.__main_window.console.print('Opening PDF: {}'.format(doc_path))
            self.__run_doc(doc_path, start_page_num)

        if 'audio' in document.keys() and len(document['audio'])>0:
            self.__main_window.console.print('Preparation wait ({} seconds)...'.format(Application.AUDIO_WAIT))
            self.__main_window.refresh()
            sleep(Application.AUDIO_WAIT)
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
                    self.__prev_page()
                elif event == 'Down' or event == 'Next:117':
                    self.__next_page()
                elif event == 'ZoomIn' or event == 'KP_Add:86':
                    self.__next_page()
                elif event == 'ZoomOut' or event == 'KP_Subtract:82':
                    self.__prev_page()
                elif event == 'KP_Divide:106':
                    self.__zoom_in()
                elif event == 'KP_Multiply:63':
                    self.__zoom_out()
                elif event == 'UPDATE_PROGRESS':
                    self.__update_progress()
                elif event == Application.LIST_FILTER_ALL:
                    self.__filter_documents()
                elif event == Application.LIST_FILTER_AUDIO_ONLY:
                    self.__filter_documents()
                elif event == Application.LIST_FILTER_PDF_ONLY:
                    self.__filter_documents()
                elif event == Application.LIST_AUDIO_PDF:
                    self.__filter_documents()
                elif event == Application.LIST_ANY:
                    self.__filter_documents()
                elif event == Application.LIST_ALTO:
                    self.__filter_documents()
                elif event == Application.LIST_TENOR:
                    self.__filter_documents()
                elif event == 'Edit':
                    self.__edit_entry()
                elif event == 'Add':
                    self.__add_entry()
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

        # win_size = sg.Window.get_screen_size()
        # win_size = (win_size[0] - 10, win_size[1] - 70)
        # pdf_width = int(0.3 * win_size[0])
        # empty_image = Image.new('RGB', (pdf_width, win_size[1]), (255, 255, 255))
        # empty_image_bytes = io.BytesIO()
        # empty_image.save(empty_image_bytes, format='PNG')
        # empty_image_data = empty_image_bytes.getvalue()

        self.__main_window.img_pdf1.update(data=None)
        self.__main_window.img_pdf2.update(data=None)
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
        selected = self.__main_window.listbox.get()
        is_selected = (selected and len(selected) > 0)
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
        window.btn_edit.update(disabled=not is_selected or self.__is_playing)
        window.btn_add_new.update(disabled=self.__is_playing)
        window.refresh()

    def __filter_documents(self):
        window = self.__main_window
        tags = []
        audio = None
        pdf = None
        if window.rd_alto.get():
            tags.append('alto')
        if window.rd_tenor.get():
            tags.append('tenor')

        if window.rd_audio_only.get():
            audio=True
            pdf=False
        elif window.rd_pdf_only.get():
            audio=False
            pdf=True
        elif window.rd_both.get():
            audio=True
            pdf=True

        listbox = window.listbox
        items = self.__documents.get_entries()
        result_items = []
        for item in items:
            if tags is not None and len(tags) > 0:
                if not any(tag.lower() in item.tags for tag in tags):
                    continue
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
        pdf.next_page(step=2)
        self.__show_pdf_pages()

    def __prev_page(self):
        pdf = self.__pdf
        if not pdf:
            return
        pdf.prev_page(step=2)
        self.__show_pdf_pages()

    def __zoom_in(self):
        pdf = self.__pdf
        if not pdf:
            return
        pdf.zoom_in()
        self.__show_pdf_pages()

    def __zoom_out(self):
        pdf = self.__pdf
        if not pdf:
            return
        pdf.zoom_out()
        self.__show_pdf_pages()


    def __add_entry(self):
        edit_window = EntryEditor()
        result = edit_window.add_new_entry()
        if result is not None:
            code, entry = result
            self.__documents.update_entry(code, entry)
            self.__main_window.listbox.update(self.__documents.get_entries())


    def __edit_entry(self):
        current_index = self.__main_window.listbox.get_indexes()[0]
        selected = self.__main_window.listbox.get()
        if selected is None or len(selected) == 0:
            sg.popup('Nothing is selected in the list')
            return
        code = selected[0].code
        if code not in self.__documents.get_items().keys():
            print('Cannot find document')
            return
        entry = self.__documents.get_items()[code]
        edit_window = EntryEditor()
        result = edit_window.edit_entry(code, entry)
        if result is not None:
            self.__documents.update_entry(code, result[1])
            self.__main_window.listbox.update(self.__documents.get_entries())
            self.__main_window.listbox.update(set_to_index=[current_index])
