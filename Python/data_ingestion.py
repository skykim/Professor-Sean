from typing import List
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_upstage import UpstageEmbeddings
from langchain.schema import Document

api_key = os.getenv("UPSTAGE_API_KEY")

def create_vectorstore(pdf_directory: str, persist_directory: str = "./chroma_db") -> Chroma:
    pdf_files = [
        os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory)
        if f.lower().endswith('.pdf')
    ]
    
    if not pdf_files:
        raise ValueError(f"No PDF files found in {pdf_directory}")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    documents = []
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            
            for page in pages:
                page.metadata['source_file'] = Path(pdf_path).name
                page.metadata['page'] = page.metadata.get('page', 0)
                
                chunks = text_splitter.split_text(page.page_content)
                
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "source_file": page.metadata['source_file'],
                            "page": page.metadata['page'],
                            "chunk": i
                        }
                    )
                    documents.append(doc)
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            continue
    
    if not documents:
        raise ValueError("No documents were successfully processed")
    
    embedding_function = UpstageEmbeddings(
        model="solar-embedding-1-large",
        api_key=api_key
    )
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        persist_directory=persist_directory
    )
    
    return vectorstore

def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    embedding_function = UpstageEmbeddings(
        model="solar-embedding-1-large",
        api_key=api_key
    )
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )
    
    return vectorstore

if __name__ == "__main__":
    pdf_directory = "./pdfs"
    persist_dir = "./chroma_db"
    
    if os.path.exists(persist_dir):
        try:
            shutil.rmtree(persist_dir)
            print(f"Successfully deleted existing {persist_dir}")
        except Exception as e:
            print(f"Error deleting {persist_dir}: {e}")
    
    try:
        vectorstore = create_vectorstore(
            pdf_directory=pdf_directory,
            persist_directory=persist_dir
        )
        print("Vector store created and saved successfully")
        
        loaded_vectorstore = load_vectorstore(persist_dir)
        print("Vector store loaded successfully")
        
        # query test        
        query = "Relay for Life를 통해서 모은 기금의 액수는?"
        results = loaded_vectorstore.similarity_search(
            query,
            k=5
        )
        for doc in results:
            print(f"Source: {doc.metadata['source_file']}")
            print(f"Page: {doc.metadata['page']}")
            print(f"Chunk: {doc.metadata['chunk']}")
            print(f"Content: {doc.page_content}...")
            print("-" * 80)        
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")