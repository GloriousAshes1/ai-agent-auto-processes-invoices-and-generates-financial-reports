from paddleocr import PaddleOCR, PPStructureV3

class OCR_Module(object):
    def __init__(self):
       self.ocr = PaddleOCR(use_textline_orientation=True,
                            text_detection_model_name='PP-OCRv5_server_det',
                            text_recognition_model_name='PP-OCRv5_server_rec',
                            lang='en')

    def ocr(self, image_path):
        result = self.ocr.predict(image_path)
        return result


