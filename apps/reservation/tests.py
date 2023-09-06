import time
from datetime import timedelta
from faker import Faker

from django.test import TestCase
from django.core.exceptions import ValidationError

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


def test_generate_discount_data(discount_rate=None, discount=None, id_update_by=None):
    data_object = {
        'discount_code': fake.name(),
        'discount_rate': discount_rate if discount_rate is not None else fake.pydecimal(left_digits=3, right_digits=2, min_value=1, max_value=100, positive=True),
        'discount': discount if discount is not None else fake.pydecimal(left_digits=4, right_digits=2, min_value=1, max_value=1000.00, positive=True),
        'updated_by':id_update_by
    }
    return data_object


def test_generate_reservation_data(id_room, id_account, id_update_by, guest=None, check_in=None, check_out=None, id_discount=None, has_canceled=False):
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
        'id_discount': id_discount,
        'updated_by': id_update_by
    }
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
        self.data_object = test_generate_discount_data(discount=0, id_update_by=self.account)
    
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
        self.data_object = test_generate_reservation_data(id_room=None, id_account=self.account, id_update_by=self.account, guest=None, check_in=None, check_out=None, id_discount=None, has_canceled=False)
    
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