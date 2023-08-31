import time
from faker import Faker

from django.test import TestCase
from django.db.utils import IntegrityError
from django.urls import reverse
from django.core.exceptions import ValidationError

from rest_framework.test import APITransactionTestCase

from apps.account.models import Account

# Create your tests here.
fake = Faker()
LOCAL_URL = 'http://127.0.0.1:8000'
PASSWORD = '12345678*Abc'


def test_generate_account_data(is_active=None):
    data_object = {
        'email' : fake.email(),
        'full_name' : fake.name(),
        'password' : PASSWORD,
    }

    if is_active is None:
        is_active = fake.pybool()
    data_object['is_active'] = is_active
    return data_object



class VerifyJWTokenTestCase(APITransactionTestCase):
    """
    Test to verify that authentication through JWT is accurate.
    """
    local_urn = '/account/profile/'

    @classmethod
    def setUpClass(self):
        self.start_time = time.time()
        super().setUpClass()
        print(f"\nStarting the testing class: {self.__name__}")
    
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        print(f"\nFinishing the testing class: {self.__name__}, Elapsed time: {(time.time()-self.start_time)}" ) 
    
    def setUp(self):
        self.model = Account
        self.data_object = test_generate_account_data(is_active=True)
        self.user = self.model.objects.create_user(**self.data_object)
        self.jwt_token = f"JWT {self.client.post(reverse('token_obtain_pair'),data={'email': self.user.email, 'password': PASSWORD}).data['access']}"
        
    def test_correct_retrieve_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.jwt_token)
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.user.id}/')
        self.assertEqual(response.status_code, 200)




