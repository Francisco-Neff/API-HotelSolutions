import time
from datetime import timedelta
from faker import Faker

from django.test import TestCase
from rest_framework.test import APITransactionTestCase

from apps.hotel.models import Hotel, Room
from apps.hotel.tests import test_generate_hotel_data, test_generate_room_data
from apps.account.models import Account
from apps.account.tests import test_generate_account_data
from apps.reservation.models import Reservation, Discount

# Create your tests here.
fake = Faker()
LOCAL_URL = 'http://127.0.0.1:8000'


def test_generate_new_room(id_account=None, id_hotel=None, room_status=Room.ChoicesStatusRoom.available):
    if id_account is None:
        id_account = Account.objects.create_user(**test_generate_account_data(is_active=True))
    
    if id_hotel is None:
        id_hotel = Hotel.objects.create(**test_generate_hotel_data(account=id_account))

    room = Room.objects.create(**test_generate_room_data(hotel=id_hotel, account=id_account, room_status=room_status))
    return room


def test_generate_discount_data(discount_rate=None, discount=None, id_updated_by=None):
    data_object = {
        'discount_code': fake.name(),
        'discount_rate': discount_rate if discount_rate is not None else fake.pydecimal(left_digits=3, right_digits=2, min_value=1, max_value=100, positive=True),
        'discount': discount if discount is not None else fake.pydecimal(left_digits=4, right_digits=2, min_value=1, max_value=1000.00, positive=True),
        'updated_by':id_updated_by
    }
    return data_object


def test_generate_reservation_data(id_room, id_account, id_updated_by, guest=None, check_in=None, check_out=None, id_discount=None, has_canceled=False):
    if check_in is None:
        check_in = fake.date_this_year(before_today=False, after_today=False)
    
    if check_out is None:
        check_out = fake.date_between(start_date=(check_in+timedelta(days=1)), end_date=(check_in+timedelta(days=5)))

    if id_room is None:
        id_room = test_generate_new_room(id_account=None, id_hotel=None, room_status=Room.ChoicesStatusRoom.available)

    data_object = {
        'id_room' : id_room,
        'id_account': id_account,
        'guest': 1 if guest is None else guest,
        'check_in': check_in,
        'check_out': check_out,
        'has_canceled': has_canceled,
        'updated_by': id_updated_by
    }

    if id_discount is not None:
        data_object['id_discount'] = id_discount

    return data_object




class DiscountTestCase(TestCase):
    """
    Test to verify the creation of Discount model objects.
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
        self.model = Discount
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.data_object = test_generate_discount_data(discount=0, id_updated_by=self.account)
    
    def test_correct_create_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertEqual(model_object.updated_by, self.account)
    
    def test_correct_update_model(self):
        """
        The system sleeps during test execution to ensure that the "created_at" field is different from the "updated_at" field.
        """
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertEqual(model_object.updated_by, self.account)
        time.sleep(0.00001)
        data_object_upt = self.data_object.copy()
        data_object_upt['discount_code'] = fake.name()
        model_object = self.model.update_model(self, model_object=model_object, **data_object_upt)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertEqual(model_object.discount_code, data_object_upt['discount_code'])
        self.assertNotEqual(model_object.discount_code, self.data_object['discount_code'])
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertNotEqual(model_object.created_at, model_object.updated_at)
        self.assertEqual(model_object.updated_by, self.account)

    def test_correct_delete_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        model_object.delete()
        self.assertFalse(self.model.objects.filter(id=model_object.id).exists())




class ReservationTestCase(TestCase):
    """
    Test to verify the creation of Reservation model objects.
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
        self.model = Reservation
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.data_object = test_generate_reservation_data(id_room=None, id_account=self.account, id_updated_by=self.account, guest=None, check_in=None, check_out=None, id_discount=None, has_canceled=False)
    
    def test_correct_create_model(self):
        print(self.data_object)
        model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertEqual(model_object.updated_by, self.account)
    
    def test_correct_update_model(self):
        """
        The system sleeps during test execution to ensure that the "created_at" field is different from the "updated_at" field.
        """
        model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertEqual(model_object.updated_by, self.account)
        time.sleep(0.00001)
        data_object_upt = self.data_object.copy()
        data_object_upt['guest'] = fake.pyint()
        model_object = self.model.update_model(self, model_object=model_object, **data_object_upt)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertEqual(model_object.guest, data_object_upt['guest'])
        self.assertNotEqual(model_object.guest, self.data_object['guest'])
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertNotEqual(model_object.created_at, model_object.updated_at)
        self.assertEqual(model_object.updated_by, self.account)

    def test_correct_delete_model(self):
        model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        model_object.delete()
        self.assertFalse(self.model.objects.filter(id=model_object.id).exists())




