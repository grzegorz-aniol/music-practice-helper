import fitz

class PdfDocument:
    PDF_DPI = 72
    DEF_PDF_VIEW_MARGIN = 0.05

    def __init__(self, file_path):
        self.__pdf = fitz.open(file_path)
        self.__page_num = 0
        self.__margin = PdfDocument.DEF_PDF_VIEW_MARGIN

    def __len__(self):
        return self.__pdf.page_count

    def current_page_num(self):
        return self.__page_num

    def next_page(self, step=1):
        self.__page_num = min(self.__page_num + step, self.__pdf.page_count - step)

    def prev_page(self, step=1):
        self.__page_num = max(self.__page_num - step, 0)

    def go_to_page(self, page_num, step=1):
        self.__page_num = min(max(page_num, 0), self.__pdf.page_count - step)

    def zoom_in(self):
        self.__margin = min(0.2, self.__margin + 0.01)

    def zoom_out(self):
        self.__margin = max(0.0, self.__margin - 0.01)

    def get_pdf_page(self, view_size_px, page_offset=0):
        if self.__page_num + page_offset not in range(self.__pdf.page_count):
            return None

        page = self.__pdf[self.__page_num + page_offset]
        box = page.mediabox
        pdf_x, pdf_y = box[2:4]
        margin = self.__margin * pdf_x
        clip = (margin, margin, pdf_x - margin, pdf_y - margin)
        pdf_view_height = pdf_y - 2 * margin

        img_x, img_y = view_size_px
        png = page.get_pixmap(dpi=int(PdfDocument.PDF_DPI * img_y / pdf_view_height), alpha=False, clip=clip)
        return png
