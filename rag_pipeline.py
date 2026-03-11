import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()


# ===============================
# 1️⃣ CREATE VECTOR STORE
# ===============================
def create_vector_store(pdf_path):

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    if not documents:
        raise ValueError("PDF contains no readable content.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = text_splitter.split_documents(documents)

    # Filter valid text chunks
    texts, metadatas = [], []

    for doc in docs:
        content = doc.page_content
        if isinstance(content, str):
            content = content.strip()
            if content:
                texts.append(content)
                metadatas.append(doc.metadata)

    if not texts:
        raise ValueError("No valid text extracted from PDF.")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

    vectorstore.save_local("vectorstore")
    print("Vector store created successfully.")


# ===============================
# 2️⃣ LOAD VECTOR STORE
# ===============================
def load_vector_store():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )


# ===============================
# 3️⃣ GET ANSWER
# ===============================
def get_answer(query):

    if not query:
        return "Please enter a valid question."

    vectorstore = load_vector_store()
    docs = vectorstore.similarity_search(query, k=3)

    if not docs:
        return "No relevant documents found."

    context = "\n".join([doc.page_content for doc in docs])

    llm = ChatNVIDIA(
        model="meta/llama3-8b-instruct",
        temperature=0.2,
        max_tokens=512
    )

    prompt = f"""
    You are a Hospital AI Assistant.
    Answer ONLY from the provided context.
    If answer is not present, say:
    "Information not available in document."

    Context:
    {context}

    Question:
    {query}
    """

    response = llm.invoke(prompt)
    return response.content