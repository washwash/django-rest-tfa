from datetime import timedelta

from django.core import mail
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from django_otp.oath import totp
from django_otp.plugins.otp_email.models import EmailDevice


class BaseTwoFactorAuthDevice(models.Model):
    attempts = models.SmallIntegerField(
        default=0
    )
    added_at = models.DateTimeField(
        auto_now_add=True
    )
    last_requested = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        abstract = True

    @property
    def is_active(self):
        client_age = int(settings.TFA_CLIENT_AGE)
        expired = self.added_at + timedelta(seconds=client_age)
        return expired > timezone.now()

    @property
    def has_active_token(self):
        token_age = int(settings.TFA_TOKEN_AGE)
        token_expired = self.last_requested + timedelta(seconds=token_age)
        return self.attempts < 3 and token_expired > timezone.now()

    def reset_device(self):
        self.last_requested = timezone.now()
        self.attempts = 0
        self.save()

    def activate(self):
        self.attempts = 0
        self.save()


class TwoFactorAuthEmailDevice(BaseTwoFactorAuthDevice, EmailDevice):

    def generate_challenge(self):
        self.reset_device()

        context = {
            'token': totp(self.bin_key, step=1),
            'host': getattr(settings, 'HOST', ''),
            'user': self.user
        }
        subject = render_to_string('tfa_email/subject.txt', context)
        body = render_to_string('tfa_email/body.txt', context)

        mail.send_mail(
            subject=subject, message=body,
            from_email=None,recipient_list=[self.user.email, ]
        )

    def verify_token(self, token):
        try:
            if isinstance(token, str) and token.isdigit():
                token = int(token)
        except Exception:
            return False

        return any(
            totp(self.bin_key, step=1, drift=drift) == token
            for drift in range(0, -int(settings.TFA_TOKEN_AGE), -1)
        )

    def reset_device(self):
        self.confirmed = False
        super(TwoFactorAuthEmailDevice, self).reset_device()

    def activate(self):
        self.confirmed = True
        super(TwoFactorAuthEmailDevice, self).activate()