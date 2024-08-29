import os
import random
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from .models import Question



def parse_questions(text):
    questions = text.split('\n\n')
    
    parsed_questions = []
    
    for i in range(0, len(questions), 3):
        question = questions[i].strip()
        options = {}
        options_text = questions[i+1].strip().split('\n')
        for option in options_text:
            key, value = option.split('. ', 1)
            options[key] = value
        
        correct_answer = questions[i+2].strip().split(': ')[1]
        
        parsed_questions.append({
            'question': question,
            'options': options,
            'Correct answer': correct_answer
        })
    
    return parsed_questions

def process_md_files(folder_path):
    question_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            file_path = os.path.join(folder_path, filename)
            loader = UnstructuredMarkdownLoader(file_path, mode="single")
            data = loader.load()
            text = data[0].page_content
            questions = parse_questions(text)
            question_list.extend(questions)
    return question_list

def load_questions():
    folder_path = "C:/Users/Admin/OneDrive/Desktop/LANGCHAIN/AWS Questions"
    question_set = process_md_files(folder_path)
    for q in question_set:
        Question.objects.create(
            text=q['question'],
            options=q['options'],
            correct_answer=q['Correct answer']
        )

def get_random_question():
    questions = Question.objects.all()
    if questions:
        return random.choice(questions)
    return None

def check_answer(question_id, user_answer, api_key):
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", anthropic_api_key=api_key)
    question = Question.objects.get(id=question_id)
    user_answers = [answer.strip().upper() for answer in user_answer.split(',')]
    
    AWS_Prefix = "You are an agent which has full knowledge of AWS cloud and its services. You are given a multiple choice question which has options. Also you are provided with correct answer. Your task is to check users answer. If user enters correct option(s) then say correct. If user selects wrong option(s) then Say Incorrect answer and also provide the correct answer with explanation"

    messages = [
        SystemMessage(content=AWS_Prefix),
        HumanMessage(content=f"The Question is:{question.text}. The options are: {question.options}. The correct options is/are {question.correct_answer}. User selected option(s) is/are {', '.join(user_answers)}"),
    ]
    ans = llm.invoke(messages)
    return {'result': ans.content}