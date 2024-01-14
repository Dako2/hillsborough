import tkinter as tk
import random
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_openai import OpenAIEmbeddings
#from langchain_community.embeddings import OpenAIEmbeddings
from langchain_together import Together
#from langchain_community.llms import Together
from langchain_together.embeddings import TogetherEmbeddings
import openai
import tkinter as tk

def display_strings(string1, string2, string3):
    root = tk.Tk()
    root.title("Chatea")

    frame = tk.Frame(root)
    frame.pack()

    label1 = tk.Label(frame, text=string1)
    label1.pack(side=tk.LEFT)

    label2 = tk.Label(frame, text=string2)
    label2.pack(side=tk.LEFT)

    label3 = tk.Label(frame, text=string3)
    label3.pack(side=tk.LEFT)

    root.mainloop()


loader = CSVLoader("./datasets/tea.csv") #PyPDFLoader("./2401.04088.pdf")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Add to vectorDB


embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")

vectorstore = Chroma.from_documents(
    documents=all_splits,
    collection_name="rag-chroma",
    embedding=TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval"),
)
vectordb = Chroma(persist_directory="", embedding_function=embeddings)
import chromadb
#client = chromadb.PersistentClient(path="./tea.db")

#retriever = vectordb.as_retriever()
retriever = vectorstore.as_retriever()

#retriever.save("rag-chroma")

# RAG prompt
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)


llm = Together(
    model="willwuwork@gmail.com/Mistral-7B-Instruct-v0.2-2024-01-13-23-14-34",
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


client = openai.OpenAI(
    api_key="2dd676e4528ce88cd7e66bd036e2d74d98d51ed4f4c3f5463e885d33e88fb5ba",
    base_url="https://api.together.xyz/v1",
    )

def generate_output():
    input_string = input_entry.get()

    system_content = "You are a traidtional Chinese medicine doctor. you analyze the patient's symptoms and recommend a treatement and a herbal tea"
    user_content = input_string #"最近我老是贪睡得病感冒，有什么茶推荐吗？"

    response = chain.invoke(user_content)

    # Base model 
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
    print("----Base model only----\n")
    str0 = stream.choices[0].message.content
    print(str0)
    #for chunk in stream:
    #    print(chunk.choices[0].delta.content or "", end="", flush=True)

    # Finetuned model 
    stream = client.chat.completions.create(
        model="willwuwork@gmail.com/Mistral-7B-Instruct-v0.2-2024-01-13-23-14-34",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        stream=False,
        max_tokens=1024,
        stop=['</s>']
    )
    print("----Finetuned model only----\n")

    str1 = stream.choices[0].message.content
    print(str1)
    #for chunk in stream:
    #    print(chunk.choices[0].delta.content or "", end="", flush=True)

    print("----Finetuned model with RAG----\n")
    print(response)

    output_string1 = str0
    output_string2 = str1
    output_string3 = response
    output_label.config(text=f"{output_string1}  {output_string2}  {output_string3}")

root = tk.Tk()
root.title("String Generator")

input_label = tk.Label(root, text="Input String:")
input_label.pack()

input_entry = tk.Entry(root)
input_entry.pack()

generate_button = tk.Button(root, text="Generate", command=generate_output)
generate_button.pack()

output_label = tk.Label(root, text="")
output_label.pack()

root.mainloop()
