import os
import uuid
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_core.messages import HumanMessage
import re

session_id = uuid.uuid4()

def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    embedding_function = UpstageEmbeddings(
        model="solar-embedding-1-large"
    )
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )
        
    return vectorstore

def create_rag_chain(vectorstore, api_key):
    retriever = vectorstore.as_retriever(k=3)
    print(retriever)
    from langchain_upstage import ChatUpstage
    chat = ChatUpstage(upstage_api_key=api_key)

    from langchain.chains import create_history_aware_retriever
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    contextualize_q_system_prompt = """이전 대화 내용과 최신 사용자 질문이 있을 때, 이 질문이 이전 대화 내용과 관련이 있을 수 있습니다. 
    이런 경우, 대화 내용을 알 필요 없이 독립적으로 이해할 수 있는 질문으로 바꾸세요. 질문에 답할 필요는 없고, 필요하다면 그저 다시 구성하거나 그대로 두세요."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])    

    history_aware_retriever = create_history_aware_retriever(chat, retriever, contextualize_q_prompt)

    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain

    qa_system_prompt = """당신은 서강대학교 메타버스전문대학원의 현대원 교수 입니다. 매우 학구적이고 친절한 태도를 가지고 있습니다.
                          질문에 답하기 위해 아래의 검색된 내용을 사용하고, 답을 모르면 모른다고 말하세요.
                          답변은 반드시 두 문장 이내로 짧게 대답하세요.
                          
    {context}"""
        
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain

if __name__ == "__main__":
    vectorstore = load_vectorstore("./chroma_db")
    rag_chain = create_rag_chain(vectorstore, os.getenv("UPSTAGE_API_KEY"))
    chat_history = []

    while True:
        question = input("Question: ")
        if question.lower() == "exit":
            break
        
        result = rag_chain.invoke({"input": question, "chat_history": chat_history})
        chat_history.extend([HumanMessage(content=question), result["answer"]])
        
        answer = result["answer"]
        context = result["context"]
        
        print("\nAnswer: ", answer)    
        print("\nSources:")
        for document in context:
            print()
            print(document)
        
        print("\n")