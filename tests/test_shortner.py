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


@pytest.fixture
def fresh_entry():
    entry = Entry(
        short='short',
        url='http://foo.bar/boink',
        created_at=timezone.now(),
        valid_to=timezone.now() + timedelta(days=30),
    )
    entry.save()
    return entry


def test_not_yet_approved(client, fresh_entry):
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


@pytest.fixture
def approved_entry(fresh_entry, admin):
    fresh_entry.approver = admin
    fresh_entry.save()
    return fresh_entry


def test_approved(client, approved_entry, admin):
    response = client.get(reverse(go, args=dict(short='short')))
    assert response.status_code == 302
    assert response.url == approved_entry.url


@pytest.fixture
def no_longer_approved_entry(approved_entry, admin):
    approved_entry.valid_to = timezone.now() - timedelta(days=5)
    approved_entry.save()


def test_no_longer_approved(client, no_longer_approved_entry):
    response = client.get(reverse(go, args=dict(short='short')))
    assert 'Not approved yet...' in response.content.decode()
