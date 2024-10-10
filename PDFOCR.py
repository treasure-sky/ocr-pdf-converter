import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
import sys

# Tesseract 경로 설정 (맥에서 Tesseract가 기본 경로에 설치된 경우 필요 없음)
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

def ocr_png_to_pdf(output_pdf_path):
    output_pdf = fitz.open()
    png_files = sorted([f for f in os.listdir('.') if f.lower().endswith('.png')], key=os.path.getctime)

    total_files = len(png_files)

    # 모든 PNG 파일에 대해 OCR 수행
    for idx, png_file in enumerate(png_files):
        image = Image.open(png_file)

        # OCR 수행
        ocr_text = pytesseract.image_to_string(image, lang='kor+eng')

        # 새로운 PDF 페이지 추가
        width, height = image.size
        new_page = output_pdf.new_page(width=width, height=height)

        # 이미지 삽입
        img_rect = fitz.Rect(0, 0, width, height)
        new_page.insert_image(img_rect, filename=png_file)

        # OCR 텍스트 추가 (투명하게 삽입)
        text_rect = fitz.Rect(0, 0, width, height)
        new_page.insert_textbox(text_rect, ocr_text, fontsize=10, overlay=True, color=(0, 0, 0, 0))

        # 진행률 출력
        progress = (idx + 1) / total_files * 100
        sys.stdout.write(f"\r진행률: {progress:.2f}% 완료")
        sys.stdout.flush()

    # 결과를 새로운 PDF로 저장
    output_pdf.save(output_pdf_path)
    output_pdf.close()

    print(f"\nOCR 적용된 PDF가 '{output_pdf_path}'에 저장되었습니다.")

# 사용 예제
output_pdf_path = "output_ocr.pdf"  # OCR이 적용된 결과 PDF 파일

ocr_png_to_pdf(output_pdf_path)