import json
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
#from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

anthropic_api_key = ""


def index(request):
    return render(request, 'generator/index.html')

def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        questions = data.get('questions', [])
        
        #llm = ChatOllama(model="llama3.1", temperature=0)
        llm = ChatAnthropic(model="claude-3-sonnet-20240229", anthropic_api_key=anthropic_api_key)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an agent who is provided with the following question. Generate exactly 10 variants of these question. Provide the variants in strictly following JSON format without any additional comments.dont include original question in JSON file. JSON format must be strictly for each variant -> instruction: input: response: "
),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | llm
        
        results = []
        for question in questions:
            instruction = question['instruction']
            ip = question['input']
            response = question['response']
            
            human_message = HumanMessage(content=f"Instruction: {instruction}, Input: {ip}, Response: {response}")
            result = chain.invoke({"messages": [human_message]})
            variants = json.loads(result.content)
            results.append({
                "original": question,
                "variants": variants
            })
        
        return JsonResponse({'results': results})

def download_json(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        json_data = json.dumps(data, indent=2)
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="generated_questions.json"'
        return response

def download_parquet(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        df = pd.DataFrame(data)
        parquet_file = df.to_parquet()
        response = HttpResponse(parquet_file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="generated_questions.parquet"'
        return response