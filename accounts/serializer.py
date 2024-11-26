from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from .models import Account


class AccountSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        required=True,
        validators=[
            MinLengthValidator(1, message='名前は1文字以上である必要があります。'),
            MaxLengthValidator(30, message='名前は30文字以下である必要があります。'),
            RegexValidator(
                regex=r'^[\w\s]+$',  # 記号を除外し、アルファベット、数字、スペースを許可
                message='名前は記号を含まない、最小1文字最大30文字である必要があります'
            )
        ]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,15}$',
                message='パスワードは半角英数字混在の最小8文字最大15文字である必要があります。'
            )
        ]
    )

    class Meta:
        model = Account
        fields = ['id', 'name', 'email', 'password', 'last_login_at']  # 'deleted_at'を除外
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        # パスワードを暗号化して保存
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # パスワードの更新時も暗号化
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)
