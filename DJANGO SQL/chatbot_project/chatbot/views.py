from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .forms import UploadFileForm, QueryForm
from .models import UploadedFile
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit

anthropic_api_key = ""


def get_or_create_db_instance():
    db_instance = cache.get('db_instance')
    if db_instance is None:
        uploaded_file = UploadedFile.objects.last()
        if uploaded_file:
            db_temp = uploaded_file.file.path
            db_instance = SQLDatabase.from_uri(f"sqlite:///{db_temp}")
            cache.set('db_path', db_temp, timeout=None)
    return db_instance

def create_agent(db_instance):
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", anthropic_api_key=anthropic_api_key)
    toolkit = SQLDatabaseToolkit(db=db_instance, llm=llm)
    tools = toolkit.get_tools()
    
    SQL_PREFIX = """You are an agent designed to interact with a SQL database.
        To start you should ALWAYS look at the tables in the database to see what you can query.
        Do NOT skip this step.
        Then you should query the schema of the most relevant tables."""
    system_message = SystemMessage(content=SQL_PREFIX)
    
    return create_react_agent(llm, tools, messages_modifier=system_message)

def chatbot(request):
    file_form = UploadFileForm()
    query_form = QueryForm()
    
    if request.method == 'POST':
        if 'file' in request.FILES:
            file_form = UploadFileForm(request.POST, request.FILES)
            if file_form.is_valid():
                file_form.save()
                cache.delete('db_path')
                return redirect('chatbot')
    
    context = {
        'file_form': file_form,
        'query_form': query_form,
    }
    return render(request, 'chatbot/chatbot.html', context)

@csrf_exempt
def submit_query(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        db_instance = get_or_create_db_instance()
        
        if db_instance:
            agent = create_agent(db_instance)
            result = agent.invoke({"messages": [HumanMessage(content=query)]})
            answer = result['messages'][-1].content
            
            return JsonResponse({'answer': answer})
        else:
            return JsonResponse({'error': 'No database file uploaded'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)