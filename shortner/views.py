from django.http import HttpResponseRedirect
from iommi import (
    Column,
    Page,
    Table,
    html,
    Form,
    Action,
)
from iommi.admin import Admin
from iommi.table import LAST

from shortner.models import Entry


class ShortnerAdmin(Admin):
    class Meta:
        parts__list_shortner_entry__columns__short = Column(
            cell__url=lambda value, **_: f'/s/{value}',
            after=0,
        )


class EntryTable(Table):
    edit = Column.edit(after=LAST)
    delete = Column.delete(after=LAST)

    class Meta:
        auto__model = Entry
        columns__short = dict(
            cell__url=lambda value, **_: f'/s/{value}',
            after=0,
        )


def entries(request):
    return EntryTable(
        actions__create=Action.button(tag='a', attrs__href='create'),
    )


def create(request):
    return Form.create(
        auto__model=Entry,
        fields__creator__initial=request.user,
        fields__use_count__include=False,
        fields__approver__include=False,
    )


def edit(request, short):
    return Form.edit(
        auto__instance=Entry.objects.get(short=short),
        fields__use_count__editable=False,
    )


def delete(request, short):
    return Form.delete(
        auto__instance=Entry.objects.get(short=short),
    )


def go(request, short):
    entry = Entry.objects.get(short=short)

    if not entry.approver:
        class ErrorPage(Page):
            header = html.h1('Not approved yet...')

        return ErrorPage()

    entry.use_count += 1
    entry.save(update_fields=['use_count'])

    return HttpResponseRedirect(entry.url)
