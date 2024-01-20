from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, JSONLoader
from langchain_openai import OpenAIEmbeddings

# Define the metadata extraction function.

loader = JSONLoader(
    file_path='./tea.jsonl',
    jq_schema=".abstract",
    text_content=False,
    json_lines=True,
    )

loader1 = JSONLoader(
    file_path='./tea.jsonl',
    jq_schema=".details",
    text_content=False,
    json_lines=True)

data = loader.load()
data1 = loader1.load()
print(data)

#embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L12-v2")
embedding_function = OpenAIEmbeddings()
#embedding_function = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

#1. how disimilarity of the data itself??
#2. analyzing the dataset??

db = FAISS.from_documents(all_splits, embedding_function)
db2 = db.save_local("faiss_index")
db3 = FAISS.load_local("faiss_index", embedding_function)

#query it
while True:
    query = input()
    docs = db.similarity_search_with_score(query) #similarity_search_by_vector
    prompt = ''
    for i in range(len(docs)):
        print(docs[i][1])
        prompt += data1[docs[i][0].metadata['row']].page_content + '\n'

    print(prompt)


