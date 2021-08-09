from users.models import User
from .models import (SegmentTracking, QuestionnaireOption, QuestionnaireQuestion, Questionnaire,
                     DownloadableDocumentTracking, CourseEnrollment)
from tareas.models import TareaAlumno


def reset_user_tracking(email):
    u = User.objects.get(email=email)
    SegmentTracking.objects.filter(user=u).delete()
    QuestionnaireOption.objects.filter(questionnaire_question__questionnaire__user=u).delete()
    QuestionnaireQuestion.objects.filter(questionnaire__user=u).delete()
    Questionnaire.objects.filter(user=u).delete()
    DownloadableDocumentTracking.objects.filter(user=u).delete()
    TareaAlumno.objects.filter(estudiante=u).delete()
    CourseEnrollment.objects.filter(user=u).delete()


def reset_user_tracking_for_course(email, course):
    u = User.objects.get(email=email)
    SegmentTracking.objects.filter(user=u, video__course=course).delete()
    QuestionnaireOption.objects.filter(questionnaire_question__questionnaire__user=u,
                                       questionnaire_question__questionnaire__video__course=course).delete()
    QuestionnaireQuestion.objects.filter(questionnaire__user=u, questionnaire__video__course=course).delete()
    Questionnaire.objects.filter(user=u, video__course=course).delete()
    DownloadableDocumentTracking.objects.filter(user=u, document__video__course=course).delete()
    TareaAlumno.objects.filter(estudiante=u, tarea__segmento__course=course).delete()
    CourseEnrollment.objects.filter(user=u, course=course).delete()


def reset_course_tracking(course):
    SegmentTracking.objects.filter(video__course=course).delete()
    QuestionnaireOption.objects.filter(questionnaire_question__questionnaire__video__course=course).delete()
    QuestionnaireQuestion.objects.filter(questionnaire__video__course=course).delete()
    Questionnaire.objects.filter(video__course=course).delete()
    DownloadableDocumentTracking.objects.filter(document__video__course=course).delete()
    TareaAlumno.objects.filter(tarea__segmento__course=course).delete()
    CourseEnrollment.objects.filter(course=course).delete()
    