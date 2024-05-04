from spire.pdf import PdfDocument
import pytesseract
import cv2
import os
from transliterate import translit
import os
from pdf2image import convert_from_path

# вспомогательная функция-конвертор из pdf в png
# def pdf_to_img(pdf_path):
#     doc = PdfDocument()
#     doc.LoadFromFile(pdf_path)
#     dir_path = os.path.dirname(pdf_path)
#     # get the file name
#     file_name = os.path.basename(pdf_path)
#     # get the file name without extension
#     file_name_no_ext = os.path.splitext(file_name)[0]
#     # make a new directory
#     dir_path = os.path.join(dir_path, file_name_no_ext)
#     dir_path = translit(dir_path, "ru", reversed=True)
#     os.makedirs(dir_path, exist_ok=True)
#     img_paths = []
#     for i in range(doc.Pages.Count):
#         with doc.SaveAsImage(i) as image:
#             img_name = os.path.join(dir_path, f"{i}.png")
#             image.Save(img_name)
#             img_paths.append(img_name)
#     doc.Close()
#     return img_paths


def pdf_to_img(pdf_path):
    dir_path = os.path.dirname(pdf_path)
    #     # get the file name
    file_name = os.path.basename(pdf_path)
    #     # get the file name without extension
    file_name_no_ext = os.path.splitext(file_name)[0]
    images = convert_from_path(
        pdf_path,
        poppler_path=r"C:\\Users\\Davron\\Desktop\\poppler-24.02.0\\Library\\bin",  # put your path here
    )
    dir_path = os.path.join(dir_path, file_name_no_ext)
    dir_path = translit(dir_path, "ru", reversed=True)
    os.makedirs(dir_path, exist_ok=True)
    img_paths = []
    for i, image in enumerate(images):
        img_name = os.path.join(dir_path, f"{i}.png")
        image.save(img_name, "PNG")
        img_paths.append(img_name)

    return img_paths


# вспомогательная функция распознание текста
# def img_to_text(img_path, tes_path):
#     img = cv2.imread(img_path)
#     if os.name == "nt":
#         pytesseract.pytesseract.tesseract_cmd = tes_path
#     text = pytesseract.image_to_string(img, lang="rus+eng")
#     # delete img
#     return pytesseract.image_to_string(img, lang="rus+eng")


def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print("Texts:")
    # for text in texts:
    #     output_text += text.description
    # print(f'\n"{text.description}"')

    # vertices = [
    #     f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
    # ]

    # print("bounds: {}".format(",".join(vertices)))
    items = []
    lines = {}
    for text in response.text_annotations[1:]:
        top_x_axis = text.bounding_poly.vertices[0].x
        top_y_axis = text.bounding_poly.vertices[0].y
        bottom_y_axis = text.bounding_poly.vertices[3].y

        if top_y_axis not in lines:
            lines[top_y_axis] = [(top_y_axis, bottom_y_axis), []]

        for s_top_y_axis, s_item in lines.items():
            if top_y_axis < s_item[0][1]:
                lines[s_top_y_axis][1].append((top_x_axis, text.description))
                break

    for _, item in lines.items():
        if item[1]:
            words = sorted(item[1], key=lambda t: t[0])
            items.append((item[0], " ".join([word for _, word in words]), words))

    output_text = " ".join([item[1] for item in items])
    print(output_text)
    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

    return output_text
