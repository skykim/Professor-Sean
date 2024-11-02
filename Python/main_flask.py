import os
import uuid
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import re
from flask import Flask, request, jsonify
from main_chat import load_vectorstore, create_rag_chain

app = Flask(__name__)
rag_chain = None
vectorstore = load_vectorstore("./chroma_db")
rag_chain = create_rag_chain(vectorstore, os.getenv("UPSTAGE_API_KEY"))

@app.route("/ask", methods=["POST"])
def process_rag():
    global vectorstore
    global rag_chain
    
    data = request.get_json()
    question = data.get("question")
    
    if question and rag_chain:
        result = rag_chain.invoke({"input": question, "chat_history": []})
        answer = result["answer"]
        context = result["context"]
        
        return jsonify({"answer": answer, "context": ""})
    else:
        return jsonify({"error": "RAG chain or question not provided"}), 400

if __name__ == "__main__":
    app.run(port=5000)