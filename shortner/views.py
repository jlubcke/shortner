import random
import string
from datetime import (
    datetime,
    timedelta,
)

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timesince import (
    timesince,
    timeuntil,
)
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


class LoginForm(Form):
    username = Field()
    password = Field.password()

    class Meta:
        title = 'Login'

        @staticmethod
        def actions__submit__post_handler(form, **_):
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


class LoginPage(Page):
    form = LoginForm()
    set_focus = html.script(mark_safe(
        'document.getElementById("id_username").focus();',
    ))


def login(request):
    return LoginPage()


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def redirect_root(request):
    return HttpResponseRedirect('/submit/')


def random_short():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def submit(request):
    class SubmitForm(Form):
        short = Field(
            initial=random_short(),
            is_valid=lambda parsed_data, **_: (
                not Entry.objects.filter(short=parsed_data.strip()).exists(),
                'Short name already in use'
            )
        )
        url = Field(
            is_valid=lambda parsed_data, **_: (
                not Entry.objects.filter(url=parsed_data.strip()).exists(),
                'URL already submitted'
            )
        )

        class Meta:
            @staticmethod
            def actions__submit__post_handler(form, **_):
                if form.is_valid():
                    entry = Entry(
                        short=form.fields.short.value,
                        url=form.fields.url.value,
                        created_at=timezone.now(),
                        valid_to=timezone.now() + timedelta(days=30),
                    )
                    entry.save()
                    return HttpResponseRedirect(f'/thanks/{entry.short}')

    class SubmitPage(Page):
        heading = html.h1('TriOptima URL Blessalizer')
        form = SubmitForm()
        set_focus = html.script(mark_safe(
            'document.getElementById("id_url").focus();',
        ))
        admin = html.p(html.a('Admin', attrs__href='/entries'), ' (requires login)')

    return SubmitPage()


def thanks(request, short):
    return html.div(
        html.h1('Thank you for submitting an URL'),
        html.p('Processing...'),
        html.a('Submit another', attrs__href='/submit/')
    )


def go(request, short):
    entry = Entry.objects.get(short=short)

    if not entry.is_valid():
        class ErrorPage(Page):
            header = html.h1('Not approved yet...')

        return ErrorPage()

    entry.use_count += 1
    entry.save(update_fields=['use_count'])

    return HttpResponseRedirect(entry.url)


class EntryTable(Table):
    class Meta:
        auto__model = Entry
        columns__short = dict(
            cell__url=lambda value, **_: f'/s/{value}',
        )
        columns__url__cell__url = (lambda value, **_: value)

        @staticmethod
        def columns__created_at__cell__format(value, **_):
            return timesince(value)

        columns__created_at__display_name = 'Age'

        @staticmethod
        def columns__created_at__cell__attrs__title(value, **_):
            return str(value)

        @staticmethod
        def columns__valid_to__cell__format(value, **_):
            if value < timezone.now():
                return 'No longer valid'
            return timeuntil(value)

        columns__valid_to__display_name = 'Valid for'

        @staticmethod
        def columns__valid_to__cell__attrs__title(value, **_):
            return str(value)


class EntryAdminTable(EntryTable):
    edit = Column.edit()
    delete = Column.delete()

    class Meta:
        actions = dict(
            create=Action.button(tag='a', attrs__href='create'),
            logout=Action.button(tag='a', attrs__href='/logout/'),
        )


class EntryApproveTable(EntryTable):
    select = Column.select()

    class Meta:
        title = 'Approvable entries'

        @staticmethod
        def rows(table, **_):
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


class EntryUnapproveTable(EntryTable):
    select = Column.select()

    class Meta:
        title = 'Approved entries'

        @staticmethod
        def rows(table, **_):
            return Entry.objects.filter(
                approver=table.get_request().user
            )

        bulk__actions__submit = dict(
            include=True,
            attrs__value='Unapprove',
        )

        @staticmethod
        def bulk__actions__submit__post_handler(table, **_):
            table.bulk_queryset().update(approver=None)


@login_required
def entries(request):
    return Page(
        parts=dict(
            admin_table=EntryAdminTable(),
            approve_table=EntryApproveTable(),
            unapprove_table=EntryUnapproveTable(),
        )
    )


@login_required
def create(request):
    return Form.create(
        auto__model=Entry,
        fields=dict(
            creator__initial=request.user,
            use_count__include=False,
            approver__include=False,
            created_at=dict(
                editable=False,
                initial=datetime.now()
            ),
            valid_to__initial=timezone.now() + timedelta(days=30),
        )
    )


@login_required
def edit(request, short):
    return Form.edit(
        auto__instance=Entry.objects.get(short=short),
        fields=dict(
            creator__editable=False,
            use_count__editable=False,
            created_at__editable=False,
        )
    )


@login_required
def delete(request, short):
    return Form.delete(
        auto__instance=Entry.objects.get(short=short),
    )


class ShortnerAdmin(Admin):
    class Meta:
        parts__list_shortner_entry__columns__short = Column(
            cell__url=lambda value, **_: f'/s/{value}',
            after=0,
        )
