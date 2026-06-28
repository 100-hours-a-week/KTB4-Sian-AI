from langchainfile.rag import build_rag_chain
from langchainfile.eval import eval_rag

def main():
    print("Hello from rag-project!")
    q = "RAG란 무엇인가요?"

    rag = build_rag_chain()
    result =rag.invoke(q)

    print("답변:")
    print(result)
    print()

    eval_result = eval_rag(rag)
    print("평가 답변: ")
    print(eval_result)


if __name__ == "__main__":
    main()
