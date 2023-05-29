from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from .models import Course, Enrollment, Lesson, Question, Choice, Submission
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = User.objects.filter(username=username).exists()
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    return Enrollment.objects.filter(user=user, course=course).exists()


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


from django.contrib.auth.decorators import login_required

@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if not check_if_enrolled(user, course):
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))



def lesson_exam(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    return render(request, 'onlinecourse/lesson_exam.html', {'lesson': lesson})


@login_required
def submit_exam(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    print(f"Lesson ID: {lesson_id}")

    choices_ids = [int(key.split('_')[1]) for key in request.POST if key.startswith('choice_')]
    print(f"Choices IDs: {choices_ids}")
    correct_answers = 0
    enrollment = Enrollment.objects.get(user=request.user, course=lesson.course)

    # Create a submission instance
    submission = Submission(enrollment=enrollment)
    submission.save()

    incorrect_choices = []

    for choice_id in choices_ids:
        choice = get_object_or_404(Choice, id=choice_id)
        if choice.is_correct:
            correct_answers += 1
        else:
            incorrect_choices.append(choice.choice_text)
        # Save the choices selected by the user
        submission.choices.add(choice)

    # Calculate the grade
    total_questions = lesson.question_set.count()
    grade = (correct_answers / total_questions) * 100
    print(f"Total Questions: {total_questions}")
    print(f"Correct Answers: {correct_answers}")
    print(f"Grade: {grade}")

    # Save the grade to the submission
    submission.grade = grade
    submission.save()

    print(f"Incorrect Choices: {incorrect_choices}")
    print(f"Lesson: {lesson}")

    # Render result page
    return render(request, 'onlinecourse/exam_result_bootstrap.html',
                  {'grade': grade, 'incorrect_choices': incorrect_choices, 'lesson': lesson})


@login_required
def submit(request, course_id):
    if request.method == 'POST':
        user = request.user
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(Enrollment, user=user, course=course)

        submission = Submission.objects.create(enrollment=enrollment)

        for choice_id in request.POST.getlist('choices'):
            choice = get_object_or_404(Choice, id=choice_id)
            submission.choices.add(choice)

        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)
    else:
        # Return some response for GET requests
        pass


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)

    selected_choices = submission.choices.all()
    selected_ids = [choice.id for choice in selected_choices]

    total_grade = 0
    total_questions = course.question_set.count()
    correct_questions = 0
    for question in course.question_set.all():
        if question.choices.filter(id__in=selected_ids, is_correct=True).exists():
            total_grade += question.grade
            correct_questions += 1

    grade = (total_grade / total_questions) * 100

    pass_exam = grade >= 70  # Change this as per your passing grade

    correct_choices = []
    incorrect_choices = []
    for question in course.question_set.all():
        if question.choices.filter(id__in=selected_ids, is_correct=True).exists():
            correct_choices.append(question)
        else:
            incorrect_choices.append(question)

    context = {
        'course': course,
        'selected_ids': selected_ids,
        'grade': grade,
        'pass_exam': pass_exam,
        'correct_choices': correct_choices,
        'incorrect_choices': incorrect_choices,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
