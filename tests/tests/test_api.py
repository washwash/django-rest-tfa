import re

from django.conf import settings
from django.urls import reverse
from rest_framework import status
import mock


def get_token_from_email(email):
    found = re.search('Code is: (.+\d)', email.body)
    if found:
        return found.group(1)


def test_login_with_redirect(client, user):
    response = client.post(
        '/auth/login/',
        data={
            'username': 'user',
            'password': 'password',
        }
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.get('/dummy/')
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response['LOCATION'] == reverse('tfa_create_challenge')


def test_create_challenge(client, user):
    response = client.post(
        '/auth/login/',
        data={
            'username': 'user',
            'password': 'password',
        }
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.post(reverse('tfa_create_challenge'), data={'type': 'email'})
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response['LOCATION'] == reverse('tfa_accept_challenge')


def test_create_challenge_wrong_type(user_logged_client):
    response = user_logged_client.post(
        reverse('tfa_create_challenge'), data={'type': 'WRONGTYPE'}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['type'] == ['Please, specify two factor type', ]


@mock.patch('django.core.mail.outbox', new_callable=list)
def test_accept_challenge(outbox, user_logged_client):
    assert len(outbox) == 0
    user_logged_client.post(reverse('tfa_create_challenge'), data={'type': 'email'})
    assert len(outbox) == 1

    token = get_token_from_email(outbox.pop())
    url = reverse('tfa_accept_challenge')
    response = user_logged_client.post(url, data={'token': token})
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response['LOCATION'] == '/'
    
    response = user_logged_client.get('/dummy/')
    assert response.status_code == status.HTTP_200_OK


def test_accept_challenge_negative(user_logged_client):
    user_logged_client.post(reverse('tfa_create_challenge'), data={'type': 'email'})

    url = reverse('tfa_accept_challenge')
    response = user_logged_client.post(url, data={'token': 'WRONG TOKEN'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['token'] == ['Invalid code', ]

    response = user_logged_client.get('/dummy/')
    assert response.status_code == status.HTTP_303_SEE_OTHER

    response = user_logged_client.post(url, data={'token': 'WRONGTOKEN'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['token'] == ['Invalid code', ]

    response = user_logged_client.post(url, data={'token': 'WRONGTOKEN'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['token'] == ['Invalid code', ]

    response = user_logged_client.post(url, data={'token': 'WRONGTOKEN'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['token'] == ['Code is outdated. Please generate a new code', ]


@mock.patch('django.core.mail.outbox', new_callable=list)
def test_accept_challenge_recreate(outbox, user_logged_client):
    user_logged_client.post(reverse('tfa_create_challenge'), data={'type': 'email'})

    url = reverse('tfa_accept_challenge')
    user_logged_client.post(url, data={'token': 'WRONG TOKEN'})
    user_logged_client.post(url, data={'token': 'WRONG TOKEN'})
    user_logged_client.post(url, data={'token': 'WRONG TOKEN'})
    user_logged_client.post(url, data={'token': 'WRONG TOKEN'})

    user_logged_client.post(reverse('tfa_create_challenge'), data={'type': 'email'})
    token = get_token_from_email(outbox.pop())
    user_logged_client.post(url, data={'token': token})

    response = user_logged_client.get('/dummy/')
    assert response.status_code == status.HTTP_200_OK


def test_enabled_types(user_logged_client):
    response = user_logged_client.get(reverse('tfa_enabled_types'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data == settings.TFA_ENABLED_AUTH_TYPES
