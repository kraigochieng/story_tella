from langchain_core.documents import Document


def create_documents_from_paragraphs(paragraphs):
    documents = []

    for paragraph in paragraphs:
        document = Document(page_content=paragraph)
        documents.append(document)

    return documents