class AccountTestCase(TestCase):
    """
    Test to verify the creation of Account model objects.
    """
    @classmethod
    def setUpClass(self):
        self.start_time = time.time()
        super().setUpClass()
        print(f"\nStarting the testing class: {self.__name__}")
    
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        print(f"\nFinishing the testing class: {self.__name__}, Elapsed time: {(time.time()-self.start_time)}" )
    
    def setUp(self):
        self.data_object = test_generate_account_data(is_active=True)
    
    def test_correct_create_user(self):
        """
        Test to verify the creation of a new user.
        It is checked that the user is active.
        It is verified that is_staff is False and is_superuser is False.
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_incorrect_create_user_bad_password(self):
        self.data_object['password'] = 'pass'
        with self.assertRaises(ValidationError) as error: 
            Account.objects.create_user(**self.data_object)
        self.assertIsInstance(error.exception, ValidationError)
    
    def test_incorrect_create_user_without_password(self):
        self.data_object.pop('password')
        with self.assertRaises(ValidationError) as error: 
            Account.objects.create_user(**self.data_object)
        self.assertIsInstance(error.exception, ValidationError)

    def test_correct_create_user_inactive(self):
        """
        Test to verify the creation of a new user with is_active set to False.
        It is checked that the user is inactive.
        It is verified that is_staff is False and is_superuser is False.
        """
        self.data_object = test_generate_account_data(is_active=False)
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_correct_create_user_staff(self):
        """
        Test to verify the creation of a new staff user.
        It is checked that the user is active.
        It is verified that is_staff is True and is_superuser is False.
        """
        user = Account.objects.create_staff(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_correct_create_user_superuser(self):
        """
        Test to verify the creation of a new superuser.
        It is checked that the user is active.
        It is verified that is_staff is True and is_superuser is True.
        """
        user = Account.objects.create_superuser(**self.data_object)
        self.assertTrue(Account.objects.filter(id=user.id).exists())
        self.assertTrue(Account.objects.filter(email = self.data_object['email']).exists())
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_incorrect_create_user_duplicate_unique_fields(self):
        """
        Test to verify that user keys and unique fields do not repeat.
        """
        Account.objects.create_user(**self.data_object)
        with self.assertRaises(IntegrityError) as error: 
            Account.objects.create_user(**self.data_object)
        self.assertIsInstance(error.exception, IntegrityError)
    
    def test_correct_update_user(self):
        """
        Test to verify successful user update.
        It is checked that even if the is_staff field is sent, it is not updated.
        Email update is verified.
        Password update is verified
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
    
    def test_correct_delete_logical(self):
        """
        Test to verify that the user becomes inactive after performing a soft delete.
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(user.is_active)
        user_inactive = Account.objects.delete_logical(account=user)
        self.assertFalse(user_inactive.is_active)
    
    def test_correct_delete_physical(self):
        """
        Test to verify that the user becomes inactive after performing a hard delete.
        It is verified that the record does not exist in the database.
        """
        user = Account.objects.create_user(**self.data_object)
        self.assertTrue(Account.objects.delete_physical(account=user))
        self.assertFalse(Account.objects.filter(id=user.id).exists())
    
    def test_correct_revoke_privilege(self):
        """
        Test to verify that is_staff and is_superuser privileges are revoked.
        """
        user = Account.objects.create_superuser(**self.data_object)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        user_update = Account.objects.revoke_is_staff(account=user)
        self.assertFalse(user_update.is_staff)
        user_update = Account.objects.revoke_is_superuser(account=user)
        self.assertFalse(user_update.is_superuser)
    
    def test_correct_add_privilege(self):
        """
        Test to verify that is_staff and is_superuser privileges are added.
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
    It is verified that user navigation and the responses obtained in fetching the user profile are as expected.
    """
    local_urn = '/account/profile/'

    @classmethod
    def setUpClass(self):
        self.start_time = time.time()
        super().setUpClass()
        print(f"\nStarting the testing class: {self.__name__}")
    
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        print(f"\nFinishing the testing class: {self.__name__}, Elapsed time: {(time.time()-self.start_time)}" )
    
    def setUp(self):
        """
        User creation and obtaining the JWT_TOKEN to verify navigation.
        """
        self.data_object = test_generate_account_data(is_active=True)
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
        Ensuring that data from another user is not accessed while authenticated with a different user.
        """
        #Create another account
        data_object = test_generate_account_data(is_active=True)
        user = Account.objects.create_user(**data_object)
        jwt_token = f"JWT {self.client.post(reverse('token_obtain_pair'),data={'email': user.email, 'password': PASSWORD}).data['access']}"
        #Request with other id
        self.client.credentials(HTTP_AUTHORIZATION=jwt_token)
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.user.id}/')
        self.assertNotEqual(response.status_code, 200)
    
    def test_correct_update_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.jwt_token)
        data_update = {'full_name':fake.name()}
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{self.user.id}/', data=data_update)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.full_name, response.data['user']['full_name'])
        self.assertEqual(data_update['full_name'], response.data['user']['full_name'])
    
    def test_incorrect_update_view_without_credentials(self):
        data_update = {'full_name':fake.name()}
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{self.user.id}/', data=data_update)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn('user', response.data)
    
    def test_incorrect_update_view_bad_credentials(self):
        """
        Ensuring that data of another user isn't updated while authenticated with a different user.
        """
        #Creación another account.
        data_object = test_generate_account_data(is_active=True)
        user = Account.objects.create_user(**data_object)
        jwt_token = f"JWT {self.client.post(reverse('token_obtain_pair'),data={'email': user.email, 'password': PASSWORD}).data['access']}"
        self.client.credentials(HTTP_AUTHORIZATION=jwt_token)
        #Request.
        data_update = {'full_name':fake.name()}
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{self.user.id}/', data=data_update)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn('user', response.data)
        



