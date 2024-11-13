from rest_framework import serializers

class SendMailSerializer(serializers.Serializer):
    recipient_email = serializers.EmailField(help_text="受信者のメールアドレス")
    subject = serializers.CharField(max_length=255, help_text="メールの件名")
    message = serializers.CharField(help_text="メールの本文")