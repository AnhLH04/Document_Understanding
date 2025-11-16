"""
Script để test nhanh các chức năng
"""

import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_extract(pdf_path: str):
    """Test extract endpoint"""
    print(f"Testing extract with: {pdf_path}")

    with open(pdf_path, "rb") as f:
        files = {"file": (Path(pdf_path).name, f, "application/pdf")}
        data = {
            "remove_logo": True,
            "save_images": True,
        }
        response = requests.post(f"{BASE_URL}/extract/", files=files, data=data)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    return response.json()


def test_index(pdf_path: str = None, file_path: str = None, skip_ocr: bool = False):
    """Test index endpoint"""
    print(f"Testing index...")

    if pdf_path:
        with open(pdf_path, "rb") as f:
            files = {"file": (Path(pdf_path).name, f, "application/pdf")}
            data = {"skip_ocr": skip_ocr}
            response = requests.post(f"{BASE_URL}/index/", files=files, data=data)
    else:
        data = {
            "file_path": file_path,
            "skip_ocr": skip_ocr,
        }
        response = requests.post(f"{BASE_URL}/index/", json=data)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    return response.json()


def test_chat(
    query: str, question_with_options: str = None, response_type: str = "text"
):
    """Test chat endpoint"""
    print(f"Testing chat with query: {query}")

    data = {
        "query": query,
        "response_type": response_type,
        "top_k": 5,
    }

    if question_with_options:
        data["question_with_options"] = question_with_options

    response = requests.post(f"{BASE_URL}/chat/", json=data)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    return response.json()


if __name__ == "__main__":
    # Test health
    test_health()

    # Test với file PDF của bạn
    # pdf_file = "path/to/your/document.pdf"

    # 1. Test extract
    # result = test_extract(pdf_file)

    # 2. Test index
    # result = test_index(pdf_path=pdf_file)

    # 3. Test chat
    # test_chat("Nội dung chính của tài liệu là gì?")
    # test_chat(
    #     query="Câu nào đúng?",
    #     question_with_options="Câu nào đúng về AI?\nA. AI không thể học\nB. AI có thể học\nC. AI vô dụng\nD. AI không tồn tại",
    #     response_type="multiple_choice"
    # )
