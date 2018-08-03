from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('course/<int:course_id>/questions', views.course_question, name='course_question'),
    path('course/<int:course_id>/build_quiz', views.quiz_builder, name='course_categories'),
    path('custom_quiz/<int:course_id>/', views.custom_quiz, name='custom_quiz'),
    path('course/<int:course_id>/progress', views.progress, name='progress'),
    path('course/<int:course_id>/answers', views.answers, name='answers')

]
