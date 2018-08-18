from django.contrib import admin

# Register your models here.

from .models import Course

admin.site.register(Course)

from .models import Category

admin.site.register(Category)

from .models import Question

admin.site.register(Question)

from .models import Answer

admin.site.register(Answer)

from .models import User_Answer

admin.site.register(User_Answer)

from .models import Answered_Quiz

admin.site.register(Answered_Quiz)
