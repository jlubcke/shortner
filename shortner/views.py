from django.http import HttpResponseRedirect
from iommi import Column
from iommi.admin import Admin

from shortner.models import Entry


class ShortnerAdmin(Admin):
    class Meta:
        parts__list_shortner_entry__columns__short = Column(
            cell__url=lambda value, **_: f'/s/{value}',
            after=0,
        )


def go(request, short):
    entry = Entry.objects.get(short=short)
    entry.use_count += 1
    entry.save(update_fields=['use_count'])

    return HttpResponseRedirect(entry.url)
