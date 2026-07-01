from indexing import indexing, embedding
import urllib.request
import os
from dotenv import load_dotenv
import os
from huggingface_hub import login

from generation import generate_main

load_dotenv()
login(token=os.getenv("HF_TOKEN"))

def main():
    print("[INFO] Hello from week6-miniproject!")
    pdf_name = "2020_경제금융용어_700선_게시.pdf"

    if pdf_name == "2020_경제금융용어_700선_게시.pdf":
        if not os.path.exists(pdf_name):
            urllib.request.urlretrieve("https://github.com/chatgpt-kr/openai-api-tutorial/raw/main/ch07/2020_%EA%B2%BD%EC%A0%9C%EA%B8%88%EC%9C%B5%EC%9A%A9%EC%96%B4%20700%EC%84%A0_%EA%B2%8C%EC%8B%9C.pdf", filename="2020_경제금융용어_700선_게시.pdf")
            print(f"[INFO] Successfully downloaded {pdf_name}")
        else:
            print(f"[INFO] {pdf_name} already exists")
    else:
        raise ValueError

    collection = indexing(pdf_name)

    query = "저축률이 무엇인가요?"

    generate_main(query, collection)
    
if __name__ == "__main__":
    main()
