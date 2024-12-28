import fitz

class PdfDocument:
    PDF_DPI = 72
    DEF_PDF_VIEW_MARGIN = 0.05

    def __init__(self, file_path):
        self.__pdf = fitz.open(file_path)
        self.__page_num = 0
        self.__margin = PdfDocument.DEF_PDF_VIEW_MARGIN

    def next_page(self):
        if self.__page_num + 1 < len(self.__pdf):
            self.__page_num += 1

    def prev_page(self):
        if self.__page_num - 1 >= 0:
            self.__page_num -= 1

    def zoom_in(self):
        self.__margin = min(0.2, self.__margin + 0.01)

    def zoom_out(self):
        self.__margin = max(0.0, self.__margin - 0.01)

    def get_pdf_page(self, view_size_px):
        if self.__page_num not in range(len(self.__pdf)):
            return None

        page = self.__pdf[self.__page_num]
        box = page.mediabox
        pdf_x, pdf_y = box[2:4]
        margin = self.__margin * pdf_x
        clip = (margin, margin, pdf_x - margin, pdf_y - margin)
        pdf_view_height = pdf_y - 2 * margin

        img_x, img_y = view_size_px
        png = page.get_pixmap(dpi=int(PdfDocument.PDF_DPI * img_y / pdf_view_height), alpha=False, clip=clip)
        return png
