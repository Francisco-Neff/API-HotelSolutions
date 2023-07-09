import time
from faker import Faker
from urllib.parse import urlencode

from django.test import TestCase
from django.db.utils import IntegrityError
from django.urls import reverse

from rest_framework.test import APITransactionTestCase, RequestsClient

from apps.account.models import Account

# Create your tests here.
fake = Faker()
LOCAL_URL = 'http://127.0.0.1:8000'
PASSWORD = '12345678*Abc'


def test_generate_account_data(self, is_active=None):
    data_object = {
        'email' : fake.email(),
        'name' : fake.name(),
        'last_name' : fake.last_name(),
        'password' : PASSWORD,
    }

    if is_active is None:
        is_active = fake.pybool()
    data_object['is_active'] = is_active
    return data_object


class AccountTestCase(TestCase):
    """
    Test para verificar la creación de objetos del modelo Account.
    """
    @classmethod
    def setUpClass(cls):
        cls.start_time = time.time()
        super().setUpClass()
        print(f"\nIniciando la clase de pruebas: {cls.__name__}")
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        print(f"\nFinalizando la clase de pruebas: {cls.__name__}, Tiempo transcurrido: {(time.time()-cls.start_time)}" )    
    
    def setUp(self):
        self.data_object = test_generate_account_data(self, is_active=True)
    
    def test_create_user(self):
        """
        Test para comprobar la creación de un nuevo usuario.
        Se verifica que el usuario esta activo.
        Se verifica que el is_staff es False y el is_superuser es False
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_inactive(self):
        """
        Test para comprobar la creación de un nuevo usuario con el is_active a False.
        Se verifica que el usuario esta inactivo.
        Se verifica que el is_staff es False y el is_superuser es False
        """
        self.data_object = test_generate_account_data(self, is_active=False)
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_staff(self):
        """
        Test para comprobar la creación de un nuevo usuario staff.
        Se verifica que el usuario esta activo.
        Se verifica que el is_staff es True y el is_superuser es False
        """
        user = Account.objects.create_staff(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_superuser(self):
        """
        Test para comprobar la creación de un nuevo usuario superuser.
        Se verifica que el usuario esta activo.
        Se verifica que el is_staff es True y el is_superuser es True.
        """
        user = Account.objects.create_superuser(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_staff_duplicate_unique_fields(self):
        """
        Test para comprobar que la clave de usuario y campos únicos no se repitan.
        """
        Account.objects.create_user(**self.data_object)
        with self.assertRaises(IntegrityError) as error: 
            Account.objects.create_user(**self.data_object)
        self.assertIsInstance(error.exception, IntegrityError)
    
    def test_update_user(self):
        """
        Test para verificar que se actualiza correctamente un usuario.
        Se verifica que aunque se envié el campo is_staff este no se actualiza
        Se verifica la actualización del email
        Se verifica la actualización de la contraseña
        """
        user = Account.objects.create_user(**self.data_object)
        self.data_object['is_staff'] = True
        self.data_object['is_superuser'] = True
        self.data_object['email'] = fake.email()
        self.data_object['password'] = 'NewPassword*123'
        user_update = Account.objects.update(account=user, **self.data_object)
        self.assertFalse(user_update.is_staff)
        self.assertFalse(user_update.is_superuser)
        self.assertEqual(self.data_object['email'], user_update.email)
        self.assertTrue(user_update.check_password(self.data_object['password']))
    
    def test_delete_logical(self):
        """
        Test para comprobar que el usuario queda inactivo tras realizar un borrado lógico.
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(user.is_active)
        user_inactive = Account.objects.delete_logical(account=user)
        self.assertFalse(user_inactive.is_active)
    
    def test_delete_physical(self):
        """
        Test para comprobar que el usuario queda inactivo tras realizar un borrado físico.
        Se comprueba que no existe el registro en base de datos.
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(Account.objects.delete_physical(account=user))
        self.assertFalse(Account.objects.filter(id=user.id).exists())
    
    def test_revoke_privilege(self):
        """
        Test para comprobar que se revocan los privilegios de is_staff y is_superuser
        """
        user = Account.objects.create_superuser(**self.data_object)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        user_update = Account.objects.revoke_is_staff(account=user)
        self.assertFalse(user_update.is_staff)
        user_update = Account.objects.revoke_is_superuser(account=user)
        self.assertFalse(user_update.is_superuser)
    
    def test_add_privilege(self):
        """
        Test para comprobar que se añaden los privilegios de is_staff y is_superuser
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        user_update = Account.objects.add_is_staff(account=user)
        self.assertTrue(user_update.is_staff)
        user_update = Account.objects.add_is_superuser(account=user)
        self.assertTrue(user_update.is_superuser)



        
