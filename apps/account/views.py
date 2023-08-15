from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status, response, viewsets
from rest_framework.decorators import action

from apps.account.models import Account
from apps.account.serializer import AccountUserRegisterSerializer, AccountRetrieveSerializer, AccountStaffRegisterSerializer, AccountSuperUserRegisterSerializer

# Create your views here.
class AccountUserRegisterView(generics.CreateAPIView):
    model = Account
    serializer_class = AccountUserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']




class AccountRetrieveViewSet(generics.RetrieveUpdateAPIView):
    model = Account
    queryset = None
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountRetrieveSerializer
    http_method_names = ['get','patch']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return super().get_queryset()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        if pk != str(self.request.user.id):
            return response.Response({'cod':1,'message':_('The sent ID does not match the requesting account.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            account = Account.objects.get(pk=pk)
            account_serializer = self.serializer_class(account)
            return response.Response({'cod':0,'message':'success','user':account_serializer.data,'status_code':status.HTTP_200_OK}, status=status.HTTP_200_OK)
        except:
            return response.Response({'cod':1,'message':'fail','user':'No valid record found.'}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk=None, *args, **kwargs):
        if pk != str(self.request.user.id):
            return response.Response({'cod':1,'message':_('The sent ID does not match the requesting account.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        account = Account.objects.get(pk=pk)
        account_serializer = self.serializer_class(account, data=request.data, partial=True)
        if account_serializer.is_valid():
            account = account_serializer.update(account = account, validated_data = account_serializer.validated_data)
            serializer = self.serializer_class(account)
            return response.Response({'cod':0,'message': 'Account updated successfully.','user':serializer.data}, status=status.HTTP_200_OK)
        
        raise response.Response({'cod':1,'message':account_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




class AccountStaffRegisterView(viewsets.ModelViewSet):
    model = Account
    serializer_class = AccountStaffRegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get','post', 'put', 'patch', 'delete']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return super().get_queryset()
    
    def update(self, request, *args, **kwargs):
        return response.Response({'cod':1,'message':_('This method is forbidden, use the appropriate URLs for account update.')}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, pk=None, *args, **kwargs):
        if pk != str(self.request.user.id):
            return response.Response({'cod':1,'message':_('The sent ID does not match the requesting account.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        account = get_object_or_404(Account, pk=pk)
        account_serializer = self.serializer_class(account, data=request.data, partial=True)
        if account_serializer.is_valid():
            account = account_serializer.update(account = account, validated_data = account_serializer.validated_data)
            serializer = self.serializer_class(account)
            return response.Response({'cod':0,'message': 'Account updated successfully.','user':serializer.data}, status=status.HTTP_200_OK)
        
        raise response.Response({'cod':1,'message':account_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def activate_user(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'message':_('The target ID is mandatory.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.activate_user(account=account)
            return response.Response({'cod':0, 'message': 'Account updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Account can`t be activate.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_physical(self, request, pk=None, *args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'message':_('The target ID is mandatory.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.delete_physical(account=account)
            return response.Response({'cod':0, 'message': 'Account deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Account can`t be deleted.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_logical(self, request, pk=None, *args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'message':_('The target ID is mandatory.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.delete_logical(account=account)
            return response.Response({'cod':0, 'message': 'Account disabled successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Account can`t be disabled.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        return response.Response({'cod':1,'message':_('This method is forbidden, use the appropriate URLs for user deletion.')}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(detail=True, methods=['put'])
    def add_staff(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'message':_('The target ID is mandatory.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.add_is_staff(account=account)
            return response.Response({'cod':0, 'message': 'Account updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Account can`t be updated successfully.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def revoke_staff(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'message':_('The target ID is mandatory.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.revoke_is_staff(account=account)
            return response.Response({'cod':0, 'message': 'Account updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Account can`t be updated successfully.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def add_superuser(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'message':_('The target ID is mandatory.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.add_is_superuser(account=account)
            return response.Response({'cod':0, 'message': 'Account updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Account can`t be updated successfully.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def revoke_superuser(self, request, pk=None,*args, **kwargs):
        if pk is None:
            return response.Response({'cod':1,'message':_('The target ID is mandatory.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, pk=pk)
        try:
            Account.objects.revoke_is_superuser(account=account)
            return response.Response({'cod':0, 'message': 'Account updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as error:
            return response.Response({'cod':1, 'message': 'Account cant`be updated successfully.','error':str(error)}, status=status.HTTP_400_BAD_REQUEST)
    



class AccountSuperUserRegisterView(generics.CreateAPIView):
    model = Account
    serializer_class = AccountSuperUserRegisterSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['post']

    def create(self, request, pk=None, *args, **kwargs):
        if not request.user.is_superuser:
            return response.Response({'cod':1,'message':_('The account making the request does not have the necessary permissions.')}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_serializer = self.serializer_class(data=request.data)
        if user_serializer.is_valid():
            try:
                user = user_serializer.create(validated_data = user_serializer.validated_data)
                serializer = self.serializer_class(user)
                return response.Response({'cod':0,'message': 'Account updated successfully.','user':serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return response.Response({'cod':1,'message':_('Account cant`be updated successfully.')}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({'cod':1,'message':_('"Invalid input data.'), 'detail':(user_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)