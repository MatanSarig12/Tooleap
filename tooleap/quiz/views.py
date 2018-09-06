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
from collections import namedtuple
from django.contrib.auth.models import User
from datetime import datetime
from datetime import timedelta
import math
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

def get_unique_students_with_answers_in_course(course_id):
    course_user_answers = User_Answer.objects.filter(course_id=course_id)
    unique_users_array = []
    user_exists = 0
    if len(course_user_answers) > 0:
        unique_users_array.append(course_user_answers[0].user)
        for course_user_answer in course_user_answers:
            user_exists = 0
            for unique_user in unique_users_array:
                if unique_user == course_user_answer.user:
                    user_exists = 1
            if user_exists == 0:
                unique_users_array.append(course_user_answer.user)

    return unique_users_array

def check_unique_students_with_answers_in_course(course_id):
    course_user_answers = User_Answer.objects.filter(course_id=course_id)
    unique_users_array = []
    user_exists = 0
    if len(course_user_answers) > 0:
        unique_users_array.append(course_user_answers[0].user)
        for course_user_answer in course_user_answers:
            user_exists = 0
            for unique_user in unique_users_array:
                if unique_user == course_user_answer.user:
                    user_exists = 1
            if user_exists == 0:
                unique_users_array.append(course_user_answer.user)

    return len(unique_users_array)

def get_number_of_course_questions(course_id):
    course_questions = get_course_questions(course_id)
    return len(course_questions)

def get_user_name(user_id):
    user = User.objects.get(id = user_id)
    return user.username

def get_user_last_login(user_id):
    user = User.objects.get(id = user_id)
    return user.last_login

def get_user_percentile(user_id, course_id):
    print ('in function')
    user_details = get_users_details(course_id)
    grades = []
    this_user_grade = 0
    for user in user_details:
        if user_id == user:
            this_user_grade = user_details[user]['right_percentage']
        else:
            grades.append(user_details[user]['right_percentage'])
    sorted_grades = sorted(grades)
    user_index = 1
    for grade in sorted_grades:
        if this_user_grade >= grade:
            return user_index, len(sorted_grades)+1
        else:
            user_index+=1
    return user_index, len(sorted_grades)+1

def get_questions_details(course_id):
    all_course_questions = Question.objects.filter(course_id=course_id)
    right_answer_counter = 0
    wrong_answer_counter = 0
    course_answers_details = {}
    all_question_user_answers = {}
    for question in all_course_questions:
        question_text = question.question_text
        question_category = question.category_id.category_name
        question_uploaded = question.pub_date
        all_question_user_answers = User_Answer.objects.filter(question_id=question.id)
        right_answer_counter = 0
        wrong_answer_counter = 0
        for user_answer in all_question_user_answers:
            if(user_answer.answered_answer_id == user_answer.right_answer_id):
                right_answer_counter+=1
            else:
                wrong_answer_counter+=1

        if(right_answer_counter+wrong_answer_counter == 0):
            course_answers_details[question.id] = {'question_text': question_text,  'right_answers': right_answer_counter, 'wrong_answers':wrong_answer_counter, 'right_percentage':0, 'question_uploaded': question_uploaded, 'question_category':question_category, 'question_level':question.question_level}
        else:
            course_answers_details[question.id] = {'question_text': question_text, 'right_answers': right_answer_counter, 'wrong_answers':wrong_answer_counter, 'right_percentage':round((right_answer_counter/(right_answer_counter+wrong_answer_counter))*100,2), 'question_uploaded': question_uploaded, 'question_category':question_category, 'question_level':question.question_level}

    return course_answers_details


def get_users_details(course_id):
    unique_users_array = get_unique_students_with_answers_in_course(course_id)
    user_details_dict = {}

    for unique_user in unique_users_array:
        course_answers = User_Answer.objects.filter(course_id=course_id,user=unique_user)
        user_name = get_user_name(unique_user)
        answers_per_difficulty = get_user_answers_per_difficulty(course_answers)
        hard_right = answers_per_difficulty['Hard'].get('right')
        hard_false = answers_per_difficulty['Hard'].get('false')
        medium_right = answers_per_difficulty['Medium'].get('right')
        medium_false = answers_per_difficulty['Medium'].get('false')
        easy_right = answers_per_difficulty['Easy'].get('right')
        easy_false = answers_per_difficulty['Easy'].get('false')
        all_questions = hard_right+medium_right+easy_right+hard_false+medium_false+easy_false
        all_right = hard_right+medium_right+easy_right
        latest_quiz = get_last_user_quiz(unique_user)
        user_details_dict[unique_user] = {'user_name': user_name, 'right_answers': all_right, 'wrong_answers': all_questions - all_right, 'right_percentage':round((all_right/all_questions)*100,2), 'latest_quiz': latest_quiz}

    return user_details_dict


