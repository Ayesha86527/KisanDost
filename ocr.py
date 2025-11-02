# app/ocr.py
"""
PaddleOCR helper.
Provides run_ocr(image_path) -> str
"""

from paddleocr import PaddleOCR
from pathlib import Path
from app.config import OCR_LANG, OUTPUT_DIRS

# Ensure OCR output dir exists (already created in config, keep safe)
Path(OUTPUT_DIRS["ocr_outputs"]).mkdir(parents=True, exist_ok=True)

# Initialize PaddleOCR model once
print(f"[OCR] Initializing PaddleOCR (lang={OCR_LANG})")
ocr = PaddleOCR(lang=OCR_LANG, use_angle_cls=True, show_log=False)


def run_ocr(image_path: str, save_output: bool = True) -> str:
    """
    Run OCR on image_path and return extracted text (as a single string).
    Saves output to outputs/ocr if save_output=True.
    """
    try:
        print(f"[OCR] Running OCR on: {image_path}")
        result = ocr.ocr(str(image_path), cls=True)

        extracted = []
        # result is a list of lines; handle possible structures
        for line in result:
            # each line may be list of word boxes
            if isinstance(line, list):
                for word_info in line:
                    # word_info: [box, (text, confidence)]
                    if isinstance(word_info, (list, tuple)) and len(word_info) > 1:
                        text = str(word_info[1][0]).strip()
                        if text:
                            extracted.append(text)
            elif isinstance(line, dict):
                # just in case
                txt = line.get("text", "").strip()
                if txt:
                    extracted.append(txt)

        final_text = "\n".join(extracted).strip()
        if not final_text:
            print("[OCR] No text detected")
            return ""

        if save_output:
            out_file = OUTPUT_DIRS["ocr_outputs"] / f"ocr_result_{Path(image_path).stem}.txt"
            with open(out_file, "w", encoding="utf-8") as fh:
                fh.write(final_text)
            print(f"[OCR] Saved OCR text to: {out_file}")

        print(f"[OCR] Extracted text (first 200 chars): {final_text[:200]}")
        return final_text

    except Exception as e:
        print(f"[OCR] Error: {e}")
        return ""

