import os
import re

import PyPDF2
import pytesseract
from langchain import hub
from langchain.chains import (
    RetrievalQA,
    create_extraction_chain,
    create_extraction_chain_pydantic,
)
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from pdf2image import convert_from_path
from PIL import Image
from transformers import AutoTokenizer


class RAG:
    """
    The RAG class helps process a PDF file so you can ask questions about its content. It works by:
    - Turning the PDF into images.
    - Extracting text from those images.
    - Breaking the text into smaller chunks (chunking).
    - Storing the chunks in a searchable database (vector database).
    - Setting up a question-and-answer system to find answers from the database.

    Properties of the Class:
    - `pdf_path`: The path to the PDF file you want to process.
    - `db_dir`: The folder where the vector database is saved or will be created.
    - `embeddings_model`: The model used to create embeddings (numerical representations of text) for the chunks.
    - `output_images_folder`: The folder where images from the PDF will be saved.
    - `output_text_folder`: The folder where text extracted from the images will be saved.
    - `llm_model`: The language model used to generate answers to your queries.
    - `vectorstore`: Stores the searchable chunks of text.
    - `qa_chain`: The system that handles the question-and-answer process.
    - `chunks`: The smaller pieces of text created from the extracted content.
    - `retriever`: The tool used to find the most relevant chunks from the vector database.

    How it works:
    - The `setup` function runs everything step by step. It checks if images, text, and the database
      already exist. If not, it creates them by calling other methods:
        1. `convert_pdf_to_images`: Turns each page of the PDF into an image.
        2. `convert_images_to_text`: Extracts text from the images.
        3. `chunking`: Breaks the extracted text into small, meaningful pieces.
        4. `setup_vectorstore`: Saves the chunks into a vector database for easy searching.
        5. `setup_qa_chain`: Sets up the question-answering system to retrieve answers.

    Once everything is set up, the `querying_loop` lets you ask questions, retrieves relevant text,
    and gives you an answer.
    """

    def __init__(
        self, pdf_path="data/Blossoms of the Savannah.pdf", db_dir="./chroma_db"
    ):
        self.pdf_path = pdf_path
        self.db_dir = db_dir
        self.embeddings_model = "all-MiniLM-L6-v2"
        self.output_images_folder = "images_from_pdf"
        self.output_text_folder = "text_from_images"
        self.llm_model = "llama3.2:1b"
        self.vectorstore = None
        self.qa_chain = None
        self.chunks = []
        self.retriever = None
        self.setup()

    def setup(self):
        # Set up environment variables
        os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
        os.environ["TORCH_USE_CUDA_DSA"] = "1"

        # Load PDF to images
        if not os.path.exists(self.output_images_folder):
            self.convert_pdf_to_images()
        else:
            print(f"{self.output_images_folder} already exists")

        # Load images to text
        if not os.path.exists(self.output_text_folder):
            self.convert_images_to_text()
        else:
            print(f"{self.output_text_folder} already exists")

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

    def convert_pdf_to_images(self):
        print("Creating necessary directory for converting PDF to images...")
        os.makedirs(self.output_images_folder)
        print("Converting PDF to images...")
        # Convert PDF to images
        output_images = convert_from_path(self.pdf_path, dpi=300)

        # Save the images
        for i, image in enumerate(output_images, start=1):
            image_path = os.path.join(self.output_images_folder, f"page_{i}.jpeg")
            image.save(image_path, "PNG")
            print(f"Page {i} saved as image")

        print(f"Converted PDF to {len(output_images)} images.")

    def convert_images_to_text(self):
        print("Creating necessary directory for converting images to text")
        os.makedirs(self.output_text_folder)
        print("Converting images to text...")
        number_of_images = len(os.listdir(self.output_images_folder))

        # Extract text from each image
        for i in range(number_of_images):
            image_path = os.path.join(self.output_images_folder, f"page_{i}.jpeg")
            extracted_text = pytesseract.image_to_string(Image.open(image_path))
            text_path = os.path.join(self.output_text_folder, f"page_{i}.txt")

            with open(text_path, "w", encoding="utf-8") as file:
                file.write(extracted_text)

            print(f"Image {i} saved as text")

        print("Converted images to text.")

    def chunking(self):
        texts = []
        print("Getting chunks from the text...")

        # Read all text files and store in array
        for file in os.listdir(self.output_text_folder):
            full_file_name = os.path.join(self.output_text_folder, file)
            with open(full_file_name, "r") as f:
                content = f.read()
                texts.append(content)

        text_splitter = SemanticChunker(
            HuggingFaceEmbeddings(model_name=self.embeddings_model),
            breakpoint_threshold_type="percentile",
        )

        self.chunks = text_splitter.create_documents(texts)

        print(f"Created {len(self.chunks)} chunks.")

    def setup_vectorstore(self):
        print("Creating vector database...")
        embeddings = HuggingFaceEmbeddings(model_name=self.embeddings_model)
        self.vectorstore = Chroma.from_documents(
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

        # Define a custom prompt template
        prompt_template = """
        You are a helpful assistant.
        Use the context below to answer the question.
        Directly quote the context in the final answer.

        
        Context:
        {context}
        
        Question: {question}
        Answer: 
        """
        qa_prompt = PromptTemplate(
            input_variables=["context", "question"],  # Variables in the prompt
            template=prompt_template,
        )

        self.retriever = self.vectorstore.as_retriever(searck_kwargs={"k": 5})

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm, retriever=self.retriever, chain_type_kwargs={"prompt": qa_prompt}
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

            # Retrieve the top documents
            retrieved_docs = self.retriever.get_relevant_documents(query)

            print("\n--- Retrieved Documents ---")

            for i, doc in enumerate(retrieved_docs, 1):
                print(f"\nDocument {i}:\n{doc.page_content}")
                if doc.metadata:
                    print(f"Metadata: {doc.metadata}")

            # Print actual answer
            print(f"Answer: {response}")


if __name__ == "__main__":
    rag_system = RAG()
    rag_system.querying_loop()
