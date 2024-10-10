import fitz  # PyMuPDF
from PIL import Image
import io
import os
import sys
from concurrent.futures import ThreadPoolExecutor

def process_image(png_file):
    # 이미지 로드 및 팔레트 변환
    image = Image.open(png_file)
    # 컬러팔레트 크기 조정
    image = image.convert('P', palette=Image.ADAPTIVE, colors=16)
    image = image.convert('RGB')

    # 이미지 압축 및 PNG로 저장
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')  # PNG로 저장하여 무손실 압축
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr, image.size

def png_to_pdf(output_pdf_path):
    output_pdf = fitz.open()
    png_files = sorted([f for f in os.listdir('.') if f.lower().endswith('.png')], key=os.path.getctime)

    total_files = len(png_files)

    if total_files == 0:
        print("PNG 파일이 존재하지 않습니다. 프로그램을 종료합니다.")
        return

    # 이미지 병렬 처리
    results = [None] * total_files
    with ThreadPoolExecutor() as executor:
        future_to_index = {executor.submit(process_image, png_file): idx for idx, png_file in enumerate(png_files)}

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                img_byte_arr, (width, height) = future.result()
                results[idx] = (img_byte_arr, width, height)
            except Exception as e:
                print(f"파일 '{png_files[idx]}' 처리 중 오류 발생: {e}")
                continue

    # 순서대로 PDF에 추가
    for idx, result in enumerate(results):
        if result is None:
            continue

        img_byte_arr, width, height = result
        new_page = output_pdf.new_page(width=width, height=height)
        img_rect = fitz.Rect(0, 0, width, height)
        new_page.insert_image(img_rect, stream=img_byte_arr)

        # 진행률 출력
        progress = (idx + 1) / total_files * 100
        sys.stdout.write(f"\r진행률: {progress:.2f}% 완료")
        sys.stdout.flush()

    # 결과를 새로운 PDF로 저장
    if len(output_pdf) > 0:
        output_pdf.save(output_pdf_path, deflate=True)  # 압축 옵션 추가
        print(f"\nPDF가 '{output_pdf_path}'에 저장되었습니다.")
    else:
        print("저장할 페이지가 없습니다.")
    output_pdf.close()

# 사용 예제
output_pdf_path = "output_16color.pdf"  # 결과 PDF 파일

png_to_pdf(output_pdf_path)