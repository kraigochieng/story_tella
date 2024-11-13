from types import new_class
from PyPDF2 import PdfReader
from langchain import embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from PyPDF2 import PdfReader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import Ollama
import os


class RAG:
    def __init__(
        self, pdf_path="data/Blossoms of the Savannah.pdf", db_dir="./chroma_db"
    ):
        self.pdf_path = pdf_path
        self.db_dir = db_dir
        self.embeddings_model = "all-MiniLM-L6-v2"
        self.llm_model = "llama3.2"
        self.vectorstore = None
        self.qa_chain = None
        self.raw_text = None
        self.chunks = None
        self.setup()

    def setup(self):
        # Load PDF and process text
        self.load_pdf()
        self.text_extraction()

        # Check if vector store exists
        if not os.path.exists(self.db_dir):
            print("Vector database not found. Creating a new one...")
            self.chunking()
            self.setup_vectorstore()
        else:
            print("Loading existing vector database...")
            self.load_vectorstore()

        # Setup the QA chain
        self.setup_qa_chain()

    def load_pdf(self):
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found at {self.pdf_path}")
        self.book = PdfReader(self.pdf_path)

    def text_extraction(self):
        print("Extracting text from the PDF...")
        self.raw_text = "".join([page.extract_text() for page in self.book.pages])

    def chunking(self):
        print("Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.chunks = text_splitter.split_text(self.raw_text)

        # Save chunks for reference
        with open("chunks.txt", "w") as f:
            for chunk in self.chunks:
                f.write(chunk + "\n")
        print(f"Created {len(self.chunks)} chunks.")

    def setup_vectorstore(self):
        print("Creating vector database...")
        embeddings = HuggingFaceEmbeddings(model_name=self.embeddings_model)
        self.vectorstore = Chroma.from_texts(
            self.chunks, embedding=embeddings, persist_directory=self.db_dir
        )
        self.vectorstore.persist()
        print("Vector database created and persisted.")

    def load_vectorstore(self):
        embeddings = HuggingFaceEmbeddings(model_name=self.embeddings_model)
        self.vectorstore = Chroma(
            persist_directory=self.db_dir, embedding_function=embeddings
        )

    def setup_qa_chain(self):
        print("Setting up QA chain...")
        llm = Ollama(model=self.llm_model)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm, retriever=self.vectorstore.as_retriever()
        )
        print("QA chain is ready.")

    def querying_loop(self):
        print("You can now query the model. Type 'exit' to stop.")
        while True:
            query = input("What is your query? ").strip()
            if query.lower() == "exit":
                print("Exiting the querying loop. Goodbye!")
                break
            response = self.qa_chain.run(query)
            print(f"Answer: {response}")


if __name__ == "__main__":
    rag_system = RAG()
    rag_system.querying_loop()
