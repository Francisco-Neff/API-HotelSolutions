from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status, response, viewsets
from rest_framework.decorators import action

from apps.account.models import Account
from apps.account.serializer import AccountUserRegisterSerializer, AccountRetrieveSerializer, AccountStaffRegisterSerializer

# Create your views here.
class AccountUserRegisterView(generics.CreateAPIView):
    model = Account
    serializer_class = AccountUserRegisterSerializer
    http_method_names = ['post']



class AccountRetrieveViewSet(generics.RetrieveUpdateAPIView):
    model = Account
    queryset = None
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountRetrieveSerializer

    def get_queryset(self):
        return super().get_queryset()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        if pk != str(self.request.user.id):
            return response.Response({'cod':1,'detail':_('El id enviado no coincide con el usuario que realiza la petición.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            account = Account.objects.get(pk=pk)
            account_serializer = self.serializer_class(account)
            return response.Response({'cod':0,'message':'success','user':account_serializer.data,'status_code':status.HTTP_200_OK}, status=status.HTTP_200_OK)
        except:
            return response.Response({'cod':1,'message':'fail','user':'No se ha encontrado un registro válido'}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk=None, *args, **kwargs):
        if pk != str(self.request.user.id):
            return response.Response({'cod':1,'detail':_('El id enviado no coincide con el usuario que realiza la petición.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        account = Account.objects.get(pk=pk)
        account_serializer = self.serializer_class(account, data=request.data, partial=True)
        if account_serializer.is_valid():
            account = account_serializer.update(account = account, validated_data = account_serializer.validated_data)
            serializer = self.serializer_class(account)
            return response.Response({'cod':0,'message': 'Usuario actualizado correctamente.','user':serializer.data}, status=status.HTTP_200_OK)
        
        raise response.Response({'cod':1,'detail':account_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class AccountStaffRegisterView(viewsets.ModelViewSet):
    model = Account
    serializer_class = AccountStaffRegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get','post','put','delete']

    def update(self, request, pk=None, *args, **kwargs):
        if pk != str(self.request.user.id):
            return response.Response({'cod':1,'detail':_('El id enviado no coincide con el usuario que realiza la petición.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        account = get_object_or_404(Account, pk=pk)
        account_serializer = self.serializer_class(account, data=request.data, partial=True)
        if account_serializer.is_valid():
            account = account_serializer.update(account = account, validated_data = account_serializer.validated_data)
            serializer = self.serializer_class(account)
            return response.Response({'cod':0,'message': 'Usuario actualizado correctamente.','user':serializer.data}, status=status.HTTP_200_OK)
        
        raise response.Response({'cod':1,'detail':account_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def activate_user(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'detail':_('El id objetivo es obligatorio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'detail':_('El usuario que realiza la petición no tiene los permisos necesarios.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.activate_user(account=account)
            return response.Response({'cod':0, 'message': 'Usuario eliminado correctamente.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Usuario actualizado correctamente.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_physical(self, request, pk=None, *args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'detail':_('El id objetivo es obligatorio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'detail':_('El usuario que realiza la petición no tiene los permisos necesarios.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.delete_physical(account=account)
            return response.Response({'cod':0, 'message': 'Usuario eliminado correctamente.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'La petición no ha podido ser concluida correctamente.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_logical(self, request, pk=None, *args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'detail':_('El id objetivo es obligatorio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'detail':_('El usuario que realiza la petición no tiene los permisos necesarios.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.delete_logical(account=account)
            return response.Response({'cod':0, 'message': 'Usuario desactivado.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'La petición no ha podido ser concluida correctamente.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        return response.Response({'cod':1,'detail':_('Este método esta prohibido, utilice las url propias para el borrado de usuario.')}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(detail=True, methods=['put'])
    def add_staff(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'detail':_('El id objetivo es obligatorio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'detail':_('El usuario que realiza la petición no tiene los permisos necesarios.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.add_is_staff(account=account)
            return response.Response({'cod':0, 'message': 'Usuario eliminado correctamente.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Usuario actualizado correctamente.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def revoke_staff(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'detail':_('El id objetivo es obligatorio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'detail':_('El usuario que realiza la petición no tiene los permisos necesarios.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.revoke_is_staff(account=account)
            return response.Response({'cod':0, 'message': 'Usuario eliminado correctamente.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Usuario actualizado correctamente.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def add_superuser(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'detail':_('El id objetivo es obligatorio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'detail':_('El usuario que realiza la petición no tiene los permisos necesarios.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.add_is_superuser(account=account)
            return response.Response({'cod':0, 'message': 'Usuario eliminado correctamente.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Usuario actualizado correctamente.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def revoke_superuser(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'detail':_('El id objetivo es obligatorio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'detail':_('El usuario que realiza la petición no tiene los permisos necesarios.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.revoke_is_superuser(account=account)
            return response.Response({'cod':0, 'message': 'Usuario eliminado correctamente.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Usuario actualizado correctamente.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)