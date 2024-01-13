from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
#from langchain_community.embeddings import OpenAIEmbeddings
from langchain_together import Together
#from langchain_community.llms import Together

loader = PyPDFLoader("./2401.04088.pdf")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Add to vectorDB

"""
from langchain_together.embeddings import TogetherEmbeddings
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")
"""
vectorstore = Chroma.from_documents(
    documents=all_splits,
    collection_name="rag-chroma",
    embedding=OpenAIEmbeddings(),
)

retriever = vectorstore.as_retriever()


# RAG prompt
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)


llm = Together(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature=0.0,
    max_tokens=2000,
    top_k=1,
)

# RAG chain
chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | llm
    | StrOutputParser()
)

response = chain.invoke("What are the Architectural details of Mixtral?")
print(response)