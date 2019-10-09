from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django_otp.middleware import OTPMiddleware
from rest_framework import status

from django_rest_tfa.views import SeeOtherResponse


class TwoFactorAuthMiddleware(OTPMiddleware):
    """
    Sets otp_device to User.
    Defines User client and validate expiration of device
    """

    def process_request(self, request):
        result = super(TwoFactorAuthMiddleware, self).process_request(request)

        if isinstance(request.user, AnonymousUser):
            return result

        if request.path_info in self.allowed_urls:
            return result

        if self.is_device_confirmed(request, request.user.otp_device):
            return result

        if self.is_device_has_active_challenge(request.user.otp_device):
            see_other_url = reverse('tfa_accept_challenge')
        else:
            see_other_url = reverse('tfa_create_challenge')

        return SeeOtherResponse(location_url=see_other_url)

    def process_response(self, request, response):
        # transaction atomic doesn't allow to increment attempts
        # in serializer or view
        if response.status_code != status.HTTP_400_BAD_REQUEST:
            return response

        if request.path_info == reverse('tfa_accept_challenge'):
            device = request.user.otp_device
            device.attempts += 1
            device.save()
        return response

    def is_device_has_active_challenge(self, device):
        """
        Returns True if Device has non-expired challenge
        :param device: Device instance
        :return: Bool
        """
        return (
            device and
            not device.confirmed and
            device.has_active_token
        )

    @cached_property
    def allowed_urls(self):
        return [
            reverse('tfa_enabled_types'),
            reverse('tfa_create_challenge'),
            reverse('tfa_accept_challenge'),
        ]

    def is_device_confirmed(self, request, device):
        """
        Returns True if device is determined, active and equals with user client
        :param request: Request instance
        :param device: Device instance
        :return: Bool
        """
        return (
            device and
            device.name == request.user.tfa_client and
            device.confirmed and
            device.is_active
        )

    def get_tfa_client(self, request):
        client_ids = []
        for identifier_path in settings.TFA_CLIENT_IDENTIFIERS:
            identifier = import_string(identifier_path)
            client_ids.append(identifier(request))

        if client_ids:
            return ' '.join(client_ids)

    def _verify_user(self, request, user):
        result = super(TwoFactorAuthMiddleware, self)._verify_user(request, user)
        user.tfa_client = self.get_tfa_client(request)
        return result
