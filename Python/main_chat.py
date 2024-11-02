import os
import uuid
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import re

# 환경 변수 로드
load_dotenv()

# 세션 ID 생성
session_id = uuid.uuid4()

def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    """
    저장된 Chroma 벡터스토어를 로드합니다.
    
    Args:
        persist_directory (str): 벡터스토어가 저장된 디렉토리 경로
    
    Returns:
        Chroma: 로드된 벡터스토어 객체
    """
    embedding_function = UpstageEmbeddings(
        model="solar-embedding-1-large"
    )
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )
    
    return vectorstore


# RAG 체인 생성 함수
def create_rag_chain(vectorstore, api_key):
    retriever = vectorstore.as_retriever(k=5)
    print(retriever)
    from langchain_upstage import ChatUpstage
    chat = ChatUpstage(upstage_api_key=api_key)

    from langchain.chains import create_history_aware_retriever
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    contextualize_q_system_prompt = """이전 대화 내용과 최신 사용자 질문이 있을 때, 이 질문이 이전 대화 내용과 관련이 있을 수 있습니다. 
    이런 경우, 대화 내용을 알 필요 없이 독립적으로 이해할 수 있는 질문으로 바꾸세요. 
    질문에 답할 필요는 없고, 필요하다면 그저 다시 구성하거나 그대로 두세요."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(chat, retriever, contextualize_q_prompt)

    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain

    qa_system_prompt = """
                          당신은 Sean교수 입니다. 외향적이고 질문을 좋아합니다. 식사 후 케이크를 먹는 것을 좋아합니다. 청바지를 좋아합니다. 술을 가리지 않습니다.
                          지질문에 답하기 위해 검색된 내용을 사용하세요.
                          답을 모르면 모른다고 말하세요.
                          답변은 두 문장 이내로 간결하게 유지하세요.

    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain

# PDF 파일 경로 설정 및 벡터스페이스 생성
vectorstore = load_vectorstore("./chroma_db")

# RAG 체인 생성
rag_chain = create_rag_chain(vectorstore, os.getenv("UPSTAGE_API_KEY"))

# 질문 입력 및 답변 출력
while True:
    question = input("질문을 입력하세요 (종료하려면 'exit'): ")
    if question.lower() == "exit":
        break
    
    # 질문에 대한 답변 생성
    result = rag_chain.invoke({"input": question, "chat_history": []})
    answer = result["answer"]
    context = result["context"]
    
    print("\n📍 답변:", answer)
    print("📍 증거:", context)
    print("\n")