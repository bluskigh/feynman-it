from datetime import date
from calendar import Calendar

from django.db.models import Q

from main.models import Note

today = date.today()
calendar = Calendar()
calendar = calendar.monthdayscalendar(today.year, today.month)
yq = Q(created__year=today.year)
mq = Q(created__month=today.month)

# dq is going to be custom to day in iteration
for mi, week in enumerate(calendar):
    for si, day in enumerate(week):
        if day != 0:
            dq = Q(created__day=day)
            notes = Note.objects.filter(yq&mq&dq)
            calendar[mi][si] = (day, len(notes))
        else:
            calendar[mi][si] = None
print(calendar)
