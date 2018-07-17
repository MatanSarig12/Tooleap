from django.urls import path

from . import views

urlpatterns = [
     path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/

    path('course/<int:course_id>/questions', views.course_question, name='course_question'),
    path('course/<int:course_id>/categories', views.course_categories, name='course_categories'),

]
