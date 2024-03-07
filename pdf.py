import fitz


class PdfDocument:
    PDF_DPI = 72
    PDF_VIEW_MARGIN = 0.05

    def __init__(self, file_path):
        self.__pdf = fitz.open(file_path)
        self.__page_num = 0

    def next_page(self):
        if self.__page_num + 1 < len(self.__pdf):
            self.__page_num += 1

    def prev_page(self):
        if self.__page_num - 1 >= 0:
            self.__page_num -= 1

    def get_pdf_page(self, view_size_px):
        if not self.__page_num in range(len(self.__pdf)):
            return None

        # img_pdf = self.__main_window.img_pdf
        # if page_no < 0 or page_no >= len(pdf_doc):
        #     img_pdf.update(date=None)
        #     return
        #
        page = self.__pdf[self.__page_num]
        box = page.mediabox
        pdf_x, pdf_y = box[2:4]
        margin = PdfDocument.PDF_VIEW_MARGIN * pdf_x
        clip = (margin, margin, pdf_x - margin, pdf_y - margin)
        pdf_view_height = pdf_y - 2 * margin

        img_x, img_y = view_size_px # img_pdf.Widget.winfo_width(), img_pdf.Widget.winfo_height()
        png = page.get_pixmap(dpi=int(PdfDocument.PDF_DPI * img_y / pdf_view_height), alpha=False, clip=clip)
        return png
