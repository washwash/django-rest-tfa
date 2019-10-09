import logging

from django.conf import settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django_rest_tfa.serializers import (
    CreateEmailChallengeSerializer,
    AcceptChallengeSerializer
)


logger = logging.getLogger(__name__)


class SeeOtherResponse(Response):
    status_code = status.HTTP_303_SEE_OTHER

    def __init__(self, location_url, *args, **kwargs):
        super(SeeOtherResponse, self).__init__(*args, **kwargs)
        self['LOCATION'] = location_url


class CreateChallengeView(viewsets.GenericViewSet):
    CHALLENGE_SERIALIZERS = {
        'email': CreateEmailChallengeSerializer
    }

    def create(self, request, *args, **kwargs):
        auth_type = request.POST.get('type')
        serializer_class = self.get_serializer_class(auth_type)
        serializer = serializer_class(
            data={
                'name': request.user.tfa_client,
                'user': request.user
            }
        )

        serializer.is_valid(raise_exception=True)
        device = serializer.save()

        request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        request.user.otp_device = device

        logger.info(
            '[two-factor-auth] Challenge for {} with {} was created'.format(
                request.user,
                device.name
            )
        )
        url = reverse('tfa_accept_challenge')
        return SeeOtherResponse(location_url=url)

    def get_serializer_class(self, type):
        serializer_class = self.CHALLENGE_SERIALIZERS.get(type)
        if not serializer_class:
            raise ValidationError({
                'type': ['Please, specify two factor type', ]
            })
        return serializer_class


class AcceptChallengeView(viewsets.GenericViewSet):

    def create(self, request, *args, **kwargs):
        serializer = AcceptChallengeSerializer(
            data={
                'token': request.POST.get('token'),
                'user': request.user,
            }
        )
        logger.info(
            '[two-factor-auth] {} tries accept challenge for {}'.format(
                request.user,
                request.user.otp_device.name,
            )
        )
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.info(
                '[two-factor-auth] Challenge for {} with failed: {}'.format(
                    request.user,
                    request.user.otp_device.name,
                    str(e)
                )
            )
            raise e

        serializer.save()
        logger.info(
            '[two-factor-auth] Challenge for {} with completed'.format(
                request.user,
                request.user.otp_device.name,
            )
        )
        return SeeOtherResponse(location_url='/')


class EnabledTypesView(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        return Response(data=settings.TFA_ENABLED_AUTH_TYPES)


create_challenge_view = CreateChallengeView.as_view(
    actions={'post': 'create'}
)
accept_challenge_view = AcceptChallengeView.as_view(
    actions={'post': 'create'}
)
enabled_types_view = EnabledTypesView.as_view(
    actions={'get': 'list'}
)