def get_last_user_quiz(user_id):
    user_answers = User_Answer.objects.filter(user=user_id)
    most_recent_quiz = user_answers[0].quiz_time

    for user_answer in user_answers:
        curr_quiz = user_answer.quiz_time
        if most_recent_quiz < curr_quiz:
            most_recent_quiz = curr_quiz

    return most_recent_quiz


def get_latest_quesiton_timestamp(course_answers):
    try:
        most_recent_upload = Question.objects.get(id=course_answers[0].question_id).pub_date
        print (most_recent_upload)
        for user_answer in course_answers:
            curr_question = Question.objects.get(id=user_answer.question_id)
            if most_recent_upload < curr_question.pub_date:
                most_recent_upload = curr_question.pub_date
    except:
        most_recent_upload = None
    return most_recent_upload


def teacher_progress_view(request, course_id):
    course_categories = Category.objects.filter(course_id=course_id)
    number_of_students_that_started_answering_questions_in_course = check_unique_students_with_answers_in_course(course_id)
    number_of_course_questions = get_number_of_course_questions(course_id)
    course_name = get_course_name(course_id)
    users_details_dict = {}
    users_details_dict = get_users_details(course_id)
    course_answers = User_Answer.objects.filter(course_id=course_id)
    last_quesions_upload = get_latest_quesiton_timestamp(course_answers)
    answers_per_category = get_user_answers_per_category(course_answers)
    course_answers_details = get_questions_details(course_id)
    template = loader.get_template('quiz/teacher_progress_view.html')
    context = {
            'course_categories': course_categories,
            'course_id': course_id,
            'course_name': course_name,
            'number_of_students_that_started_answering_questions_in_course': number_of_students_that_started_answering_questions_in_course,
            'number_of_course_questions': number_of_course_questions,
            'users_details_dict': users_details_dict,
            'answers_per_category': answers_per_category,
            'last_quesions_upload': last_quesions_upload,
            'course_answers_details': course_answers_details,
    }
    return HttpResponse(template.render(context,request))

def question_distribution(request, course_id, question_id):

    question_dict,answers_right_precentage =  get_answers_distribution_per_question(question_id)

    answer_1_text = answers_right_precentage[0][0]
    answer_1_percentage = answers_right_precentage[0][1]
    answer_2_text = answers_right_precentage[1][0]
    answer_2_percentage = answers_right_precentage[1][1]
    answer_3_text = answers_right_precentage[2][0]
    answer_3_percentage = answers_right_precentage[2][1]
    answer_4_text = answers_right_precentage[3][0]
    answer_4_percentage = answers_right_precentage[3][1]

    template = loader.get_template('quiz/answers_distribution_per_question.html')

    context = {
            'question_dict': question_dict,
            'answer_1_text': answer_1_text,
            'answer_1_percentage': answer_1_percentage,
            'answer_2_text': answer_2_text,
            'answer_2_percentage': answer_2_percentage,
            'answer_3_text': answer_3_text,
            'answer_3_percentage': answer_3_percentage,
            'answer_4_text': answer_4_text,
            'answer_4_percentage': answer_4_percentage,
            }
    return HttpResponse(template.render(context,request))



def get_answers_distribution_per_question(question_id):
    question = Question.objects.get(id=question_id)
    question_dict = {'text':question.question_text,
                    'level':question.question_level,
                    'category':question.category_id.category_name}
    answers = Answer.objects.filter(question=question_id)
    answers_right_precentage = []
    for answer in answers:
        user_answers = User_Answer.objects.filter(question_id=question_id,answered_answer_id=answer.id)
        answers_right_precentage.append([answer.answer_text,len(user_answers)])

    return question_dict,answers_right_precentage

