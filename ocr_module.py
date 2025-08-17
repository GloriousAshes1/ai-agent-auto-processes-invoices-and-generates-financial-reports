from paddleocr import PaddleOCR
import os

class OCR_Module(object):
    def __init__(self):
        self.ocr_engine = PaddleOCR(
            use_textline_orientation=True,
            text_detection_model_name='PP-OCRv5_server_det',
            text_recognition_model_name='PP-OCRv5_server_rec',
        )

    def get_text(self, image_path, save_path_txt=None):
        save_path_img = "./ocr_result/ocr_img"
        result = self.ocr_engine.ocr(image_path)

        # Kiểm tra xem có kết quả không
        if not result or not isinstance(result, list):
            return ""

        # Lấy danh sách văn bản đã nhận dạng
        rec_texts = result[0].get("rec_texts", [])

        # Gộp các dòng lại thành 1 chuỗi plain text
        plain_text = "\n".join(rec_texts)

        if save_path_img:
            result[0].save_to_img(save_path_img)

        # Nếu có yêu cầu lưu file
        if save_path_txt:
            with open(save_path_txt, 'w', encoding='utf-8') as f:
                texts = result[0]["rec_texts"]
                scores = result[0]["rec_scores"]
                boxes = result[0]["rec_boxes"]

                for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
                    line = f"{i + 1:02}. Text: {text} | Score: {score:.2f} | Box: {box.tolist()}\n"
                    f.write(line)
        # Trả về plain_text để NLP_Module xử lý tiếp
        return plain_text
