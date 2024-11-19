from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Account
from ..serializer import AccountSerializer


class AccountView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                account = Account.objects.get(pk=pk)
                serializer = AccountSerializer(account)
                return Response(serializer.data)
            except Account.DoesNotExist:
                return Response(
                    {"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            accounts = Account.objects.filter(deleted_at__isnull=True)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            account = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            account = Account.objects.get(pk=pk)
            account.deleted_at = now()
            account.save()
            return Response(
                {"message": "Account deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND
            )
