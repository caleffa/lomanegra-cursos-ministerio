def reset_user_tracking(email):
	u = User.objects.get(email=email)
	SegmentTracking.objects.filter(user=u).delete()
	QuestionnaireOption.objects.filter(questionnaire_question__questionnaire__user=u).delete()
	QuestionnaireQuestion.objects.filter(questionnaire__user=u).delete()
	Questionnaire.objects.filter(user=u).delete()
	DownloadableDocumentTracking.objects.filter(user=u).delete()
	CourseEnrollment.objects.filter(user=u).delete()


# Reset all users tracking
#

SegmentTracking.objects.all().delete()

QuestionnaireOption.objects.all().delete()
QuestionnaireQuestion.objects.all().delete()
Questionnaire.objects.all().delete()

DownloadableDocumentTracking.objects.all().delete()

CourseEnrollment.objects.all().delete()
