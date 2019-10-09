from django.urls import path
from django_rest_tfa.views import (
    accept_challenge_view,
    enabled_types_view,
    create_challenge_view
)


urlpatterns = [
    path(
        'create_challenge/',
        create_challenge_view,
        name='tfa_create_challenge'
    ),
    path(
        'accept_challenge/',
        accept_challenge_view,
        name='tfa_accept_challenge'
    ),
    path(
        'enabled_types/',
        enabled_types_view,
        name='tfa_enabled_types'
    ),
]
