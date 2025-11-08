import os
import json
import re
import numpy as np
from openai import OpenAI
import faiss
import logging



class RagDatabase:
    RAG_INDEX = "data/rag/rag_index"
    RAG_DATA = "data/rag"

    def __init__(self):
        self.index = None
        self.documents = []
        self.all_chunks = []
        self.client = OpenAI()

    def initialize(self):
        self.load_documents()
        self.all_chunks = self.chunk()

        self.build_index()

    def load_documents(self):
        files = [f for f in os.listdir(self.RAG_DATA) if f.endswith('.txt')]
        for file in files:
            with open(os.path.join(self.RAG_DATA, file), "r", encoding="utf-8") as f:
                document = f.read()
                self.documents.append(document)

        if not self.documents:
            logging.warning("No documents found in RAG data directory.")
            return

    def build_index(self):
        if os.path.exists(self.RAG_INDEX):
            self.index = faiss.read_index(self.RAG_INDEX)
            return

        logging.info("Building RAG index...")
        for doc in self.documents:
            chunks = self.split_chunks(doc)
            embeddings = np.array([self.get_embeddings(chunk) for chunk in chunks])

            if self.index is None:
                d = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(d)
            self.index.add(embeddings)

    def get_embeddings(self, text):
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

    def chunk(self):
        all_chunks = []
        for doc in self.documents:
            chunks = self.split_chunks(doc)
            all_chunks.extend(chunks)

        return all_chunks

    def split_chunks(self, text, max_chunk_size=1024):
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def query(self, prompt, k=2) -> list[str]:
        query_embedding = np.array([self.get_embeddings(prompt)])
        D, I = self.index.search(query_embedding, k)

        return [self.all_chunks[i] for i in I.tolist()[0]][0]


