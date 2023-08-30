import time
from faker import Faker

from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.account.tests import test_generate_account_data
from apps.hotel.models import Account, Hotel, Room

# Create your tests here.
fake = Faker()
LOCAL_URL = 'http://127.0.0.1:8000'
PASSWORD = '12345678*Abc'


def test_generate_hotel_data(self, account):
    data_object = {
        'name' : fake.name(),
        'address' : fake.address(),
        'description' : fake.sentence(),
        'stars' : fake.pyint(max_value=5),
        'updated_by' : account
    }
    return data_object


def test_generate_room_data(self, hotel, account, room_status=Room.ChoicesStatusRoom.available):
    data_object = {
        'id_hotel' : hotel,
        'name' : fake.name(),
        'description' : fake.sentence(),
        'number' : fake.pyint(min_value=1, max_value=1500),
        'room_status' : room_status,
        'price' : fake.pydecimal(left_digits=4, right_digits=2, positive=True),
        'room_capacity' : fake.pyint(min_value=1, max_value=10),
        'num_bed' : fake.pyint(min_value=1, max_value=12),
        'updated_by' : account
    }
    return data_object




class HotelTestCase(TestCase):
    """
    Test to verify the creation of Hotel model objects.
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
        self.model = Hotel
        self.account = Account.objects.create_staff(**test_generate_account_data(self, is_active=True))
        self.data_object = test_generate_hotel_data(self, account=self.account)
    
    def test_correct_create_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertEqual(model_object.updated_by, self.account)
    
    def test_correct_update_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        data_object_upt = self.data_object.copy()
        data_object_upt['name'] = fake.name()
        model_object = self.model.update_model(self, model_object=model_object, **data_object_upt)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertEqual(model_object.name, data_object_upt['name'])
        self.assertNotEqual(model_object.name, self.data_object['name'])
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertNotEqual(model_object.created_at, model_object.updated_at)
        self.assertEqual(model_object.updated_by, self.account)

    def test_correct_delete_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        model_object.delete()
        self.assertFalse(self.model.objects.filter(id=model_object.id).exists())




class RoomTestCase(TestCase):
    """
    Test to verify the creation of Hotel model objects.
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
        self.model = Room
        self.account = Account.objects.create_staff(**test_generate_account_data(self, is_active=True))
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(self, account=self.account))
        self.data_object = test_generate_room_data(self, hotel=self.hotel, account=self.account)
    
    def test_correct_create_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertEqual(model_object.id_hotel, self.hotel)
        self.assertEqual(model_object.updated_by, self.account)
    
    def test_incorrect_create_model(self):
        self.data_object.pop('name')
        self.data_object.pop('number')
        with self.assertRaises(ValidationError) as error: 
            self.model.objects.create(**self.data_object)
        self.assertIsInstance(error.exception, ValidationError)
    
    def test_correct_update_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        data_object_upt = self.data_object.copy()
        data_object_upt['name'] = fake.name()
        model_object = self.model.update_model(self, model_object=model_object, **data_object_upt)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertEqual(model_object.name, data_object_upt['name'])
        self.assertNotEqual(model_object.name, self.data_object['name'])
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertNotEqual(model_object.created_at, model_object.updated_at)
        self.assertEqual(model_object.id_hotel, self.hotel)
        self.assertEqual(model_object.updated_by, self.account)
    
    def test_incorrect_update_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        data_object_upt = self.data_object.copy()
        data_object_upt['name'] = None
        data_object_upt['number'] = None
        with self.assertRaises(ValidationError) as error: 
            self.model.update_model(self, model_object=model_object, **data_object_upt)
        self.assertIsInstance(error.exception, ValidationError)
    
    def test_correct_delete_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        model_object.delete()
        self.assertFalse(self.model.objects.filter(id=model_object.id).exists())