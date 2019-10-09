import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.fixture()
def user(db):
    return get_user_model().objects.create_user(
        'user', 'user@example.com', 'password'
    )


@pytest.fixture()
def user_logged_client(db, user):
    client = Client()
    client.login(username='user', password='password')

    return client
