from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Question, Course, Answer

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def course_question(request, course_id):
    course_questions_list = Question.objects.filter(course_id=course_id)
    questions_dict = {}  ## Will have muliple Question Text and Question Answers

    for question in course_questions_list:
        #question_answers_list = [] ##Has answers for one question only
        questions_answers_list = Answer.objects.filter(question_id=question.id)
        questions_dict[question.question_text] = questions_answers_list
        #for answer in questions_answers_list:
        #    question_answers_list.append(answer.answer_text)
        #questions_dict_arr.append({question.question_text:question_answers_list})


    template = loader.get_template('quiz/course_questions.html')
    context = {
        'questions_dict': questions_dict,
    }
    return HttpResponse(template.render(context, request))

def index(request):
    courses_list = Course.objects.all()
    template = loader.get_template('quiz/index.html')
    context = {
        'courses_list': courses_list,
    }
    return HttpResponse(template.render(context, request))
