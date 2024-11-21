from PyPDF2 import PdfReader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from transformers import AutoTokenizer
import os
import re


class RAG:
    def __init__(
        self, pdf_path="data/Blossoms of the Savannah.pdf", db_dir="./chroma_db"
    ):
        self.pdf_path = pdf_path
        self.db_dir = db_dir
        self.embeddings_model = "all-MiniLM-L6-v2"
        self.llm_model = "llama3.2:1b"
        self.vectorstore = None
        self.qa_chain = None
        self.raw_text = None
        self.chunks = []
        self.book = None
        self.setup()

    def setup(self):
        # Set up environment variables
        os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
        os.environ["TORCH_USE_CUDA_DSA"] = "1"
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
        print("Getting text from the PDF...")
        # Load text from a .txt file
        with open(
            "./data/extracted_text_from_images_batch_two.txt", "r", encoding="utf-8"
        ) as file:
            self.raw_text = file.read()

    def preprocess_text(self, text):
        """
        Clean and preprocess the input text.
        """
        text = re.sub(
            r"([a-z])([A-Z])", r"\1 \2", text
        )  # Add space between lowercase and uppercase
        text = re.sub(r"(\w)([.,;])", r"\1 \2", text)  # Add space before punctuation
        text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with a single space
        return text.strip()

    def chunking(self):
        print("Splitting text into chunks using tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        tokens = tokenizer.encode(self.raw_text, add_special_tokens=False)
        chunk_size = 128  # Adjust this to suit the LLM's context size
        overlap = 20

        # Tokenize and chunk the text
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i : i + chunk_size]
            chunk = tokenizer.decode(chunk_tokens)
            self.chunks.append(self.preprocess_text(chunk))

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
        os.system("cls" if os.name == "nt" else "clear")
        print("You can now query the model. Type 'exit' to stop.")
        while True:
            query = input("What is your query? ").strip()
            if query.lower() == "exit":
                print("Exiting the querying loop. Goodbye!")
                break
            response = self.qa_chain.invoke(query)
            print(f"Answer: {response}")


if __name__ == "__main__":
    rag_system = RAG()
    rag_system.querying_loop()