class AccountRegisterUserTestCase(APITransactionTestCase):
    """
    It is verified that user navigation and user creation are correct.
    """
    local_urn = '/account/register/user/'

    @classmethod
    def setUpClass(self):
        self.start_time = time.time()
        super().setUpClass()
        print(f"\nStarting the testing class: {self.__name__}")
    
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        print(f"\nFinishing the testing class: {self.__name__}, Elapsed time: {(time.time()-self.start_time)}" )
    
    def setUp(self):
        self.data_object = test_generate_account_data(is_active=True)
        
    def test_correct_register_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
    
    def test_incorrect_register_view(self):
        """
        Test to verify that a record is not created in the following scenarios:
        Case 1: Data is not sent correctly by removing the email field.
        Case 2: Data is not sent correctly by removing the full_name field.
        Case 3: The password field is not sent.
        Case 4: A password is sent that does not meet the requirements.
        """
        #Case 1
        data_object = self.data_object
        data_object.pop('email')
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        #Case 2
        data_object = self.data_object
        data_object.pop('full_name')
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        #Case 3
        data_object = self.data_object
        data_object.pop('password')
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        #Case 4
        data_object = self.data_object
        data_object['password'] = 'pass'
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
    
    def test_incorrect_register_view_duplicate_unique_fields(self):
        """
        Test to verify that a record is not created in case an attempt is made to register another user with a duplicate email.
        """
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
    


class AccountStaffRegisterViewTestCase(APITransactionTestCase):
    """
    It is verified that user navigation and the creation of staff-type users are correct.
    """
    local_urn = '/account/register/staff/'

    @classmethod
    def setUpClass(self):
        self.start_time = time.time()
        super().setUpClass()
        print(f"\nStarting the testing class: {self.__name__}")
    
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        print(f"\nFinishing the testing class: {self.__name__}, Elapsed time: {(time.time()-self.start_time)}" )
    
    def setUp(self):
        self.model = Account
        self.data_staff = test_generate_account_data(is_active=True)
        self.staff = self.model.objects.create_staff(**self.data_staff)
        self.client.force_authenticate(user=self.staff)
        self.data_object = test_generate_account_data(is_active=True)
        
    def test_correct_register_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
    
    def test_incorrect_update_view(self):
        """
        Test to verify that the update method is disabled.
        """
        data_update = {'full_name':fake.name()}
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{self.staff.id}/', data=data_update)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 405)
    
    def test_correct_partial_update_view(self):
        data_update = {'full_name':fake.name()}
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{self.staff.id}/', data=data_update)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.staff.full_name, response.data['user']['full_name'])
        self.assertEqual(data_update['full_name'], response.data['user']['full_name'])
    
    def test_correct_delete_physical_view(self):
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_active)
        superuser = self.model.objects.create_superuser(**self.data_object)
        self.client.force_authenticate(user=superuser)
        user_id = user.id
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{user_id}/delete_physical/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.model.objects.filter(id=user_id).exists())
    
    def test_incorrect_delete_physical_view(self):
        """
        Test to verify that the user is not deactivated if the requesting account is not a superuser,
        """
        staff_id = self.staff.id
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{staff_id}/delete_physical/', data={})
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.filter(id=staff_id).exists())
    
    def test_correct_delete_logical_view(self):
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_active)
        superuser = self.model.objects.create_superuser(**self.data_object)
        self.client.force_authenticate(user=superuser)
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{user.id}/delete_logical/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.model.objects.get(id=user.id).is_active)
    
    def test_incorrect_delete_logical_view(self):
        """
        Test to verify that the user is not deleted if the requesting account is not a superuser.
        """
        staff_id = self.staff.id
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{staff_id}/delete_logical/', data={})
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.filter(id=staff_id).exists())

    def test_correct_destroy_view(self):
        """
        Test to verify that the destroy method is disabled.
        """
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{self.staff.id}/')
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 405)
    
    def test_correct_activate_user_view(self):
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_active)
        superuser = self.model.objects.create_superuser(**self.data_object)
        self.client.force_authenticate(user=superuser)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/activate_user/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.get(id=user.id).is_active)
    
    def test_incorrect_activate_user_view(self):
        """
        Test to verify that the user is not reactivated if the requesting account is not a superuser.
        """
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_active)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/activate_user/', data={})
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(self.model.objects.get(id=user.id).is_active)

    def test_correct_add_staff_view(self):
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_staff)
        superuser = self.model.objects.create_superuser(**self.data_object)
        self.client.force_authenticate(user=superuser)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/add_staff/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.get(id=user.id).is_staff)
    
    def test_incorrect_add_staff_view(self):
        """
        Test to verify that the staff privilege is not added if the requesting account is not a superuser.
        """
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_staff)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/add_staff/', data={})
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(self.model.objects.get(id=user.id).is_staff)
    
    def test_correct_revoke_staff_view(self):
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_staff(**user_data)
        self.assertTrue(user.is_staff)
        superuser = self.model.objects.create_superuser(**self.data_object)
        self.client.force_authenticate(user=superuser)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/revoke_staff/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.model.objects.get(id=user.id).is_staff)
    
    def test_incorrect_revoke_staff_view(self):
        """
        Test to verify that the superuser privilege is not restricted if the requesting account is not a superuser.
        """
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_staff(**user_data)
        self.assertTrue(user.is_staff)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/revoke_staff/', data={})
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.get(id=user.id).is_staff)
    
    def test_correct_add_superuser_view(self):
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_superuser)
        superuser = self.model.objects.create_superuser(**self.data_object)
        self.client.force_authenticate(user=superuser)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/add_superuser/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.get(id=user.id).is_superuser)
    
    def test_incorrect_add_superuser_view(self):
        """
        Test to verify that the superuser privilege is not added if the requesting account is not a superuser.
        """
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_user(**user_data)
        self.assertFalse(user.is_superuser)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/add_superuser/', data={})
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(self.model.objects.get(id=user.id).is_superuser)
    
    def test_correct_revoke_superuser_view(self):
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_superuser(**user_data)
        self.assertTrue(user.is_superuser)
        superuser = self.model.objects.create_superuser(**self.data_object)
        self.client.force_authenticate(user=superuser)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/revoke_superuser/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.model.objects.get(id=user.id).is_superuser)
    
    def test_incorrect_revoke_superuser_view(self):
        """
        Test to verify that the superuser privilege is not restricted if the requesting account is not a superuser.
        """
        user_data = test_generate_account_data(is_active=False)
        user = self.model.objects.create_superuser(**user_data)
        self.assertTrue(user.is_superuser)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{user.id}/revoke_superuser/', data={})
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.get(id=user.id).is_superuser)
    