class AccountRetrieveTestCase(APITransactionTestCase):
    """
    Se verifica que la navegación del usuario y las respuestas obtenidas en la obtención del perfil de usuario son las esperadas.
    """
    local_urn = '/account/profile/'

    @classmethod
    def setUpClass(cls):
        cls.start_time = time.time()
        super().setUpClass()
        print(f"\nIniciando la clase de pruebas: {cls.__name__}")
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        print(f"\nFinalizando la clase de pruebas: {cls.__name__}, Tiempo transcurrido: {(time.time()-cls.start_time)}" )
    
    def setUp(self):
        """
        Creación de usuario y obtención del JWT_TOKEN para comprobar la navegación
        """
        self.data_object = test_generate_account_data(self, is_active=True)
        self.user = Account.objects.create_user(**self.data_object)
        self.jwt_token = f"JWT {self.client.post(reverse('token_obtain_pair'),data={'email': self.user.email, 'password': PASSWORD}).data['access']}"
        
    def test_correct_retrieve_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.jwt_token)
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.user.id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_incorrect_retrieve_view_without_credentials(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.user.id}/')
        self.assertNotEqual(response.status_code, 200)

    def test_incorrect_retrieve_view_with_bad_credentials(self):
        """
        Verificación de que no se obtiene los datos de otro usuario si esta autentificado con otro usuario
        """
        #Creación de otra cuenta
        data_object = test_generate_account_data(self, is_active=True)
        user = Account.objects.create_user(**data_object)
        jwt_token = f"JWT {self.client.post(reverse('token_obtain_pair'),data={'email': user.email, 'password': PASSWORD}).data['access']}"
        #Petición
        self.client.credentials(HTTP_AUTHORIZATION=jwt_token)
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.user.id}/')
        self.assertNotEqual(response.status_code, 200)
    
    def test_correct_update_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.jwt_token)
        data_update = {'name':fake.name(), 'last_name':fake.last_name()}
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{self.user.id}/', data=data_update)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.name, response.data['user']['name'])
        self.assertEqual(data_update['name'], response.data['user']['name'])
        self.assertNotEqual(self.user.last_name, response.data['user']['last_name'])
        self.assertEqual(data_update['last_name'], response.data['user']['last_name'])
    
    def test_incorrect_update_view_without_credentials(self):
        data_update = {'name':fake.name(), 'last_name':fake.last_name()}
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{self.user.id}/', data=data_update)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn('user', response.data)
    
    def test_incorrect_update_view_bad_credentials(self):
        """
        Verificación de que no se obtiene los datos de otro usuario si esta autentificado con otro usuario
        """
        #Creación de otra cuenta
        data_object = test_generate_account_data(self, is_active=True)
        user = Account.objects.create_user(**data_object)
        jwt_token = f"JWT {self.client.post(reverse('token_obtain_pair'),data={'email': user.email, 'password': PASSWORD}).data['access']}"
        self.client.credentials(HTTP_AUTHORIZATION=jwt_token)
        #Petición
        data_update = {'name':fake.name(), 'last_name':fake.last_name()}
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{self.user.id}/', data=data_update)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn('user', response.data)
        



    

