# PyMuPDF 라이브러리를 가져옵니다.
# PDF 파일을 열고, 페이지별 텍스트를 추출할 때 사용합니다.
import pymupdf
import chromadb

def load_pdf_pymupdf(filepath):
    """
    PyMuPDF로 PDF 파일에서 페이지별 텍스트를 추출합니다.
    각 페이지의 텍스트와 메타데이터(출처, 페이지 번호)를 함께 반환합니다.

    매개변수
    filepath : str
        읽어올 PDF 파일 경로

    반환값
    list[dict]
        페이지별 텍스트와 메타데이터를 담은 딕셔너리 리스트
    """

    # PDF 파일을 엽니다.
    doc = pymupdf.open(filepath)

    # 페이지별 결과를 저장할 리스트입니다.
    pages = []

    # PDF의 각 페이지를 순회하면서 텍스트를 추출합니다.
    # i는 페이지 인덱스이며 0부터 시작합니다.
    # page는 실제 페이지 객체입니다.
    for i, page in enumerate(doc):
        # 현재 페이지의 전체 텍스트를 추출합니다.
        text = page.get_text()

        # 추출한 텍스트와 메타데이터를 하나의 딕셔너리로 만들어 리스트에 추가합니다.
        pages.append({
            "text": text.strip(),  # 앞뒤 공백과 줄바꿈을 제거한 텍스트
            "metadata": {
                "source": filepath,     # 원본 PDF 파일 경로
                "page": i + 1,          # 실제 페이지 번호는 1부터 시작하도록 변환
                "total_pages": len(doc) # 전체 페이지 수
            }
        })

    # 사용이 끝난 PDF 파일 객체를 닫아 메모리를 정리합니다.
    doc.close()

    # 페이지별 추출 결과를 반환합니다.
    return pages

# PDF 파일 전체에서 텍스트를 추출합니다.
def load_pdf(filepath):
    """PyMuPDF로 PDF 파일에서 텍스트를 추출합니다."""
    # PDF 파일을 엽니다.
    doc = pymupdf.open(filepath)

    # 모든 페이지의 텍스트를 누적할 문자열입니다.
    text = ""

    # 각 페이지를 순회하며 텍스트를 이어 붙입니다.
    for page in doc:
        text += page.get_text()

    # 파일 사용이 끝났으므로 닫습니다.
    doc.close()

    # PDF 전체 텍스트를 반환합니다.
    return text

def chunking(pages):
    # ===== 페이지별 텍스트를 청크로 저장 =====
    # PDF에서 추출한 텍스트 청크를 저장할 리스트입니다.
    all_chunks = []

    # 각 청크에 대응하는 메타데이터를 저장할 리스트입니다.
    # 예: 파일명, 페이지 번호, 전체 페이지 수
    all_metadatas = []

    # pages는 이전 단계에서 PDF를 페이지별로 파싱한 결과입니다.
    # 각 페이지의 텍스트와 메타데이터를 순회합니다.
    for p in pages:
        # 텍스트가 비어 있지 않은 경우에만 저장합니다.
        if p["text"]:
            # 페이지 텍스트를 청크 리스트에 추가합니다.
            all_chunks.append(p["text"])

            # 해당 페이지의 메타데이터도 함께 저장합니다.
            all_metadatas.append(p["metadata"])

    return all_chunks, all_metadatas


def embedding(model, all_chunks):
    
    # 페이지별 텍스트 청크를 임베딩 벡터로 변환합니다.
    # 결과는 넘파이 배열 형태이므로, ChromaDB에 넣기 위해 리스트로 변환합니다.
    embeddings = model.encode(all_chunks).tolist()
    return embeddings


def save_to_vectorDB(client, embeddings, all_chunks, all_metadatas):

    # "pdf_demo"라는 이름의 컬렉션을 생성합니다.
    # cosine 유사도를 사용하도록 설정합니다.
    collection = client.create_collection(
        name="rag_demo",
        metadata={"hnsw:space": "cosine"}
    )

    # ChromaDB 컬렉션에 문서, 임베딩, 메타데이터를 저장합니다.
    collection.add(
        # 각 문서를 구분하기 위한 고유 ID를 생성합니다.
        # 여기서는 page_0, page_1, ... 형식으로 만듭니다.
        ids=[f"page_{i}" for i in range(len(all_chunks))],

        # 저장할 실제 문서 텍스트입니다.
        documents=all_chunks,

        # 문서 텍스트를 벡터로 변환한 임베딩 값입니다.
        embeddings=embeddings,

        # 각 문서에 대응하는 메타데이터입니다.
        # 검색 결과에서 출처와 페이지 번호를 함께 보여줄 수 있습니다.
        metadatas=all_metadatas
    )

    print(f"ChromaDB 저장 수: {collection.count()}")
    return collection

# ===== 실행 =====
def indexing(pdf_name, model):
    pages = load_pdf_pymupdf(pdf_name)
    print(len(pages))

    all_chunks, all_metadatas = chunking(pages)

    
    embeddings = embedding(model, all_chunks)
    # ChromaDB 클라이언트를 생성합니다.
    client = chromadb.Client()
    collection = save_to_vectorDB(client, embeddings, all_chunks, all_metadatas)
    return collection
    