def progress(request, user_id, course_id):
    course_categories = Category.objects.filter(course_id=course_id)
    course_questions = Question.objects.filter(course_id=course_id)
    total_number_of_course_questions = len(course_questions)
    course_answers = User_Answer.objects.filter(course_id=course_id,user=user_id)
    answers_per_quiz = get_user_answers_per_quiz(course_answers)
    answers_per_category = get_user_answers_per_category(course_answers)
    course_name = get_course_name(course_id)
    answers_per_difficulty = get_user_answers_per_difficulty(course_answers)
    hard_right = answers_per_difficulty['Hard'].get('right')
    hard_false = answers_per_difficulty['Hard'].get('false')
    medium_right = answers_per_difficulty['Medium'].get('right')
    medium_false = answers_per_difficulty['Medium'].get('false')
    easy_right = answers_per_difficulty['Easy'].get('right')
    easy_false = answers_per_difficulty['Easy'].get('false')
    all_right = hard_right+medium_right+easy_right
    all_questions = hard_right+medium_right+easy_right+hard_false+medium_false+easy_false
    tooleap_baby = False
    tooleap_master = False
    tooleap_not_started= False
    tooleap_student = False

    if total_number_of_course_questions == 0:
        tooleap_not_started = True
    elif all_right/total_number_of_course_questions <= 0.33:
        tooleap_baby = True
    elif all_right/total_number_of_course_questions <= 0.66:
        tooleap_student = True
    else:
        tooleap_master = True

    is_answered = 0
    unique_user_questions = []
    if len(course_answers) != 0:
        unique_user_questions.append(course_answers[0].question_id)
        for user_question in course_answers:
            is_answered = 0
            for unique in unique_user_questions:
                if unique ==  user_question.question_id:
                    is_answered = 1

            if is_answered == 0:
                unique_user_questions.append(user_question.question_id)

    user_unsolved_questions_count =len(course_questions) - len(unique_user_questions)
    percentile, total_users = get_user_percentile(user_id, course_id)

    template = loader.get_template('quiz/progress.html')
    dates = ['2018-01-01','2018-01-02']
    arr_right_percentage = []
    for quiz in answers_per_quiz:
        right_answer_counter = answers_per_quiz[quiz]['right']
        wrong_answer_counter = answers_per_quiz[quiz]['false']
        arr_right_percentage.append(round((right_answer_counter/(right_answer_counter+wrong_answer_counter))*100,2))
    user_wrong_answers = get_user_wrong_answers(user_id,course_id)
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
            'all_right': all_right,
            'all_questions': all_questions,
            'total_number_of_course_questions': total_number_of_course_questions,
            'user_unsolved_questions_count': user_unsolved_questions_count,
            'percentile': percentile,
            'total_users': total_users,
            'tooleap_baby': tooleap_baby,
            'tooleap_master': tooleap_master,
            'tooleap_not_started': tooleap_not_started,
            'tooleap_student': tooleap_student,
            'arr_right_percentage':arr_right_percentage,
            'arr_user_wrong_answers':user_wrong_answers,
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

def get_user_wrong_answers(user_id,course_id):
    user_answers = User_Answer.objects.filter(user=user_id,course_id=course_id)
    user_agg_answers = {}
    for question in user_answers:
        if question.question_id not in user_agg_answers:
            user_agg_answers[question.question_id] = {'right':0,'false':0}
        if question.answered_answer_id == question.right_answer_id:
            user_agg_answers[question.question_id]['right'] += 1
        else:
            user_agg_answers[question.question_id]['false'] += 1
    user_wrong_answers = []
    for agg_question in user_agg_answers:
        if user_agg_answers[agg_question]['right'] == 0:
            question_details = Question.objects.get(id=agg_question)
            user_wrong_answers.append({'question_text':question_details.question_text,
                    'wrong_answers':user_agg_answers[agg_question]['false'],
                    'level':question_details.question_level,
                    'category':question_details.category_id.category_name,
                    'question_id':agg_question})
    return user_wrong_answers

def get_user_answers_per_category(course_answers):
    category_answers = {}
    for answer in course_answers:
        question_text = Question.objects.get(id=answer.question_id).question_text
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

    return difficulty_answers

