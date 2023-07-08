from django.shortcuts import render

from rest_framework import generics, permissions, status, response


from apps.account.models import Account
from apps.account.serializer import AccountRetrieveSerializer

# Create your views here.

class AccountRetrieveViewSet(generics.RetrieveAPIView):
    model = Account
    queryset = None
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountRetrieveSerializer

    def get_queryset(self):
        return super().get_queryset()
    
    def retrieve(self, request, pk=None):
        #if pk != str(self.request.user.id):
        #    raise BadRequestAPIException(cod=2,detail=_('El id enviado no coincide con el usuario que realiza la petición.'))
        
        try:
            user = Account.objects.get(pk=pk)
            user_serializer = self.serializer_class(user)
            return response.Response({'cod':0,'message':'success','user':user_serializer.data,'status_code':status.HTTP_200_OK}, status=status.HTTP_200_OK)
        except:
            return response.Response({'cod':1,'message':'fail','user':'No se ha encontrado un registro válido'}, status=status.HTTP_404_NOT_FOUND)
