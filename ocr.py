from spire.pdf import PdfDocument
import pytesseract
import cv2
import os
from transliterate import translit
import os


# вспомогательная функция-конвертор из pdf в png
def pdf_to_img(pdf_path):
    doc = PdfDocument()
    doc.LoadFromFile(pdf_path)
    dir_path = os.path.dirname(pdf_path)
    # get the file name
    file_name = os.path.basename(pdf_path)
    # get the file name without extension
    file_name_no_ext = os.path.splitext(file_name)[0]
    # make a new directory
    dir_path = os.path.join(dir_path, file_name_no_ext)
    dir_path = translit(dir_path, "ru", reversed=True)
    os.makedirs(dir_path, exist_ok=True)
    img_paths = []
    for i in range(doc.Pages.Count):
        with doc.SaveAsImage(i) as image:
            img_name = os.path.join(dir_path, f"{i}.png")
            image.Save(img_name)
            img_paths.append(img_name)
    doc.Close()
    return img_paths


# вспомогательная функция распознание текста
def img_to_text(img_path, tes_path):
    img = cv2.imread(img_path)
    if os.name=='nt':
        pytesseract.pytesseract.tesseract_cmd = tes_path
    text = pytesseract.image_to_string(img, lang="rus+eng")
    # delete img
    return pytesseract.image_to_string(img, lang="rus+eng")
