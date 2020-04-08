from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from shortner.models import Entry
from shortner.views import (
    submit,
    go,
)

pytestmark = [
    pytest.mark.django_db,
]


def test_root_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.url == reverse(submit)


def test_submit(client):
    short = 'foo'
    url = 'http://foo.bar/boink'

    response = client.post(
        reverse(submit),
        data={
            '-submit': '',
            'short': short,
            'url': url,
        },
    )

    assert response.status_code == 302

    entry = Entry.objects.get()
    assert entry.url == url
    assert entry.short == short


def test_not_yet_approved(client):
    Entry(
        short='short',
        url='http://foo.bar/boink',
        created_at=timezone.now(),
        valid_to=timezone.now() + timedelta(days=30),
    ).save()

    response = client.get(reverse(go, args=dict(short='short')))
    assert 'Not approved yet...' in response.content.decode()


@pytest.fixture
def admin():
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='admin',
        email='admin@badmin.com',
        password='password',
    )


def test_approved(client, admin):
    Entry(
        short='short',
        url='http://foo.bar/boink',
        approver=admin,
        created_at=timezone.now(),
        valid_to=timezone.now() + timedelta(days=30),
    ).save()

    response = client.get(reverse(go, args=dict(short='short')))
    assert 'Not approved yet...' not in response.content.decode()
