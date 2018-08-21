from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.template import loader
from .models import Question, Course, Answer, Category, User_Answer, Answered_Quiz
from django.views.decorators.csrf import csrf_exempt
from tablib import Dataset
import random
import csv
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm


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
    course_name = get_course_name(course_id)
    template = loader.get_template('quiz/quiz_builder.html')
    context = {
            'course_categories': course_categories,
            'course_id': course_id,
            'course_name': course_name,
    }
    return HttpResponse(template.render(context,request))



def teacher_progress_view(request, course_id):
    course_categories = Category.objects.filter(course_id=course_id)
    course_name = get_course_name(course_id)
    template = loader.get_template('quiz/teacher_progress_view.html')
    context = {
            'course_categories': course_categories,
            'course_id': course_id,
            'course_name': course_name,
    }
    return HttpResponse(template.render(context,request))

def progress(request, user_id, course_id):
    course_categories = Category.objects.filter(course_id=course_id)
    course_answers = User_Answer.objects.filter(course_id=course_id,user=user_id)
    answers_per_quiz = get_user_answers_per_quiz(course_answers)
    answers_per_category = get_user_answers_per_category(course_answers)
    answers_per_difficulty = get_user_answers_per_difficulty(course_answers)
    print('ANSWER PER DIFFICULTY')
    print(answers_per_difficulty['Hard'].get('right'))
    print (answers_per_quiz)
    print (answers_per_category)
    print (answers_per_difficulty)
    course_name = get_course_name(course_id)
    hard_right = answers_per_difficulty['Hard'].get('right')
    hard_false = answers_per_difficulty['Hard'].get('false')
    medium_right = answers_per_difficulty['Medium'].get('right')
    medium_false = answers_per_difficulty['Medium'].get('false')
    easy_right = answers_per_difficulty['Easy'].get('right')
    easy_false = answers_per_difficulty['Easy'].get('false')
    template = loader.get_template('quiz/progress.html')
    dates = ['2018-01-01','2018-01-02']
    context = {
            'course_categories': course_categories,
            'course_id': course_id,
            'course_name': course_name,
            'answers_per_category': answers_per_category,
            'answers_per_quiz': answers_per_quiz,
            'dates':dates,
            'answers_per_difficulty': answers_per_difficulty,
            'hard_right': hard_right,
            'hard_false': hard_false,
            'medium_right': medium_right,
            'medium_false': medium_false,
            'easy_right': easy_right,
            'easy_false': easy_false,
            'all_right': hard_right+medium_right+easy_right,
            'all_questions': hard_right+medium_right+easy_right+hard_false+medium_false+easy_false,
    }
    return HttpResponse(template.render(context,request))

def get_user_answers_per_quiz(course_answers):
    quizes_answeres = {}
    for answer in course_answers:
        if answer.quiz_id not in quizes_answeres:
            quizes_answeres[answer.quiz_id] = {'right':0,'false':0,'quiz_time':answer.quiz_time}
        if answer.answered_answer_id == answer.right_answer_id:
            quizes_answeres[answer.quiz_id]['right'] += 1
        else:
            quizes_answeres[answer.quiz_id]['false'] += 1
    return quizes_answeres

def get_user_answers_per_category(course_answers):
    category_answers = {}
    for answer in course_answers:
        print('Printing ANSWER ####')
        print(answer)
        print('Printing qid ####')
        print(answer.question_id)
        question_text = Question.objects.get(id=answer.question_id).question_text
        print('Printing q text ####')
        print(question_text)
        question_category = Question.objects.get(id=answer.question_id).category_id
        if question_category not in category_answers:
            category_answers[question_category] = {'right':0,'false':0}
        if answer.answered_answer_id == answer.right_answer_id:
            category_answers[question_category]['right'] += 1
        else:
            category_answers[question_category]['false'] += 1
    return category_answers


