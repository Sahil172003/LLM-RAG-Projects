import os
import pickle
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

anthropic_api_key = ""

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def index(request):
    return render(request, 'chatbot/index.html')

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf')
        query = request.POST.get('query')

        if pdf_file and query:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=300,
                chunk_overlap=20,
                length_function=len
            )
            chunks = text_splitter.split_text(text=text)

            store_name = pdf_file.name[:-4]
            if os.path.exists(f"{store_name}.pkl"):
                with open(f"{store_name}.pkl", "rb") as f:
                    VectorStore = pickle.load(f)
            else:
                embeddings = HuggingFaceEmbeddings()
                VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
                with open(f"{store_name}.pkl", "wb") as f:
                    pickle.dump(VectorStore, f)

            llm = ChatAnthropic(model="claude-3-sonnet-20240229", anthropic_api_key=anthropic_api_key)
            retriever = VectorStore.as_retriever()

            prompt = ChatPromptTemplate.from_template("""Answer the following question based on the given context:

            Context: {context}

            Question: {question}

            Answer:""")

            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            response = rag_chain.invoke(query)

            return JsonResponse({'response': response})

    return render(request, 'chatbot/chat.html')