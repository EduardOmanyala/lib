from django.contrib import admin
from .models import Question, Kasneb, Course, Subject, MyCourses, MySubjects, Book, Docs, MMFProvider, MMFMonthlyRate

admin.site.register(Book)
admin.site.register(Docs)
admin.site.register(MMFProvider)
admin.site.register(MMFMonthlyRate)
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'year', 'question_num', 'type', 'paper_type']
    list_filter = ['subject', 'year', 'type', 'paper_type']
    search_fields = ['subject', 'text']
    ordering = ['year', 'subject', 'question_num']


@admin.register(Kasneb)
class KasnebAdmin(admin.ModelAdmin):
    list_display = ['subject', 'course', 'year', 'month']
    list_filter = ['subject', 'course', 'year', 'month']
    search_fields = ['subject', 'course', 'text']
    ordering = ['year', 'course', 'subject']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'course']
    list_filter = ['course']
    search_fields = ['name', 'code']
    ordering = ['course', 'name']


@admin.register(MyCourses)
class MyCoursesAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['user__email', 'course__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(MySubjects)
class MySubjectsAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'course', 'created_at']
    list_filter = ['course', 'subject', 'created_at']
    search_fields = ['user__email', 'subject__name', 'course__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
