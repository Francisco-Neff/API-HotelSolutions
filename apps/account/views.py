from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status, response

from apps.account.models import Account
from apps.account.serializer import AccountUserRegisterSerializer, AccountRetrieveSerializer

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

