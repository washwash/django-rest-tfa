from django.conf import settings
from django.apps import apps

from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError

from django_rest_tfa.models import TwoFactorAuthEmailDevice


class UserField(serializers.ModelSerializer):

    def to_internal_value(self, data):
        return data

    class Meta:
        fields = ('id', )
        model = apps.get_model(settings.AUTH_USER_MODEL)


class CreateChallengeSerializer(serializers.Serializer):
    name = fields.CharField(
        required=True,
        allow_null=False
    )
    user = UserField(
        required=True,
        allow_null=False
    )

    def validate_user(self, user):
        if user.is_authenticated and not user.is_anonymous:
            return user
        raise ValidationError(['User should be authenticated'])

    def create(self, validated_data):
        device = validated_data['user'].otp_device

        if not device:
            device = self.Meta.model.objects.create(**validated_data)

        device.generate_challenge()
        return device


class CreateEmailChallengeSerializer(CreateChallengeSerializer):

    class Meta:
        model = TwoFactorAuthEmailDevice


class AcceptChallengeSerializer(serializers.Serializer):
    user = UserField(
        required=True,
        allow_null=False
    )
    token = fields.CharField(
        required=True,
        allow_null=False
    )

    def validate_user(self, user):
        if user.otp_device:
           return user

        raise ValidationError(['User does not have otp device', ])

    def validate_token(self, token):
        device = self.initial_data['user'].otp_device
        if device.attempts >= 3:
            raise ValidationError(['Code is outdated. Please generate a new code', ])

        if device.verify_token(token):
            return token

        raise ValidationError(['Invalid code'])
    
    def create(self, validated_data):
        device = validated_data['user'].otp_device
        device.activate()
        return device