##TODO Multiple categories
##TODO 0 Questions for some difficulties
##TODO Decompose
@csrf_exempt
def custom_quiz(request, course_id):
    categories = []
    course_categories = Category.objects.filter(course_id=course_id)
    for course_category in course_categories:
        try:
            categories.append(request.POST[course_category.category_name])
        except:
            continue
    num_of_hard = int(request.POST['hard'])
    num_of_medium = int(request.POST['medium'])
    num_of_easy = int(request.POST['easy'])
    course_name = get_course_name(course_id)
    template = loader.get_template('quiz/custom_quiz.html')
    final_questions_list = []
    total_number_of_easy_questions = 0
    total_number_of_medium_questions = 0
    total_number_of_hard_questions = 0
    for category in categories:
        category_id = get_category_id_from_name(category)
        questions_list = get_category_questions(category_id)
        hard_questions = get_questions_by_difficulty(questions_list,'Hard',num_of_hard)
        final_questions_list.extend(hard_questions)
        medium_questions = get_questions_by_difficulty(questions_list,'Medium',num_of_hard)
        final_questions_list.extend(medium_questions)
        easy_questions = get_questions_by_difficulty(questions_list,'Easy',num_of_hard)
        final_questions_list.extend(easy_questions)
        total_number_of_easy_questions += len(easy_questions)
        total_number_of_medium_questions += len(medium_questions)
        total_number_of_hard_questions += len(hard_questions)
    total_number_of_questions = total_number_of_easy_questions + total_number_of_medium_questions + total_number_of_hard_questions
    random.shuffle(final_questions_list)
    questions_dict = {}  ## Will have muliple Question Text and Question Answers
    for question in final_questions_list:
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
    if(categories==[]):
        category_id =0;

    if(questions_dict == {}):
        no_questions = 0;
    else:
        no_questions = 1
    context = {
    'custom_categories' : ','.join(categories),
    'true_num_hard' : total_number_of_hard_questions,
    'true_num_medium' : total_number_of_medium_questions,
    'true_num_easy' : total_number_of_easy_questions,
    'total_questions': total_number_of_questions,
    'course_id': course_id,
    'category_id':category_id,
    'questions_dict':questions_dict,
    'course_name': course_name,
    'no_questions': no_questions,
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
    quiz_checked,right_questions,total_questions = check_answer_to_questions(course_id, marked_answers_from_quiz,user_id,quiz.id)
    template = loader.get_template('quiz/answers_page.html')
    context = {
        'questions_dict': quiz_checked,
        'course_id': course_id,
        'right_questions':right_questions,
        'total_questions': total_questions
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def smart_quiz(request,course_id,user_id):
    total_number_of_questions = 20 ##TODO Change
    course_name = get_course_name(course_id)
    user_wrong_answers = get_user_wrong_answers(user_id,course_id)
    template = loader.get_template('quiz/smart_quiz.html')
    course_questions_list = []
    num_of_questions = 0
    for question in user_wrong_answers:
        course_questions_list.append(Question.objects.get(id=question['question_id']))
        num_of_questions +=1
        if num_of_questions == total_number_of_questions:
            break
    random.shuffle(course_questions_list)
    questions_dict = {}  ## Will have muliple Question Text and Question Answers
    for question in course_questions_list:
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
    if questions_dict == {}:
        no_questions = False
    else:
        no_questions = True
    print(questions_dict)
    print(no_questions)
    context = {
    'course_id': course_id,
    'questions_dict':questions_dict,
    'course_name': course_name,
    'no_questions': no_questions,
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
                new_question = add_question(row[2], course, datetime.now(), row[4], new_category)
            else:
                category = Category.objects.get(id=category_id)
                new_question = add_question(row[2], course, datetime.now(), row[4], category)
            for i in range(0,4):
                x = 3*i
                new_answer = add_answer(new_question, row[5+x],row[7+x],row[6+x])

    template = loader.get_template('quiz/questions_added.html')
    context = {
            'course_id': course_id,
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
    template = loader.get_template('quiz/index.html')
    context = {
        'courses_list': courses_list,
    }
    return HttpResponse(template.render(context, request))


###### Functions without Requests & Templates

def get_category_id_from_name(category_name):
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
    quiz_checked = {}
    course_questions_list = Question.objects.filter(course_id=course_id)
    right_questions = 0
    for answered_question in marked_answers_from_quiz:
        for quiz_question in course_questions_list:
            if str(answered_question) == str(quiz_question.question_text):
                questions_answers_list = Answer.objects.filter(question_id=quiz_question.id)
                for answer in questions_answers_list:
                    if str(answer.is_right) == 'true' or str(answer.is_right) == ' true' or str(answer.is_right) == 'TRUE':
                        right_answer = answer
                        if right_answer.answer_text == marked_answers_from_quiz[answered_question]:
                            right_questions += 1
                    if answer.answer_text == marked_answers_from_quiz[answered_question]:
                        answered_answer_id = answer.id
                add_user_answer(user_id,quiz_question.id,answered_answer_id,right_answer.id,quiz_id,course_id)
                quiz_checked[quiz_question.question_text] = {'student_answer':marked_answers_from_quiz[answered_question],
                                                       'correct_answer':right_answer.answer_text,'answer_explanation':right_answer.answer_explanation}
                break
    return quiz_checked,right_questions,len(marked_answers_from_quiz)

def jqueryserver(request):
    print ("in jqueryserver")
    response_string="hello"
    if request.method == 'GET':
        if request.is_ajax()== True:
            return HttpResponse(response_string,mimetype='text/plain')
