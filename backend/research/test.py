import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFacePipeline


PDF_PATH = "2nd semester marks carks.pdf"

print("Loading document...")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

if not documents:
    raise ValueError("No text extracted from PDF. Possibly scanned PDF.")

print(f"Loaded {len(documents)} pages")


print("Splitting document into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks")

print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


print("Creating FAISS vector store...")
vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)


test_query = "When does my insurance expire?"
print("\nTesting retrieval...")
retrieved_docs = vectorstore.similarity_search(test_query, k=2)

for i, doc in enumerate(retrieved_docs, start=1):
    print(f"\n--- Retrieved Chunk {i} ---")
    print(doc.page_content)


print("\nLoading LLaMA model (TinyLLaMA)...")

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map="auto"
)


hf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
    temperature=0,
    do_sample=False,
    repetition_penalty=1.1
)

llm = HuggingFacePipeline(pipeline=hf_pipeline)


qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
    return_source_documents=True
)


question = "What is my SGPA?"

print("\nAsking question:")
print(question)

result = qa_chain(question)

print("\n================ ANSWER ================")
print(result["result"])

print("\n=========== SOURCE DOCUMENTS ===========")
for doc in result["source_documents"]:
    print(doc.page_content)
    print("---------------------------------------")

print("\nNegative test:")
print(qa_chain("What is my bank balance?")["result"])
