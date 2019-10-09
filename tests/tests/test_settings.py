import mock
from datetime import datetime, timedelta
from django.test import override_settings
from freezegun import freeze_time
from django.urls import reverse
from rest_framework import status
from tests.tests.test_api import get_token_from_email


@mock.patch('django.core.mail.outbox', new_callable=list)
@override_settings(TFA_TOKEN_AGE='20')
def test_token_expire(outbox, user_logged_client):
    user_logged_client.post(
        '/auth/login/',
        data={
            'username': 'user',
            'password': 'password',
        }
    )
    user_logged_client.post(reverse('tfa_create_challenge'), data={'type': 'email'})

    token = get_token_from_email(outbox.pop())
    date = datetime.now() + timedelta(seconds=30)
    with freeze_time(date):
        url = reverse('tfa_accept_challenge')
        response = user_logged_client.post(url, data={'token': token})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@mock.patch('django.core.mail.outbox', new_callable=list)
@override_settings(TFA_CLIENT_AGE='20')
def test_client_expire(outbox, user_logged_client):
    user_logged_client.post(
        '/auth/login/',
        data={
            'username': 'user',
            'password': 'password',
        }
    )
    user_logged_client.post(reverse('tfa_create_challenge'), data={'type': 'email'})
    token = get_token_from_email(outbox.pop())
    user_logged_client.post(reverse('tfa_accept_challenge'), data={'token': token})

    response = user_logged_client.get('/dummy/')
    assert response.status_code == status.HTTP_200_OK

    date = datetime.now() + timedelta(seconds=30)
    with freeze_time(date):
        response = user_logged_client.get('/dummy/')
        assert response.status_code == status.HTTP_303_SEE_OTHER
