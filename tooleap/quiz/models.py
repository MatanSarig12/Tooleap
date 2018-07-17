from django.db import models

# Create your models here.

class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_desc = models.CharField(max_length=500)
    def __str__(self):
        return self.course_name

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_desc = models.CharField(max_length=500)
    course_id = models.ForeignKey(Course,  on_delete=models.CASCADE)
    def __str__(self):
        return self.category_name

class Question(models.Model):
    question_text = models.CharField(max_length=500)
    course_id = models.ForeignKey(Course,  on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')
    question_level = models.CharField(max_length=20)
    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=250)
    answer_explanation = models.CharField(max_length=500)
    is_right = models.CharField(max_length=25) ### TODO: Change to Boolean
    def __str__(self):
        return self.answer_text
