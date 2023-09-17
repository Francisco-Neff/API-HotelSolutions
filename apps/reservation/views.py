from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.reservation.models import Discount, Reservation
from apps.reservation.serializer import DiscountRegisterSerializer, ReservationRegisterSerializer


# Create your views here.
class BaseCRUDModelView(viewsets.ModelViewSet):
    """
    Basic CRUD operations to be used in record administration. To utilize the various methods, the user must have administrator privileges.
    """
    model = None
    serializer_class = None
    queryset = None
    permission_classes = [permissions.IsAdminUser]
    http_method_names = None

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return self.model.objects.all()
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response({'cod':0, 'queryset':serializer.data}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        if pk is None:
            return Response({'cod':1,'message':_('The sent ID is incorrect.')}, status=status.HTTP_400_BAD_REQUEST)

        model_object = get_object_or_404(self.model, pk=pk)
        model_serializer = self.serializer_class(model_object, data=request.data)
        if model_serializer.is_valid():
            try:
                model_object = model_serializer.update(model_object = model_object, validated_data = model_serializer.validated_data)
                serializer = self.serializer_class(model_object)
                return Response({'cod':0,'message': f'{self.model.__name__} updated successfully.', **serializer.data}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'cod':1,'message':f"{_('Data error: ')} {model_serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        if pk is None:
            return Response({'cod':1,'message':_('The sent ID is incorrect.')}, status=status.HTTP_400_BAD_REQUEST)

        model_object = get_object_or_404(self.model, pk=pk)
        model_serializer = self.serializer_class(model_object, partial=True, data=request.data)
        if model_serializer.is_valid():
            try:
                model_object = model_serializer.update(model_object = model_object, validated_data = model_serializer.validated_data)
                serializer = self.serializer_class(model_object)
                return Response({'cod':0,'message': f'{self.model.__name__} updated successfully.', **serializer.data}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'cod':1,'message':f"{_('Data error: ')} {model_serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        if pk is None:
            return Response({'cod':1,'message':_('The sent ID is incorrect.')}, status=status.HTTP_400_BAD_REQUEST)
        try:
            model_object = get_object_or_404(self.model, pk=pk)
            model_object.delete()
        except Http404:
            return Response({'cod':1,'message':f"{_('Record not found error.')}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response( status=status.HTTP_204_NO_CONTENT)




class DiscountRegisterView(BaseCRUDModelView):
    """
    CRUD for Discount Model
    """
    model = Discount
    serializer_class = DiscountRegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get','post', 'put', 'patch', 'delete']
    



class ReservationRegisterView(BaseCRUDModelView):
    """
    CRUD for Reservation Model
    """
    model = Reservation
    serializer_class = ReservationRegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']