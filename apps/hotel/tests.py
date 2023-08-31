import time
from faker import Faker

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from apps.account.tests import test_generate_account_data
from apps.hotel.models import Account, Hotel, HotelMedia, Room, RoomMedia, RoomExtra

# Create your tests here.
fake = Faker()
LOCAL_URL = 'http://127.0.0.1:8000'
PASSWORD = '12345678*Abc'


def test_generate_hotel_data(account):
    data_object = {
        'name' : fake.name(),
        'address' : fake.address(),
        'description' : fake.sentence(),
        'stars' : fake.pyint(max_value=5),
        'updated_by' : account
    }
    return data_object


def test_generate_hotel_media_data(hotel, name_file='hotel_media_test_example.png'):
    data_object = {
        'id_hotel' : hotel,
        'img' : SimpleUploadedFile(name=name_file, content=b'', content_type='image/png')
    }
    return data_object


def test_generate_room_data(hotel, account, room_status=Room.ChoicesStatusRoom.available):
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


def test_generate_room_media_data(id_rooms, name_file='room_media_test_example.png'):
    """
    The "id_rooms" field should be a list of IDs, like a id_rooms = [1, 2, 3, ..., n]
    """
    data_object = {
        'id_rooms' : id_rooms,
        'img' : SimpleUploadedFile(name=name_file, content=b'', content_type='image/png')
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
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.data_object = test_generate_hotel_data(account=self.account)
    
    def test_correct_create_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertEqual(model_object.updated_by, self.account)
    
    def test_correct_update_model(self):
        """
        Test to verify successful update of a model object.
        The system sleeps during test execution to ensure that the "created_at" field is different from the "updated_at" field.
        """
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertEqual(model_object.updated_by, self.account)
        time.sleep(0.00001)
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




class HotelMediaTestCase(TestCase):
    """
    Test to verify the creation of HotelMedia model objects.
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
        self.model = HotelMedia
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.data_object = test_generate_hotel_media_data(hotel=self.hotel)
    
    def tearDown(self):
        """
        Verification that the created object is deleted to destroy files.
        """
        if self.model_object is not None:
            self.model_object.delete()
            self.assertFalse(self.model.objects.filter(id=self.model_object.id).exists())
        return super().tearDown()
    
    def test_correct_create_model(self):
        self.model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=self.model_object.id).exists())
        self.assertEqual(self.model_object.id_hotel, self.hotel)    
    
    def test_correct_update_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertEqual(model_object.id_hotel, self.hotel)
        data_object_upt = self.data_object.copy()
        data_object_upt['img'] = SimpleUploadedFile(name='hotel_media_update_test_example.png', content=b'', content_type='image/png')
        self.model_object = self.model.update_model(self, model_object=model_object, **data_object_upt)
        self.assertTrue(self.model.objects.filter(id=self.model_object.id).exists())
    
    def test_correct_delete_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        model_object.delete()
        self.assertFalse(self.model.objects.filter(id=model_object.id).exists())
        self.model_object = None



class RoomTestCase(TestCase):
    """
    Test to verify the creation of Room model objects.
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
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.data_object = test_generate_room_data(hotel=self.hotel, account=self.account)
    
    def test_correct_create_model(self):
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertIsNotNone(model_object.created_at)
        self.assertIsNotNone(model_object.updated_at)
        self.assertEqual(model_object.id_hotel, self.hotel)
        self.assertEqual(model_object.updated_by, self.account)
    
    def test_incorrect_create_model(self):
        """
        Test to verify that the "name" or "number" fields are included during object creation.
        """
        self.data_object.pop('name')
        self.data_object.pop('number')
        with self.assertRaises(ValidationError) as error: 
            self.model.objects.create(**self.data_object)
        self.assertIsInstance(error.exception, ValidationError)
    
    def test_correct_update_model(self):
        """
        Test to verify successful update of a model object.
        The system sleeps during test execution to ensure that the "created_at" field is different from the "updated_at" field.
        """
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        data_object_upt = self.data_object.copy()
        data_object_upt['name'] = fake.name()
        time.sleep(0.00001)
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
        """
        Test to verify that the "name" or "number" fields are included during object update.
        """
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




class RoomMediaTestCase(TestCase):
    """
    Test to verify the creation of RoomMedia model objects.
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
        self.model = RoomMedia
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        self.data_object = test_generate_room_media_data(id_rooms=[self.room.id])
    
    def tearDown(self):
        """
        Verification that the created object is deleted to destroy files.
        """
        if self.model_object is not None:
            self.model_object.delete()
            self.assertFalse(self.model.objects.filter(id=self.model_object.id).exists())
        return super().tearDown()
    
    def test_correct_create_model(self):
        self.model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=self.model_object.id).exists())
        self.assertTrue(self.model_object.id_rooms.filter(id=self.room.id).exists())   
    
    def test_correct_update_model(self):
        """
        Test to verify that a record is updated in the following scenarios:
        Case 1: Add new image.
        Case 2: Add new object room.
        """
        self.model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=self.model_object.id).exists())
        self.assertTrue(self.model_object.id_rooms.filter(id=self.room.id).exists())  
        #Case 1
        data_object_upt = self.data_object.copy()
        data_object_upt['img'] = SimpleUploadedFile(name='room_media_update_test_example.png', content=b'', content_type='image/png')
        self.model_object = self.model.update_model(self, model_object=self.model_object, **data_object_upt)
        self.assertTrue(self.model.objects.filter(id=self.model_object.id).exists())
        self.assertTrue(self.model_object.id_rooms.filter(id=self.room.id).exists())  
        #Case 2
        data_object_upt = self.data_object.copy()
        room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        data_object_upt['id_rooms'].append(room.id)
        self.model_object = self.model.update_model(self, model_object=self.model_object, **data_object_upt)
        self.assertEqual(self.model_object.id_rooms.count(), len(data_object_upt['id_rooms']))  
        self.assertTrue(self.model_object.id_rooms.filter(id__in=data_object_upt['id_rooms']).exists())  
    
    def test_correct_delete_item(self):
        self.model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=self.model_object.id).exists())
        self.assertTrue(self.model_object.id_rooms.filter(id=self.room.id).exists())   
        self.model_object.delete_item_room(id_room=self.room)
        self.assertTrue(self.model.objects.filter(id=self.model_object.id).exists())
        self.assertFalse(self.model_object.id_rooms.filter(id=self.room.id).exists()) 

    def test_correct_delete_model(self):
        model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        model_object.delete()
        self.assertFalse(self.model.objects.filter(id=model_object.id).exists())
        self.model_object = None