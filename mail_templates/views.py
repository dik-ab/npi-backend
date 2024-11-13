# views.py

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SendMailSerializer

class SendMailView(APIView):
    def post(self, request):
        serializer = SendMailSerializer(data=request.data)
        if serializer.is_valid():
            sender_email = settings.DEFAULT_FROM_EMAIL
            recipient_email = serializer.validated_data['recipient_email']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']

            # メール送信
            try:
                send_mail(
                    subject,
                    message,
                    sender_email,
                    [recipient_email],
                    fail_silently=False,
                )
                return Response({"message": "メールが正常に送信されました。"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"メールの送信に失敗しました: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # バリデーションエラー
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
