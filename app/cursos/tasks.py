from celery import shared_task

@shared_task
def test_celery(s="hello world"):
    print(s)
    return s