def get_user_answers_per_difficulty(course_answers):
    difficulty_answers = {'Hard': {'right': 0, 'false': 0}, 'Easy': {'right': 0, 'false': 0}, 'Medium': {'right': 0, 'false': 0}}
    for answer in course_answers:
        question_difficulty = Question.objects.get(id=answer.question_id).question_level
        if question_difficulty not in difficulty_answers:
            difficulty_answers[question_difficulty] = {'right':0,'false':0}
        if answer.answered_answer_id == answer.right_answer_id:
            difficulty_answers[question_difficulty]['right'] += 1
        else:
            difficulty_answers[question_difficulty]['false'] += 1
    print('###DIFFICULTY###')
    print(difficulty_answers)
    print('###DIFFICULTY###')

    return difficulty_answers

##TODO Multiple categories
##TODO 0 Questions for some difficulties
##TODO Decompose
@csrf_exempt
def custom_quiz(request, course_id):
    category_name = request.POST['category']
    num_of_hard = int(request.POST['hard'])
    num_of_medium = int(request.POST['medium'])
    num_of_easy = int(request.POST['easy'])
    course_name = get_course_name(course_id)
    template = loader.get_template('quiz/custom_quiz.html')
    category_id = get_category_id_from_name(category_name)
    questions_list = get_category_questions(category_id)
    final_questions_list = []
    hard_questions = get_questions_by_difficulty(questions_list,'Hard',num_of_hard)
    final_questions_list.extend(hard_questions)
    medium_questions = get_questions_by_difficulty(questions_list,'Medium',num_of_hard)
    final_questions_list.extend(medium_questions)
    easy_questions = get_questions_by_difficulty(questions_list,'Easy',num_of_hard)
    true_num_hard = len(hard_questions)
    true_num_medium = len(medium_questions)
    true_num_easy = len(easy_questions)
    total_number_of_questions = true_num_hard + true_num_medium + true_num_easy
    final_questions_list.extend(easy_questions)
    random.shuffle(final_questions_list)
    questions_dict = {}  ## Will have muliple Question Text and Question Answers
    for question in final_questions_list:
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
    context = {
    'custom_category' : category_name,
    'true_num_hard' : true_num_hard,
    'true_num_medium' : true_num_medium,
    'true_num_easy' : true_num_easy,
    'total_questions': total_number_of_questions,
    'course_id': course_id,
    'category_id':category_id,
    'questions_dict':questions_dict,
    'course_name': course_name,
}
    return HttpResponse(template.render(context, request))

##TODO Decompose
@csrf_exempt
def auto_generated(request, course_id):
    total_number_of_questions = 20 ##TODO Change
    course_name = get_course_name(course_id)
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
    'course_name': course_name,
}
    return HttpResponse(template.render(context, request))


##TODO Decompose
def answers(request,user_id,course_id):
    marked_answers_from_quiz = {}
    quiz_checked = {}
    for arg in request.POST:
        if arg != 'csrfmiddlewaretoken':
            marked_answers_from_quiz[arg] = request.POST[arg]
    quiz = add_answered_quiz()
    quiz_checked = check_answer_to_questions(course_id, marked_answers_from_quiz,user_id,quiz.id)
    template = loader.get_template('quiz/answers_page.html')
    context = {
        'questions_dict': quiz_checked,
        'course_id': course_id,
    }
    return HttpResponse(template.render(context, request))


def teacher(request):
    courses_list = Course.objects.all()
    template = loader.get_template('quiz/teacher_view.html')
    context = {
        'courses_list': courses_list,
    }
    return HttpResponse(template.render(context, request))

