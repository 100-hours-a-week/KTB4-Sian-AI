from langchainfile.rag import build_rag_chain
from langchainfile.eval import eval_rag
import argparse

import langchain
import langchain_community

def main():
    print("Hello from rag-project!")

    #print(langchain.__version__)
    #print(langchain_community.__version__)
    
    parser = argparse.ArgumentParser(description="LangChain")
    parser.add_argument('--mode', choices=['chaintest','eval'], help='Choose mode: LangChainTest, LangSmithEval')
    args = parser.parse_args()

    if args.mode == "chaintest":
        keyword = input("TIL에서 알고 싶은 개념을 입력하세요: ")
        q = f"{keyword}란 무엇인가요?"
        print(f"Sample Question: {q}\n")
        
        rag = build_rag_chain()
        result =rag.invoke(q)

        print(f"Answer: \n{result}")
        print()
    elif args.mode == "eval":
        rag = build_rag_chain()
        eval_result = eval_rag(rag)
        print("LangSmith Evaluation")
        print(f"{eval_result}")
    
if __name__ == "__main__":
    main()
