from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import Announcement
from .serializers import AnnouncementSerializer

# Create your views here.

class AnnouncementPagination(PageNumberPagination):
    page_size_query_param = 'per_page'

class AnnouncementListView(generics.ListAPIView):
    queryset = Announcement.objects.filter(deleted_at__isnull=True)
    serializer_class = AnnouncementSerializer
    pagination_class = AnnouncementPagination
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_page = request.query_params.get('current_page', 1)
        per_page = request.query_params.get('per_page', 10)
        self.pagination_class.page_size = per_page
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'pagination': {
                'current_page': current_page,
                'per_page': per_page,
                'total_pages': self.paginator.page.paginator.num_pages,
                'total_items': self.paginator.page.paginator.count,
            }
        })
