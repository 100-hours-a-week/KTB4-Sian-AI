from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough #, RunnableParallel

from dotenv import load_dotenv
import shutil, os
from glob import glob

load_dotenv()

EMBEDDING_MODEL = "models/gemini-embedding-001"

PERSIST_DIR = "./chroma_db"
COLLECTION = "sian-til"
MD_PATH = "./sian-til/*.md"
MD_LOADER_PATH = "./sian-til"

def md_loader():
    md_paths = sorted(glob(MD_PATH))
    md_docs = []
    for p in md_paths:
        md_docs.extend(TextLoader(p, encoding="utf-8").load())
    docs = md_docs
    print(f"[INFO] ... Number of Loaded Documents : {len(docs)}")

    # chunking 필요?
    split_docs = chunking(docs)

    return docs, split_docs

def chunking(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    split_docs = splitter.split_documents(docs)
    print(f"[INFO] ... Number of chunks: {len(split_docs)}")

    return split_docs

def dir_loader():

    md_loader = DirectoryLoader(
        path=MD_LOADER_PATH,
        glob="*.md", # 하위 폴더 포함: "**/*.md"
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    md_docs = md_loader.load()
    print(f"[INFO] ... Number of Loaded Documents : {len(md_docs)}")

    return md_docs

def build_embedding():
    # Embedding model
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return embeddings

def build_vector_store():
    # Embedding model
    embeddings = build_embedding()
    
    # ====== 1. Vector DB 존재 확인하고 Indexing 새로 하거나, 기존 Vector DB 로드 ======
    if os.path.exists(os.path.join(PERSIST_DIR, "chroma.sqlite3")):
        # ====== Vector DB 존재하면, 기존 인덱스 로드 (from_documents 호출 없이) ======
        print("[INFO] ---- 기존 인덱스 재로드 ---- ")
        return Chroma(
            collection_name=COLLECTION,
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings,  #embedding_function=embeddings는 새 질의를 벡터로 변환할 때 사용할 임베딩 모델
            # 저장된 문서 벡터는 처음 인덱싱할 때 사용한 임베딩 모델 기준으로 만들어졌습니다. 따라서 다시 검색할 때도 같은 임베딩 모델을 사용해야 합니다.
        )

    # ====== Vector DB 존재하지 않으면, Indexing 시작 ======
    print("[INFO] ---- 새 인덱스 생성 ---- ")
    #docs, split_docs = md_loader()
    docs = dir_loader()

    # ====== Vector DB 디렉토리 없으면 생성 ======
    if not os.path.exists(PERSIST_DIR):
        os.makedirs(PERSIST_DIR)

    # ====== 영구 저장 모드 ======
    vectorstore = Chroma.from_documents(
        docs,
        embeddings,
        collection_name=COLLECTION,         # 한 persist_directory 안에 여러 컬렉션을 분리 저장할 수 있다
        persist_directory=PERSIST_DIR,    # Chroma가 해당 폴더에 SQLite 파일로 인덱스를 저장. 프로세스를 다시 시작해도 이 폴더에서 인덱스를 다시 열 수 있다.
    )

    print("[INFO] ... Vector DB 저장 완료. ./chroma_db 폴더에 SQLite 인덱스가 생성되었습니다.")
    print("[INFO] ---- Finish Indexing ---- ")
    return vectorstore

def build_llm():
    print("[INFO] ---- Build LLM ---- ")

    provider = os.getenv("LLM_PROVIDER", "google").lower()
    print(f"[INFO] LLM Provider: {provider}")
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "gemma4:e2b-mlx"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash-lite"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

#retriever는 문자열을 받아 List[Document]를 돌려주므로, 
# 프롬프트에 넣기 전에 한 덩어리 문자열로 합치는 포맷 함수를 한 번 거쳐야 합니다
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs) # 하나의 긴 문자열로 포맷

def format_docs_with_source(docs):
    return "\n\n".join(f"[source {d.metadata.get('source')}] {d.page_content}" for d in docs)

def format_docs_with_source2(docs):
    lines = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        lines.append(f"[{i}] source={source}\n{doc.page_content}")
    return "\n\n".join(lines)

def build_prompt():
    prompt = ChatPromptTemplate.from_messages([
        ("system",
        "다음 문서만을 근거로 사용자 질문에 답하세요. "
        "근거가 부족하면 '주어진 자료에서는 확인할 수 없습니다. '라고 답하세요. "
        "답변 끝에는 참고한 출처를 표시하세요. \n\n"
        "{context}"),
        ("human", "{question}"),
    ])
    return prompt

def build_rag_chain():
    print("[INFO] Start RAG Pipeline")
    # ===== 1. 저장된 크로마 디비 가져옴 =====
    vectorstore = build_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # test_doc = retriever.invoke("RAG란 무엇인가요?")
    # print(f"검색된 문서 수: {len(test_doc)}")
    # for doc in test_doc:
    #     print(doc.page_content)
    #     print("---")

    # Augmented Generation을 위한 Prompt 구성
    prompt = build_prompt()

    # 답변 생성 LLM
    llm = build_llm()
    
    # LCEL chain (original)
    rag = (
        {"context": retriever | format_docs_with_source, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    ''' 이해가 필요함
    # 답변 생성용 체인 (docs를 문자열로 합친 뒤 LLM 호출)
    answer_chain = (
        {"context": lambda x: format_docs_with_source(x["docs"]),
         "question": lambda x: x["question"]}
        | prompt
        | llm
        | StrOutputParser()
    )
    # 최종 체인: 문서를 한번만 검색해서 답과 출처에 동시 사용
    rag = RunnableParallel(
        docs=retriever,
        question=RunnablePassthrough(),
    ).assign(answer=answer_chain)
    '''
    print("[INFO] RAG 파이프라인 완료\n")
    return rag

