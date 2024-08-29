from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Question
from .quiz_logic import check_answer
import random
import os

def api_key_input(request):
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        request.session['anthropic_api_key'] = api_key
        return redirect('start_quiz')
    return render(request, 'api_key_input.html')

def start_quiz(request):
    if 'anthropic_api_key' not in request.session:
        return redirect('api_key_input')
    
    if 'quiz_questions' in request.session:
        del request.session['quiz_questions']
    if 'current_question' in request.session:
        del request.session['current_question']
    
    all_question_ids = list(Question.objects.values_list('id', flat=True))
    quiz_questions = random.sample(all_question_ids, min(50, len(all_question_ids)))
    request.session['quiz_questions'] = quiz_questions
    request.session['current_question'] = 0
    
    return redirect('quiz')

def quiz_view(request):
    if 'anthropic_api_key' not in request.session:
        return redirect('api_key_input')
    if 'quiz_questions' not in request.session:
        return redirect('start_quiz')

    current_question = request.session['current_question']
    quiz_questions = request.session['quiz_questions']

    if current_question >= len(quiz_questions):
        return render(request, 'quiz_ended.html')

    if request.method == 'GET':
        question = Question.objects.get(id=quiz_questions[current_question])
        return render(request, 'quiz.html', {'question': question, 'question_number': current_question + 1})
    elif request.method == 'POST':
        question_id = request.POST.get('question_id')
        user_answer = request.POST.get('answer')
        result = check_answer(question_id, user_answer, request.session['anthropic_api_key'])
        request.session['current_question'] += 1
        return JsonResponse(result)

def result_view(request):
    return render(request, 'result.html')