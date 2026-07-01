from generation import generate_answer
from indexing import indexing, embedding
import urllib.request
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from huggingface_hub import login

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

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    print(f"[INFO] Successfully downloaded Embedding Model")

    
    collection = indexing(pdf_name,model)

    query = "저축률이 무엇인가요?"
    query_embedding = embedding(model, query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    # 검색된 청크 텍스트를 꺼냅니다.
    retrieved_chunks = results["documents"][0]

    # 검색 결과를 확인합니다.
    print("===== Retrieval 결과 =====")
    for i, chunk in enumerate(retrieved_chunks):
        pages = results["metadatas"][0][i]["page"]
        dist = results["distances"][0][i]
        print(f"  [{i+1}위] {chunk[:80]}...")
        print(f"       출처: p.{pages}, 거리: {dist:.4f}")
    print()

    # Generation: 검색된 청크를 근거로 답변을 생성합니다.
    answer = generate_answer(query, retrieved_chunks)

    print("===== Generation 결과 =====")
    print(f"질문: {query}")
    print(f"답변: {answer}")
    
if __name__ == "__main__":
    main()
