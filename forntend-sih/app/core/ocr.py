from typing import Optional, Tuple, List
import numpy as np

def is_tesseract_available():
    try:
        import pytesseract  # noqa
        return True
    except Exception:
        return False

def image_to_text(image_bytes: bytes) -> Tuple[str, List[Tuple[str, Tuple[int,int,int,int]]]]:
    """
    Returns (text, words_with_boxes) where words_with_boxes is a list of (word, (x,y,w,h)).
    """
    try:
        from PIL import Image
        import pytesseract
        import io
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        words = []
        for i in range(len(data['text'])):
            word = data['text'][i]
            if not word.strip():
                continue
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            words.append((word, (x,y,w,h)))
        full_text = " ".join([w for w,_ in words])
        return full_text, words
    except Exception as e:
        return f"", []
