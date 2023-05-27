from django.contrib import admin
import nested_admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Enrollment, Submission

class ChoiceInline(nested_admin.NestedTabularInline):
    model = Choice
    extra = 2

class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [ChoiceInline]
    extra = 5

class LessonInline(nested_admin.NestedStackedInline):
    model = Lesson
    inlines = [QuestionInline]
    extra = 5

class CourseAdmin(nested_admin.NestedModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

admin.site.register(Course, CourseAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Enrollment)
admin.site.register(Submission)