class ReservationRegisterTestCase(APITransactionTestCase):
    """
    It is verified that ReservationRegisterView navigation are correct.
    """
    local_urn = '/reservation/register/reservation/'

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
        self.model = Reservation
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.id_room = test_generate_new_room(id_account=None, id_hotel=None, room_status=Room.ChoicesStatusRoom.available)
        self.data_object = test_generate_reservation_data(id_room=self.id_room.id, id_account=self.account.id, id_updated_by=self.account.id, guest=None, check_in=None, check_out=None, id_discount=None, has_canceled=False)
        self.client.force_authenticate(user=self.account)
    
    def test_incorrect_permission_request(self):
        """
        The test to verify that creating new records or do another request, fails in cases where the requesting user is not of administrator type.
        """
        self.account = Account.objects.create_user(**test_generate_account_data(is_active=True))
        self.client.force_authenticate(user=self.account)
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertEqual(response.status_code, 403)
        self.assertIn('cod', response.data)
    
    def test_correct_list_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
    
    def test_correct_retrieve_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        current_id = response.data['id']
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{current_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertEqual(current_id, response.data['id'])
    
    def test_correct_register_view(self):
        """
        Test to verify successful create of a model object.
        Case 1: Without Discount
        Case 2: With Discount
        """
        #Case 1
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.id_account, self.account)
        self.assertEqual(model_object.id_room, self.id_room)
        self.assertEqual(model_object.check_in.date(), self.data_object['check_in'])
        self.assertEqual(model_object.check_out.date(), self.data_object['check_out'])
        self.assertEqual(model_object.has_canceled, self.data_object['has_canceled'])
        #Case 2
        id_discount = Discount.objects.create(**test_generate_discount_data(discount=0, id_updated_by=self.account))
        self.id_room = test_generate_new_room(id_account=None, id_hotel=None, room_status=Room.ChoicesStatusRoom.available)
        self.data_object = test_generate_reservation_data(id_room=self.id_room.id, id_account=self.account.id, id_updated_by=self.account.id, guest=None, check_in=None, check_out=None, id_discount=id_discount.id, has_canceled=False)
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.id_account, self.account)
        self.assertEqual(model_object.id_room, self.id_room)
        self.assertEqual(model_object.id_discount, id_discount)
        self.assertEqual(model_object.check_in.date(), self.data_object['check_in'])
        self.assertEqual(model_object.check_out.date(), self.data_object['check_out'])
        self.assertEqual(model_object.has_canceled, self.data_object['has_canceled'])
    
    def test_correct_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = self.data_object.copy()
        data_object_upt['has_canceled'] = True
        data_object_upt['guest'] = fake.pyint(max_value=5)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.has_canceled, data_object_upt['has_canceled'])
        self.assertEqual(model_object.guest, data_object_upt['guest'])
    
    def test_correct_partial_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = {
            'has_canceled': True,
            'guest': fake.pyint(max_value=5)
        }
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.has_canceled, data_object_upt['has_canceled'])
        self.assertEqual(model_object.guest, data_object_upt['guest'])
    
    def test_correct_delete_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        current_id = response.data["id"]
        self.assertTrue(self.model.objects.filter(id=current_id).exists())
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{current_id}/')
        self.assertEqual(response.status_code, 204)
        self.assertIn('cod', response.data)
        self.assertFalse(self.model.objects.filter(id=current_id).exists())




class DiscountRegisterTestCase(APITransactionTestCase):
    """
    It is verified that ReservationRegisterView navigation are correct.
    """
    local_urn = '/reservation/register/discount/'

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
        self.model = Discount
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.data_object = test_generate_discount_data(discount_rate=None, discount=0, id_updated_by=self.account.id)
        self.client.force_authenticate(user=self.account)
    
    def test_incorrect_permission_request(self):
        """
        The test to verify that creating new records or do another request, fails in cases where the requesting user is not of administrator type.
        """
        self.account = Account.objects.create_user(**test_generate_account_data(is_active=True))
        self.client.force_authenticate(user=self.account)
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertEqual(response.status_code, 403)
        self.assertIn('cod', response.data)
    
    def test_correct_list_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
    
    def test_correct_retrieve_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        current_id = response.data['id']
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{current_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertEqual(current_id, response.data['id'])
    
    def test_correct_register_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.updated_by, self.account)
        self.assertEqual(model_object.discount, self.data_object['discount'])
        self.assertEqual(model_object.discount_code, self.data_object['discount_code'])
    
    def test_correct_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = self.data_object.copy()
        data_object_upt['discount_rate'] = fake.pyint(max_value=5)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.discount_rate, data_object_upt['discount_rate'])
    
    def test_correct_partial_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = {
            'discount_code': fake.name(),
            'discount_rate': fake.pyint(max_value=5)
        }
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.discount_code, data_object_upt['discount_code'])
        self.assertEqual(model_object.discount_rate, data_object_upt['discount_rate'])
    
    def test_correct_delete_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        current_id = response.data["id"]
        self.assertTrue(self.model.objects.filter(id=current_id).exists())
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{current_id}/')
        self.assertEqual(response.status_code, 204)
        self.assertIn('cod', response.data)
        self.assertFalse(self.model.objects.filter(id=current_id).exists())