from django.contrib import admin
from .models import Survey, Question, Response, Answer

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(Answer)