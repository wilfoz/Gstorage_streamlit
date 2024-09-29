import asyncio

import streamlit as st
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_community import GCSDirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from storage_server import init_bucket

init_bucket()

st.secrets['OPENAI_API_KEY']
llm = ChatOpenAI(model="gpt-4o")


async def load_documents_async():
    loader = GCSDirectoryLoader(project_name="Chat-lt", bucket='streamlit-chatlt')
    documents = []
    async for docs in loader.alazy_load():
        if docs:
            print(f"Total de documentos carregados: {len(docs)}")
            print(docs[0].page_content[0:10])
            print(docs[0].metadata)
            documents.append(docs[0])
        else:
            print("Nenhum PDF foi carregado.")

docs = asyncio.run(load_documents_async())

print(f"Dividindo {len(docs)} documentos...")
for doc in docs:
    print(f"Tamanho do documento: {len(doc.page_content)}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever()

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

results = rag_chain.invoke({"input": "What was Nike's revenue in 2023?"})

results

st.markdown(results["context"][0].page_content)
print(results["context"][0].page_content)

