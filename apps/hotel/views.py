from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets, parsers
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.hotel.models import Hotel, HotelMedia, Room, RoomMedia, RoomExtra
from apps.hotel.serializer import HotelRegisterSerializer, HotelMediaRegisterSerializer, RoomRegisterSerializer, RoomMediaRegisterSerializer, RoomDeleteItemSerializer, RoomExtraRegisterSerializer

# Create your views here.


class BaseCRUDModelView(viewsets.ModelViewSet):
    model = None
    serializer_class = None
    permission_classes = [permissions.IsAdminUser]
    http_method_names = None

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
                return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e.message)}"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e.message)}"}, status=status.HTTP_400_BAD_REQUEST)
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




class HotelRegisterView(BaseCRUDModelView):
    model = Hotel
    serializer_class = HotelRegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get','post', 'put', 'patch', 'delete']
    



class HotelMediaRegisterView(BaseCRUDModelView):
    model = HotelMedia
    serializer_class = HotelMediaRegisterSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']




class RoomRegisterView(BaseCRUDModelView):
    model = Room
    serializer_class = RoomRegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get','post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)




class RoomMediaRegisterView(BaseCRUDModelView):
    model = RoomMedia
    serializer_class = RoomMediaRegisterSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    @action(detail=True, methods=['post'])
    def delete_item(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return Response({'cod':1,'message':_('The sent ID is incorrect.')}, status=status.HTTP_400_BAD_REQUEST)
        try:
            model_object = get_object_or_404(self.model, pk=pk)
            serializer = RoomDeleteItemSerializer(data=request.data)
            if serializer.is_valid():
                id_room = get_object_or_404(Room, pk=serializer.validated_data.get('id_room'))
                model_object.delete_item_room(id_room=id_room)
            serializer = self.serializer_class(model_object)
            return Response({'cod':0,'message': f'{self.model.__name__} updated successfully.', **serializer.data}, status=status.HTTP_200_OK)
        except Http404:
            return Response({'cod':1,'message':f"{_('Record not found error.')}"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)




class RoomExtraRegisterView(BaseCRUDModelView):
    model = RoomExtra
    serializer_class = RoomExtraRegisterSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def delete_item(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return Response({'cod':1,'message':_('The sent ID is incorrect.')}, status=status.HTTP_400_BAD_REQUEST)
        try:
            model_object = get_object_or_404(self.model, pk=pk)
            serializer = RoomDeleteItemSerializer(data=request.data)
            if serializer.is_valid():
                id_room = get_object_or_404(Room, pk=serializer.validated_data.get('id_room'))
                model_object.delete_item_room(id_room=id_room)
            serializer = self.serializer_class(model_object)
            return Response({'cod':0,'message': f'{self.model.__name__} updated successfully.', **serializer.data}, status=status.HTTP_200_OK)
        except Http404:
            return Response({'cod':1,'message':f"{_('Record not found error.')}"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'cod':1,'message':f"{_('Unexpected validation.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'cod':1,'message':f"{_('Unexpected error.')} {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)