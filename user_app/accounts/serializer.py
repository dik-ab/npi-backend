from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.core.validators import (
    RegexValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from shared.models import Account
import hashlib
import secrets
from django.utils.timezone import now
from datetime import timedelta


class AccountSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        required=True,
        validators=[
            MinLengthValidator(1, message="名前は1文字以上である必要があります。"),
            MaxLengthValidator(30, message="名前は30文字以下である必要があります。"),
            RegexValidator(
                regex=r"^[\w\s]+$",  # 記号を除外し、アルファベット、数字、スペースを許可
                message="名前は記号を含まない、最小1文字最大30文字である必要があります",
            ),
        ],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,15}$",
                message="パスワードは半角英数字混在の最小8文字最大15文字である必要があります。",
            )
        ],
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "email",
            "password",
            "last_login_at",
        ]  # 'deleted_at'を除外
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


class TOTPVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスは登録されていません。")
        return value

    def create_reset_token(self, user):
        """トークンを生成、ハッシュ化して保存"""
        raw_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
        expiration = now() + timedelta(hours=24)  # トークン有効期限 24時間

        user.reset_token = hashed_token
        user.token_expiration = expiration
        user.save()

        return raw_token  # 生成されたトークン（非ハッシュ化）を返す


class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True,)
    token = serializers.CharField(required=True,)

    def validate_email(self, value):
        if not Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスは登録されていません。")
        return value

    def validate(self, data):
        try:
            hashed_token = hashlib.sha256(data['token'].encode()).hexdigest()
            user = Account.objects.get(email=data['email'], reset_token=hashed_token)

            if not user.is_reset_token_valid():
                raise serializers.ValidationError("トークンが無効または期限切れです。")

            self.user = user
            return data

        except Account.DoesNotExist:
            raise serializers.ValidationError("無効なトークンです。")


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True,)
    token = serializers.CharField(required=True,)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,15}$",
                message="パスワードは半角英数字混在の最小8文字最大15文字である必要があります。",
            )
        ],
    )

    def validate_email(self, value):
        if not Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスは登録されていません。")
        return value

    def validate(self, data):
        try:
            hashed_token = hashlib.sha256(data['token'].encode()).hexdigest()
            user = Account.objects.get(email=data['email'], reset_token=hashed_token)

            if not user.is_reset_token_valid():
                raise serializers.ValidationError("トークンが無効または期限切れです。")

            self.user = user
            return data

        except Account.DoesNotExist:
            raise serializers.ValidationError("無効なトークンです。")

    def save(self):
        """新しいパスワードを保存"""
        # パスワードは暗号化して保存
        self.validated_data["new_password"] = make_password(self.validated_data["new_password"])
        self.user.password = self.validated_data['new_password']
        self.user.reset_token = None
        self.user.token_expiration = None
        self.user.save()