def teacher_add_course(request):
    template = loader.get_template('quiz/add_course.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def course_added(request):
    new_course_name = request.POST['course_name']
    new_course_desc = request.POST['course_desc']
    new_course = add_course(new_course_name,new_course_desc)
    new_course_id = new_course.id
    template = loader.get_template('quiz/course_added.html')
    context = {
    'course_name': new_course_name,
    'course_desc': new_course_desc,
    'new_course': new_course,
    'course_id': new_course_id,
    }
    return HttpResponse(template.render(context, request))

## CSV Structure: category, cat_desc, question_text, pub_date,question_level, answer_1_text, answer_1_is_right, answer_1_explanation, answer_2_text, answer_2_is_right, answer_2_explanation, answer_3_text, answer_3_is_right, answer_3_explanation,answer_4_text, answer_4_is_right, answer_4_explanation,
##TODO Decompose, Add Uploader, and add functionality of n' answers
##TODO Add date as NOW time not not deal with formats.
def parse_csv(request, course_id):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES['myfile']
    else:
        form = UploadFileForm()

    course = Course.objects.get(id=course_id)
    file_data = file.read().decode("utf-8")
    lines = []
    lines = file_data.split("\n")

    for line in lines:
        row = line.split(",")
        if(row[0]!=''):
            category_id = get_category_id_from_name(row[0])
            if category_id==-1:
                new_category = add_category(row[0], row[1], course)
                new_question = add_question(row[2], course, row[3], row[4], new_category)
            else:
                category = Category.objects.get(id=category_id)
                new_question = add_question(row[2], course, row[3], row[4], category)
            for i in range(0,4):
                x = 3*i
                new_answer = add_answer(new_question, row[5+x],row[7+x],row[6+x])

    template = loader.get_template('quiz/questions_added.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def add_questions_csv(request, course_id):
    template = loader.get_template('quiz/add_questions.html')
    context = {
            'course_id': course_id,
    }
    return HttpResponse(template.render(context,request))

def index(request):
    courses_list = Course.objects.all()
    print (Course.objects.all())
    template = loader.get_template('quiz/index.html')
    context = {
        'courses_list': courses_list,
    }
    return HttpResponse(template.render(context, request))


###### Functions without Requests & Templates

def get_category_id_from_name(category_name):
    print (category_name)
    try:
        category_list = Category.objects.filter(category_name=category_name)
        return category_list[0].id
    except:
        return -1

def get_course_name(course_id):
    course = Course.objects.get(id = course_id)
    return course.course_name

def get_category_questions(category_id):
    category_questions_list = Question.objects.filter(category_id=category_id)
    if category_questions_list is None:
        return None
    return category_questions_list

def get_course_questions(course_id):
    course_question_list = Question.objects.filter(course_id=course_id)
    return course_question_list

def get_questions_by_difficulty(question_list,difficulty,num_of_questions):
    questions_by_difficulty = []
    for question in question_list:
        if question.question_level == difficulty:
            print('IN QUESTION DIFFICULTY' +str(difficulty))
            questions_by_difficulty.append(question)
    # TODO check greater between num_of_questions and actual quesions exist
    random.shuffle(questions_by_difficulty)
    questions_for_quiz = questions_by_difficulty[:num_of_questions]
    return questions_for_quiz

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

def add_user_answer(user_id,question_id,answered_answer_id,right_answer_id,quiz_id,course_id):
    new_user_answer = User_Answer(question_id = question_id, user = user_id, answered_answer_id = answered_answer_id, right_answer_id = right_answer_id,quiz_id = quiz_id,course_id = course_id)
    new_user_answer.save()

def add_answered_quiz():
    new_answered_quiz = Answered_Quiz()
    new_answered_quiz.save()
    return new_answered_quiz


def check_answer_to_questions(course_id, marked_answers_from_quiz, user_id,quiz_id):
    print (marked_answers_from_quiz)
    quiz_checked = {}
    course_questions_list = Question.objects.filter(course_id=course_id)
    for answered_question in marked_answers_from_quiz:
        for quiz_question in course_questions_list:
            if str(answered_question) == str(quiz_question.question_text):
                questions_answers_list = Answer.objects.filter(question_id=quiz_question.id)
                for answer in questions_answers_list:
                    if str(answer.is_right) == 'true' or str(answer.is_right) == ' true':
                        right_answer = answer
                    if answer.answer_text == marked_answers_from_quiz[answered_question]:
                        answered_answer_id = answer.id
                add_user_answer(user_id,quiz_question.id,answered_answer_id,right_answer.id,quiz_id,course_id)
                print ("user_id " + str(user_id))
                print ("question " + str(quiz_question.id))
                print ("answered_answer_id " + str(answered_answer_id))
                print ("right_answer_id " + str(right_answer.id))
                quiz_checked[quiz_question.question_text] = {'student_answer':marked_answers_from_quiz[answered_question],
                                                       'correct_answer':right_answer.answer_text}
    return quiz_checked

def jqueryserver(request):
    print ("in jqueryserver")
    response_string="hello"
    if request.method == 'GET':
        if request.is_ajax()== True:
            return HttpResponse(response_string,mimetype='text/plain')
