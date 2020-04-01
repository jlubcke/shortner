from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from iommi import (
    Action,
    Column,
    Field,
    Form,
    html,
    Page,
    Table,
)
from iommi.admin import Admin

from shortner.models import Entry


def redirect_root(request):
    return HttpResponseRedirect('/entries/')


class EntryTable(Table):
    class Meta:
        auto__model = Entry
        columns__short = dict(
            cell__url=lambda value, **_: f'/s/{value}',
        )
        columns__url__cell__url = (lambda value, **_: value)


class EntryAdminTable(EntryTable):
    edit = Column.edit()
    delete = Column.delete()


class EntryApproveTable(EntryTable):
    class Meta:
        title = 'Approvable entries'
        columns__select__include = True

        @staticmethod
        def auto__rows(table, **_):
            return Entry.objects.exclude(
                creator=table.get_request().user
            ).exclude(
                approver__isnull=False,
            )

        bulk__actions__submit = dict(
            include=True,
            attrs__value='Approve',
        )

        @staticmethod
        def bulk__actions__submit__post_handler(table, **_):
            table.bulk_queryset().update(approver=table.get_request().user)


@login_required
def entries(request):
    return Page(
        parts__admin_table=EntryAdminTable(
            actions=dict(
                create=Action.button(tag='a', attrs__href='create'),
                logout=Action.button(tag='a', attrs__href='/logout/'),
            ),
        ),
        parts__approve_table=EntryApproveTable()
    )


@login_required
def create(request):
    return Form.create(
        auto__model=Entry,
        fields__creator__initial=request.user,
        fields__use_count__include=False,
        fields__approver__include=False,
    )


@login_required
def edit(request, short):
    return Form.edit(
        auto__instance=Entry.objects.get(short=short),
        fields__use_count__editable=False,
    )


@login_required
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


def login(request):
    return Page(
        parts__form=LoginForm(),
        parts__set_focus=html.script(mark_safe('document.getElementById("id_username").focus();')),
    )


def on_post(form, **_):
    if form.is_valid():
        user = auth.authenticate(
            username=form.fields.username.value,
            password=form.fields.password.value,
        )

        if user is not None:
            request = form.get_request()
            auth.login(request, user)
            return HttpResponseRedirect(request.GET.get('next', '/'))

        form.errors.add('Unknown username or password')


class LoginForm(Form):
    username = Field()
    password = Field.password()

    class Meta:
        title = 'Login'
        actions__submit__post_handler = on_post


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')


class ShortnerAdmin(Admin):
    class Meta:
        parts__list_shortner_entry__columns__short = Column(
            cell__url=lambda value, **_: f'/s/{value}',
            after=0,
        )
