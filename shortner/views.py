from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect
from iommi import (
    Column,
    Page,
    Table,
    html,
    Form,
    Action,
    Field,
)
from iommi.admin import Admin
from iommi.table import LAST

from shortner.models import Entry


def redirect_root(request):
    return HttpResponseRedirect('/entries/')


class EntryAdminTable(Table):
    class Meta:
        auto__model = Entry
        columns__short = dict(
            cell__url=lambda value, **_: f'/s/{value}',
            after=0,
        )
        columns__url__cell__url=lambda value, **_: value
        columns__edit = Column.edit(after=LAST)
        columns__delete = Column.delete(after=LAST)


@login_required
def entries(request):
    return EntryAdminTable(
        actions=dict(
            create=Action.button(tag='a', attrs__href='create'),
            logout=Action.button(tag='a', attrs__href='/logout/'),
        )
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
    return LoginForm()


def on_post(form, **_):
    if form.is_valid:
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
