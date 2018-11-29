from celery import shared_task
from .models import blacklist
from datetime import datetime, timezone, timedelta

@shared_task
def get_thirty_day_labels():
    labels = []
    today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    for day in range(30)[::-1]:
        date = today - timedelta(days=day)
        label = date.strftime('%Y-%m-%d')
        labels.append(label)
    return labels


@shared_task
def get_thirty_day_data():
    data = []
    today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    for day in range(30)[::-1]:
        from_date = today - timedelta(days=day)
        to_date = today - timedelta(days=day-1)
        count = blacklist.objects.filter(datetime__gte=from_date, datetime__lte=to_date).count()
        data.append(count)
    return data

#@shared_task
#def get_thirty_day_data():
#    alldata = {}
#    today = datetime.now(timezone(timedelta(hours=+9), 'JST'))
#    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
#    for src in blacklist.SOURCES:
#        data = []
#        for day in range(30)[::-1]:
#            from_date = today - timedelta(days=day)
#            to_date = today - timedelta(days=day-1)
#            count = blacklist.objects.filter(source=src[0], datetime__gte=from_date, datetime__lte=to_date).count()
#            data.append(count)
#        alldata[src[1]] = data
#    return alldata

