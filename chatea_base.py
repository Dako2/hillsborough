from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_openai import OpenAIEmbeddings
#from langchain_community.embeddings import OpenAIEmbeddings

#from langchain_community.llms import Together
from langchain_together.embeddings import TogetherEmbeddings
import openai

loader = CSVLoader("./datasets/tea.csv", encoding = 'utf-8') #PyPDFLoader("./2401.04088.pdf")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

embedding_function = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")

vectorstore = Chroma.from_documents(
    documents=all_splits,
    collection_name="rag-chroma",
    embedding=embedding_function#$TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval"),
)

retriever = vectorstore.as_retriever()
retriever.save("rag-chroma")

def base_main(user_content = "最近我老是贪睡得病感冒，有什么茶推荐吗？"):
    system_content = "You are a traidtional Chinese medicine doctor. you analyze the patient's symptoms and recommend a treatement and a herbal tea"
    client = openai.OpenAI()
    stream = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        stream=False,
        max_tokens=1024,
        stop=['</s>']
    )

    print("\n----Base model only----\n")
    str0 = stream.choices[0].message.content
    print(str0)

user_content = input("Please enter your question: ")
if not user_content:
    user_content = "最近我老是贪睡得病感冒，有什么茶推荐吗？"

base_main(user_content)
