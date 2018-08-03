from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.template import loader
from .models import Question, Course, Answer, Category
from django.views.decorators.csrf import csrf_exempt
from tablib import Dataset
import random
import csv


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




def progress(request, course_id):
    course_categories = Category.objects.filter(course_id=course_id)
    template = loader.get_template('quiz/progress.html')
    context = {
            'course_categories': course_categories,
            'course_id': course_id,
    }
    return HttpResponse(template.render(context,request))


@csrf_exempt
def custom_quiz(request, course_id):
    category_name = request.POST['category']
    num_of_hard = int(request.POST['hard'])
    num_of_medium = int(request.POST['medium'])
    num_of_easy = int(request.POST['easy'])
    total_number_of_questions = num_of_hard + num_of_medium + num_of_easy
    template = loader.get_template('quiz/custom_quiz.html')
    category_id = get_category_id_from_name(category_name)
    questions_list = get_category_questions(category_id)
    final_questions_list = []
    hard_questions = get_questions_by_difficulty(questions_list,'Hard',num_of_hard)
    final_questions_list.extend(hard_questions)
    medium_questions = get_questions_by_difficulty(questions_list,'Medium',num_of_hard)
    final_questions_list.extend(medium_questions)
    easy_questions = get_questions_by_difficulty(questions_list,'Easy',num_of_hard)
    final_questions_list.extend(easy_questions)
    random.shuffle(final_questions_list)
    questions_dict = {}  ## Will have muliple Question Text and Question Answers
    for question in final_questions_list:
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
    context = {
    'custom_category' : category_name,
    'custom_hard' : num_of_hard,
    'custom_medium' : num_of_medium,
    'custom_easy' : num_of_easy,
    'total_questions': total_number_of_questions,
    'course_id': course_id,
    'category_id':category_id,
    'questions_dict':questions_dict,
}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def auto_generated(request, course_id):
    total_number_of_questions = 20 ##TODO Change
    template = loader.get_template('quiz/auto_generated_quiz.html')
    course_questions_list = get_course_questions(course_id)
    course_questions_list = list(course_questions_list)
    random.shuffle(course_questions_list)
    course_questions_list = course_questions_list[:total_number_of_questions]
    questions_dict = {}  ## Will have muliple Question Text and Question Answers
    for question in course_questions_list:
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
    context = {
    'course_id': course_id,
    'questions_dict':questions_dict,
}
    return HttpResponse(template.render(context, request))

def get_category_id_from_name (category_name):
    category_list = Category.objects.filter(category_name=category_name)
    return category_list[0].id

def get_category_questions(category_id):
    category_questions_list = Question.objects.filter(category_id=category_id)
    return category_questions_list

def get_course_questions(course_id):
    course_question_list = Question.objects.filter(course_id=course_id)
    return course_question_list

def get_questions_by_difficulty(question_list,difficulty,num_of_questions):
    questions_by_difficulty = []
    for question in question_list:
        if question.question_level == difficulty:
            questions_by_difficulty.append(question)
    # TODO check greater between num_of_questions and actual quesions exist
    random.shuffle(questions_by_difficulty)
    questions_for_quiz = questions_by_difficulty[:num_of_questions]
    return questions_for_quiz

def answers(request, course_id):
    course_questions_list = Question.objects.filter(course_id=course_id)
    questions_dict = {}  ## Will have muliple Question Text and Question Answers
    for question in course_questions_list:
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
    template = loader.get_template('quiz/answers_page.html')
    context = {
        'questions_dict': questions_dict,
    }
    return HttpResponse(template.render(context, request))


##Functions For Saving Items to DB:

def add_course(course_name,course_desc):
    new_course = Course(course_name=course_name, course_desc = course_desc)
    new_course.save()
    return new_course

def add_category(category_name, category_desc, course_id):
    new_category = Category(category_name=category_name, category_desc=category_desc, course_id=course_id)
    new_category.save()
    return new_category

def add_question(question_text, course_id, pub_date, question_level, category_id):
    new_question = Question(question_text = question_text, course_id = course_id, pub_date = pub_date, question_level = question_level, category_id = category_id)
    new_question.save()
    return new_question

def add_answer(question, answer_text,answer_explanation,is_right):
    new_answer = Answer(question = question, answer_text = answer_text, answer_explanation = answer_explanation, is_right = is_right)
    new_answer.save()
    return new_answer

# Code to add new entities
# new_course = add_course('New Course For All','This is Desc')
# new_category = add_category('Best Category Ever', 'Category Desc is nice', new_course)
# new_question = add_question('Any Questions?', new_course, '2018-08-01 19:00:00', 'Hard', new_category)
# new_answer = add_answer(new_question, 'This is the final answer', 'Nothing to explain', 'true')


def index(request):
    courses_list = Course.objects.all()
    template = loader.get_template('quiz/index.html')
    context = {
        'courses_list': courses_list,
    }
    return HttpResponse(template.render(context, request))