class AccountRegisterSuperUserTestCase(APITransactionTestCase):
    """
    It is verified that user navigation and user creation are correct.
    """
    local_urn = '/account/register/superuser/'

    @classmethod
    def setUpClass(self):
        self.start_time = time.time()
        super().setUpClass()
        print(f"\nStarting the testing class: {self.__name__}")
    
    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        print(f"\nFinishing the testing class: {self.__name__}, Elapsed time: {(time.time()-self.start_time)}" )
    
    def setUp(self):
        self.model = Account
        self.data_superuser = test_generate_account_data(is_active=True)
        self.superuser = self.model.objects.create_superuser(**self.data_superuser)
        self.client.force_authenticate(user=self.superuser)
        self.data_object = test_generate_account_data(is_active=True)
        
    def test_correct_register_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        model_object = self.model.objects.get(id=response.data['user']['id'])
        self.assertTrue(model_object.is_superuser)
    
    def test_incorrect_register_view(self):
        """
        Test to verify that a record is not created in the following scenarios:
        Case 1: Data is not sent correctly by removing the email field.
        Case 2: Data is not sent correctly by removing the full_name field.
        Case 3: The password field is not sent.
        Case 4: A password is sent that does not meet the requirements.
        Case 5: The request is not sent by a SuperUser.
        """
        #Case 1
        data_object = self.data_object
        data_object.pop('email')
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        #Case 2
        data_object = self.data_object
        data_object.pop('full_name')
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        #Case 3
        data_object = self.data_object
        data_object.pop('password')
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        #Case 4
        data_object = self.data_object
        data_object['password'] = 'pass'
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        #Case 5
        data_object = self.data_object
        user_staff = test_generate_account_data(is_active=False)
        user = self.model.objects.create_staff(**user_staff)
        self.client.force_authenticate(user=user)
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
    
    def test_incorrect_register_view_duplicate_unique_fields(self):
        """
        Test to verify that a record is not created in the case of attempting to register another user with the same email.
        """
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
    