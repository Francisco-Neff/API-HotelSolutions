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
        Se verifica que el usuario esta activo
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertTrue(user.is_active)

    def test_create_staff_duplicate_unique_fields(self):
        """
        Test para comprobar que la clave de usuario y campos únicos no se repitan.
        """
        Account.objects.create_user(**self.data_object)
        with self.assertRaises(IntegrityError) as error: 
            Account.objects.create_user(**self.data_object)
        self.assertIsInstance(error.exception, IntegrityError)


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


    

