from django.contrib import admin
from .models import Exam, StudentExam, Option, Question, Response, CapturedImage

class OptionInline(admin.TabularInline):
    model = Option
    extra = 3

class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline, ResponseInline]
    list_display = ("question_text", "exam", "correct_option",)
    list_filter = ("exam",)
    search_fields = ("question_text",)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "correct_option":
            question_id = request.resolver_match.kwargs.get('object_id')
            if question_id:
                kwargs["queryset"] = Option.objects.filter(question=question_id)
            else:
                kwargs["queryset"] = Option.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ("title", "get_questions_count")
    list_filter = ("duration",)
    search_fields = ("title",)
    exclude = ("creator",)

    def get_questions_count(self, obj):
        return obj.questions.count()

    get_questions_count.short_description = "Number of Questions"

    def get_inline_instances(self, request, obj=None):
        if obj:
            return [inline(self.model, self.admin_site) for inline in self.inlines]
        return []

    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.creator = request.user
        super().save_model(request, obj, form, change)

@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "start_time", "end_time")
    list_filter = ("exam", "student", "start_time", "end_time")

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("text", "question")
    list_filter = ("question",)
    search_fields = ("text",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "question":
            kwargs["queryset"] = Option.objects.filter(question__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("student_exam", "question", "selected_option", "is_correct")
    list_filter = ("student_exam", "question", "is_correct")
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(CapturedImage)
class CapturedImageAdmin(admin.ModelAdmin):
    list_display = ("get_exam_student_username", "image_data", "is_match")
    list_filter = ("student_exam__exam", "is_match")
    search_fields = ("student_exam__student__username",)
    readonly_fields = ("image_data",) 

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def get_exam_student_username(self, obj):
        return obj.student_exam.student.username + '__' + obj.student_exam.exam.title

    get_exam_student_username.short_description = "Exam Student Username"