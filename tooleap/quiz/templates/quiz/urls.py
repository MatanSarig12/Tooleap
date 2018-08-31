from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('course/<int:course_id>/questions', views.course_question, name='course_question'),
    path('course/<int:course_id>/build_quiz', views.quiz_builder, name='course_categories'),
    path('custom_quiz/<int:course_id>/', views.custom_quiz, name='custom_quiz'),
    path('course/<int:user_id>/<int:course_id>/progress', views.progress, name='progress'),
    path('course/<int:user_id>/<int:course_id>/answers', views.answers, name='answers'),
    path('auto_generated/<int:course_id>/', views.auto_generated, name='auto_generated'),
    path('teacher/', views.teacher, name='teacher'),
    path('teacher/course/<int:course_id>/progress', views.teacher_progress_view, name='teacher_progress_view'),
    path('teacher/add_course/', views.teacher_add_course, name='teacher_add_course'),
    path('teacher/add_course/course_added', views.course_added, name='course_added'),
    path('teacher/course/<int:course_id>/parse/',views.parse_csv, name ='csv_parse'),
    path('teacher/course/<int:course_id>/add_questions',views.add_questions_csv, name ='add_questions'),
]
