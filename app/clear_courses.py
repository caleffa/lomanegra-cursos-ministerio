from cursos.models import QuestionnaireOption, QuestionnaireQuestion, Questionnaire, SegmentTracking, CourseEnrollment, DownloadableDocumentTracking, UploadedDocumentTracking

for qo in QuestionnaireOption.objects.all():
    qo.delete()

for qq in QuestionnaireQuestion.objects.all():
    qq.delete()

for q in Questionnaire.objects.all():
    q.delete()

for dd in DownloadableDocumentTracking.objects.all():
    dd.delete()

for ud in UploadedDocumentTracking.objects.all():
    ud.delete()

for st in SegmentTracking.objects.all():
    st.delete()

for ce in CourseEnrollment.objects.all():
    ce.delete() 
