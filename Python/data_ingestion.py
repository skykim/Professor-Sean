from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_upstage import UpstageEmbeddings

# .env 파일에서 환경 변수 불러오기
load_dotenv()
api_key = os.getenv("UPSTAGE_API_KEY")

#PDF 파일들로부터 Chroma 벡터스토어를 생성
def create_vectorstore(pdf_directory: str, persist_directory: str = "./chroma_db") -> Chroma:
    # PDF 파일 목록 가져오기
    pdf_files = [
        os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory)
        if f.lower().endswith('.pdf')
    ]
    
    if not pdf_files:
        raise ValueError(f"No PDF files found in {pdf_directory}")
    
    # 문서 로드 및 처리
    documents = []
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            # 소스 파일 정보 추가
            for page in pages:
                page.metadata['source_file'] = Path(pdf_path).name
            documents.extend(pages)
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            continue
    
    if not documents:
        raise ValueError("No documents were successfully processed")
    
    # 임베딩 모델 초기화
    embedding_function = UpstageEmbeddings(
        model="solar-embedding-1-large",
        api_key=api_key  # API 키 전달
    )
    
    # Chroma 벡터스토어 생성
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        persist_directory=persist_directory  # 이렇게 하면 자동으로 저장됨
    )
    
    return vectorstore

#저장된 Chroma 벡터스토어를 로드
def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    embedding_function = UpstageEmbeddings(
        model="solar-embedding-1-large",
        api_key=api_key  # API 키 전달
    )
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )
    
    return vectorstore

# 사용 예시
if __name__ == "__main__":
    try:
        # 벡터스토어 생성
        vectorstore = create_vectorstore(
            pdf_directory="./pdfs",
            persist_directory="./chroma_db"
        )
        print("Vector store created and saved successfully")
        
        # 저장된 벡터스토어 로드
        loaded_vectorstore = load_vectorstore("./chroma_db")
        print("Vector store loaded successfully")
        
        '''
        # 예시 쿼리 실행
        query = "your query here"
        results = loaded_vectorstore.similarity_search(
            query,
            k=3  # 상위 3개 결과 반환
        )
        for doc in results:
            print(f"Source: {doc.metadata['source_file']}")
            print(f"Content: {doc.page_content[:200]}...")
            print("-" * 80)
        '''
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
