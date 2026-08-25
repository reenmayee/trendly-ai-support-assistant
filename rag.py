from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load policy document
with open("trendly_policy.md", "r", encoding="utf-8") as f:
    policy_text = f.read()

# Split policy into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_text(policy_text)

# Create vector database
vector_db = FAISS.from_texts(chunks, embeddings)

def search_policy(question):
    docs = vector_db.similarity_search(question, k=2)
    return "\n\n".join(doc.page_content for doc in docs)
