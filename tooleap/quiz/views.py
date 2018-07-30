from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.template import loader
from .models import Question, Course, Answer, Category
from django.views.decorators.csrf import csrf_exempt


##This generates html for questions for a given course.
def course_question(request, course_id):
    course_questions_list = Question.objects.filter(course_id=course_id)
    questions_dict = {}  ## Will have muliple Question Text and Question Answers
    for question in course_questions_list:
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
    template = loader.get_template('quiz/course_questions.html')
    context = {
        'questions_dict': questions_dict,
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def quiz_builder(request, course_id):
    course_categories = Category.objects.filter(course_id=course_id)
    template = loader.get_template('quiz/quiz_builder.html')
    context = {
            'course_categories': course_categories,
            'course_id': course_id,
    }
    return HttpResponse(template.render(context,request))


def index(request):
    courses_list = Course.objects.all()
    template = loader.get_template('quiz/index.html')
    context = {
        'courses_list': courses_list,
    }
    return HttpResponse(template.render(context, request))




@csrf_exempt
def custom_quiz(request, course_id):
    category = request.POST['category']
    hard = int(request.POST['hard'])
    medium = int(request.POST['medium'])
    easy = int(request.POST['easy'])
    total_number_of_questions = hard + medium + easy
    template = loader.get_template('quiz/custom_quiz.html')
    context = {
    'custom_category' : category,
    'custom_hard' : hard,
    'custom_medium' : medium,
    'custom_easy' : easy,
    'total_questions': total_number_of_questions,
    'course_id': course_id,
}
    return HttpResponse(template.render(context, request))
