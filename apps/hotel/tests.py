import time, os
from faker import Faker

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from rest_framework.test import APITransactionTestCase, APIClient

from apps.account.tests import test_generate_account_data
from apps.hotel.models import Account, Hotel, HotelMedia, Room, RoomMedia, RoomExtra
from apps.hotel.views import HotelMediaRegisterView

# Create your tests here.
fake = Faker()
LOCAL_URL = 'http://127.0.0.1:8000'
PASSWORD = '12345678*Abc'
IMG_PATH_1= r'.\\media\\media_tests\\img_default_1.png'


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


def test_generate_hotel_media_view_data(hotel, name_file='hotel_media_test_example.png', file_path=IMG_PATH_1):
    data_object = {
        'id_hotel' : hotel,
        'img' :  SimpleUploadedFile(name=name_file, content=open(file_path, 'rb').read(), content_type='image/png')
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


def test_generate_room_media_view_data(id_rooms, name_file='room_media_test_example.png', file_path=IMG_PATH_1):
    """
    The "id_rooms" field should be a list of IDs, like a id_rooms = [1, 2, 3, ..., n]
    """
    data_object = {
        'id_rooms' : id_rooms,
        'img' : SimpleUploadedFile(name=name_file, content=open(file_path, 'rb').read(), content_type='image/png')
    }
    return data_object


def test_generate_room_extra_data(id_rooms, has_internet=False, has_tv=False):
    """
    The "id_rooms" field should be a list of IDs, like a id_rooms = [1, 2, 3, ..., n]
    """
    data_object = {
        'id_rooms' : id_rooms,
        'has_internet' : has_internet,
        'has_tv' : has_tv
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
        self.assertEqual(model_object.price, self.data_object['price'])
    
    def test_incorrect_create_model(self):
        """
        Test to verify can`t create records in next cases.
        Case 1: Duplicate constrains "unique_name_number_per_hotel".
        Case 2: The "name" or "number" fields are included during object creation.
        Case 3:
        """
        model_object = self.model.objects.create(**self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        #Case 1
        with self.assertRaises(ValidationError) as error: 
            self.model.objects.create(**self.data_object)
        self.assertIsInstance(error.exception, ValidationError)
        #Case 2
        data_object = self.data_object.copy()
        data_object.pop('name')
        data_object.pop('number')
        with self.assertRaises(ValidationError) as error: 
            self.model.objects.create(**data_object)
        self.assertIsInstance(error.exception, ValidationError)
        #Case 3
        data_object = self.data_object.copy()
        data_object['room_status'] = 'wrong_status'
        with self.assertRaises(ValidationError) as error: 
            self.model.objects.create(**data_object)
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




class RoomExtraTestCase(TestCase):
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
        self.model = RoomExtra
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        self.data_object = test_generate_room_extra_data(id_rooms=[self.room.id])
    
    def test_correct_create_model(self):
        model_object = self.model.create_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertTrue(model_object.id_rooms.filter(id=self.room.id).exists())
    
    def test_correct_update_model(self):
        model_object = self.model.create_or_update_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertTrue(model_object.id_rooms.filter(id=self.room.id).exists())
        data_object_upt = self.data_object.copy()
        room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        data_object_upt['id_rooms'].append(room.id)
        model_object = self.model.update_model(self, model_object=model_object, **self.data_object)
        self.assertEqual(model_object.id_rooms.count(), len(data_object_upt['id_rooms']))  
        self.assertTrue(model_object.id_rooms.filter(id__in=data_object_upt['id_rooms']).exists())  
    
    def test_correct_create_or_update_model(self):
        """
        Test to verify the proper functioning of the create_or_update_model method. Additionally, 
        it is validated that duplicate records are not created in id_rooms, 
        leaving this field unique based on the booleans.
        Case 1: Create record
        Case 2: Update record
        Case 3: Creation of a new record and updating it with the already created rooms.
        """
        #Case 1
        model_object = self.model.create_or_update_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertTrue(model_object.id_rooms.filter(id=self.room.id).exists())  
        #Case 2
        data_object_upt = self.data_object.copy()
        room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        data_object_upt['id_rooms'].append(room.id)
        model_object = self.model.create_or_update_model(self, **self.data_object)
        self.assertEqual(model_object.id_rooms.count(), len(data_object_upt['id_rooms']))  
        self.assertTrue(model_object.id_rooms.filter(id__in=data_object_upt['id_rooms']).exists())  
        #Case 3
        data_object = test_generate_room_extra_data(id_rooms=[self.room.id], has_internet=True)
        model_object = self.model.create_or_update_model(self, **data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertTrue(model_object.id_rooms.filter(id=self.room.id).exists())
        self.assertEqual(1, self.model.objects.filter(id_rooms=room).count())
        data_object['id_rooms'].append(room.id)
        model_object = self.model.create_or_update_model(self, **data_object)
        self.assertEqual(model_object.id_rooms.count(), len(data_object['id_rooms']))  
        self.assertTrue(model_object.id_rooms.filter(id__in=data_object['id_rooms']).exists())
        self.assertEqual(len(data_object['id_rooms']), self.model.objects.filter(id_rooms=room).count())

    def test_correct_delete_item(self):
        model_object = self.model.create_or_update_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertTrue(model_object.id_rooms.filter(id=self.room.id).exists())   
        model_object.delete_item_room(id_room=self.room)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        self.assertFalse(model_object.id_rooms.filter(id=self.room.id).exists()) 

    def test_correct_delete_model(self):
        model_object = self.model.create_or_update_model(self, **self.data_object)
        self.assertTrue(self.model.objects.filter(id=model_object.id).exists())
        model_object.delete()
        self.assertFalse(self.model.objects.filter(id=model_object.id).exists())




class HotelRegisterTestCase(APITransactionTestCase):
    """
    It is verified that HotelRegisterView navigation are correct.
    """
    local_urn = '/hotel/register/hotel/'

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
        self.client.force_authenticate(user=self.account)
        self.data_object = test_generate_hotel_data(account=self.account.id)
    
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
        self.assertEqual(model_object.address, self.data_object['address'])
        self.assertEqual(model_object.name, self.data_object['name'])
    
    def test_incorrect_register_view(self):
        """
        Test to verify that the creation of new records fails in the following cases:
        #Case 1: Duplicate data.
        #Case 2: Field updated_by don't exists.
        """
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        #Case 1
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        #Case 2
        case_id = True
        while case_id:
            fake_id = fake.pyint(min_value=8000, max_value=9000)
            if not Account.objects.filter(id=fake_id).exists():
                case_id = False
        self.data_object['updated_by'] = fake_id
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('cod', response.data)

    def test_correct_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = self.data_object.copy()
        data_object_upt['name'] = fake.name()
        data_object_upt['stars'] = fake.pyint(max_value=5)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.name, data_object_upt['name'])
        self.assertEqual(model_object.stars, data_object_upt['stars'])
    
    def test_correct_partial_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = {
            'name': fake.name(),
            'stars': fake.pyint(max_value=5)
        }
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.name, data_object_upt['name'])
        self.assertEqual(model_object.stars, data_object_upt['stars'])
    
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




class HotelMediaRegisterTestCase(APITransactionTestCase):
    """
    It is verified that HotelMediaRegister navigation are correct.
    """
    local_urn = '/hotel/register/hotelmedia/'

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
        self.client.force_authenticate(user=self.account)
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.data_object = test_generate_hotel_media_view_data(hotel=self.hotel.id, file_path=IMG_PATH_1)

    def test_incorrect_permission_request(self):
        """
        The test to verify that creating new records or do another request, fails in cases where the requesting user is not of administrator type.
        """
        account = Account.objects.create_user(**test_generate_account_data(is_active=True))
        self.client.force_authenticate(user=account)
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
        self.model.objects.get(id=response.data['id']).delete()
    
    def test_correct_register_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.id_hotel, self.hotel)
        self.assertEqual(model_object.id_hotel.id, response.data['id_hotel']['id'])
        model_object.delete()
    
    def test_correct_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = test_generate_hotel_media_view_data(hotel=self.hotel.id, name_file='image_test.png', file_path=IMG_PATH_1)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{model_object.id}/', data=data_object, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertTrue(os.path.exists(model_object.img.path))
        model_object.delete()
    
    def test_correct_partial_update_model(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = test_generate_hotel_media_view_data(hotel=self.hotel.id, name_file='image_test.png', file_path=IMG_PATH_1)
        data_object.pop('id_hotel')
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{model_object.id}/', data=data_object, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertTrue(os.path.exists(model_object.img.path))
        model_object.delete()

    def test_correct_delete_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        current_id = response.data['id']
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{current_id}/')
        self.assertFalse(self.model.objects.filter(id=current_id).exists())




class RoomRegisterTestCase(APITransactionTestCase):
    """
    It is verified that RoomRegisterView navigation are correct.
    """
    local_urn = '/hotel/register/room/'

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
        self.client.force_authenticate(user=self.account)
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.data_object = test_generate_room_data(hotel=self.hotel.id, account=self.account.id)
    
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
        self.assertEqual(model_object.id_hotel, self.hotel)
        self.assertEqual(model_object.id_hotel.id, response.data['id_hotel']['id'])
        self.assertEqual(model_object.name, self.data_object['name'])
        self.assertEqual(model_object.number, self.data_object['number'])
    
    def test_incorrect_register_view(self):
        """
        Test to verify that the creation of new records fails in the following cases:
        #Case 1: Duplicate data.
        #Case 2: Don`t send name and number fields.
        #Case 3: Send a incorrect room_status_choices.
        #Case 4: Field updated_by don't exists.
        #Case 5: Field id_hotel don't exists.
        """
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        #Case 1
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        #Case 2
        data_object = self.data_object.copy()
        data_object.pop('name')
        data_object.pop('number')
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        #Case 3
        data_object = self.data_object.copy()
        data_object['room_status'] = 'wrong_status'
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        #Case 4
        case_id = True
        while case_id:
            fake_id = fake.pyint(min_value=8000, max_value=9000)
            if not Account.objects.filter(id=fake_id).exists():
                case_id = False
        self.data_object['updated_by'] = fake_id
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        #Case 5
        case_id = True
        while case_id:
            fake_id = fake.pyint(min_value=8000, max_value=9000)
            if not Hotel.objects.filter(id=fake_id).exists():
                case_id = False
        self.data_object['id_hotel'] = fake_id
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('cod', response.data)

    def test_correct_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = self.data_object.copy()
        data_object_upt['name'] = fake.name()
        data_object_upt['number'] = fake.pyint(max_value=5)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.name, data_object_upt['name'])
        self.assertEqual(model_object.number, data_object_upt['number'])
    
    def test_correct_partial_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        data_object_upt = {
            'name': fake.name(),
            'number': fake.pyint()
        }
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{response.data["id"]}/', data=data_object_upt)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertEqual(model_object.name, data_object_upt['name'])
        self.assertEqual(model_object.number, data_object_upt['number'])
    
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




class RoomMediaRegisterTestCase(APITransactionTestCase):
    """
    It is verified that RoomMediaRegister navigation are correct.
    """
    local_urn = '/hotel/register/roommedia/'

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
        self.client.force_authenticate(user=self.account)
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        self.data_object = test_generate_room_media_view_data(id_rooms=[self.room.id], file_path=IMG_PATH_1)

    def test_incorrect_permission_request(self):
        """
        The test to verify that creating new records or do another request, fails in cases where the requesting user is not of administrator type.
        """
        account = Account.objects.create_user(**test_generate_account_data(is_active=True))
        self.client.force_authenticate(user=account)
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
        self.model.objects.get(id=response.data['id']).delete()
    
    def test_correct_register_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertTrue(model_object.id_rooms.filter(id=response.data['id_rooms'][0]['id_room']).exists())
        model_object.delete()
    
    def test_correct_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = test_generate_room_media_view_data(id_rooms=[self.room.id], name_file='room_test.png', file_path=IMG_PATH_1)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{model_object.id}/', data=data_object, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertTrue(os.path.exists(model_object.img.path))
        model_object.delete()
    
    def test_correct_partial_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = test_generate_room_media_view_data(id_rooms=[self.room.id], file_path=IMG_PATH_1)
        data_object.pop('id_rooms')
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{model_object.id}/', data=data_object, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertTrue(os.path.exists(model_object.img.path))
        model_object.delete()

    def test_correct_delete_item_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = {'id_room':model_object.id_rooms.first().id}
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}{model_object.id}/delete_item/', data=data_object, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertFalse(model_object.id_rooms.filter(id=self.room.id).exists())
        self.model.objects.get(id=response.data['id']).delete()

    def test_correct_delete_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        current_id = response.data['id']
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{current_id}/')
        self.assertEqual(response.status_code, 204)
        self.assertIn('cod', response.data)
        self.assertFalse(self.model.objects.filter(id=current_id).exists())

        




class RoomExtraRegisterTestCase(APITransactionTestCase):
    """
    It is verified that RoomExtraRegister navigation are correct.
    """
    local_urn = '/hotel/register/roomextra/'

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
        self.model = RoomExtra
        self.account = Account.objects.create_staff(**test_generate_account_data(is_active=True))
        self.client.force_authenticate(user=self.account)
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        self.data_object = test_generate_room_extra_data(id_rooms=[self.room.id])

    def test_incorrect_permission_request(self):
        """
        The test to verify that creating new records or do another request, fails in cases where the requesting user is not of administrator type.
        """
        account = Account.objects.create_user(**test_generate_account_data(is_active=True))
        self.client.force_authenticate(user=account)
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
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        self.assertTrue(model_object.id_rooms.filter(id=response.data['id_rooms'][0]['id_room']).exists())
        model_object.delete()
    
    def test_correct_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = test_generate_room_extra_data(id_rooms=[self.room.id], has_tv=True)
        response = self.client.put(f'{LOCAL_URL}{self.local_urn}{model_object.id}/', data=data_object)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
    
    def test_correct_partial_update_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = {'id_rooms':[self.room.id],'has_internet':True}
        response = self.client.patch(f'{LOCAL_URL}{self.local_urn}{model_object.id}/', data=data_object)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])

    def test_correct_delete_item_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        model_object = self.model.objects.get(id=response.data['id'])
        data_object = {'id_room':model_object.id_rooms.first().id}
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}{model_object.id}/delete_item/', data=data_object)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertFalse(model_object.id_rooms.filter(id=self.room.id).exists())

    def test_correct_delete_view(self):
        response = self.client.post(f'{LOCAL_URL}{self.local_urn}', data=self.data_object)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cod', response.data)
        self.assertTrue(self.model.objects.filter(id=response.data['id']).exists())
        current_id = response.data['id']
        response = self.client.delete(f'{LOCAL_URL}{self.local_urn}{current_id}/')
        self.assertEqual(response.status_code, 204)
        self.assertIn('cod', response.data)
        self.assertFalse(self.model.objects.filter(id=current_id).exists())




class HotelPublicViewerTestCase(APITransactionTestCase):
    """
    It is verified that HotelPublicViewer navigation are correct.
    """
    local_urn = '/hotel/viewer/hotel/'

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
        self.client.force_authenticate(user=self.account)
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.hotel_media = HotelMedia.objects.create(**test_generate_hotel_media_data(hotel=self.hotel))
        self.room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        self.room_media = RoomMedia.create_model(self, **test_generate_room_media_data(id_rooms=[self.room.id]))
    
    def tearDown(self):
        self.hotel_media.delete()
        self.room_media.delete()
    
    def test_correct_list_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertIn('queryset', response.data)
        self.assertEqual(self.model.objects.all().count(), len(response.data['queryset']))
    
    def test_correct_retrieve_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.hotel.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertEqual(self.hotel.id, response.data['id'])




class HotelPrivateViewerTestCase(APITransactionTestCase):
    """
    It is verified that HotelPrivateViewer navigation are correct.
    """
    local_urn = '/hotel/viewer/private/hotel/'

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
        self.client.force_authenticate(user=self.account)
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.hotel_media = HotelMedia.objects.create(**test_generate_hotel_media_data(hotel=self.hotel))
        self.room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        self.room_media = RoomMedia.create_model(self, **test_generate_room_media_data(id_rooms=[self.room.id]))
    
    def tearDown(self):
        self.hotel_media.delete()
        self.room_media.delete()
    
    def test_correct_list_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertIn('queryset', response.data)
        self.assertEqual(self.model.objects.all().count(), len(response.data['queryset']))
    
    def test_correct_retrieve_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.hotel.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertEqual(self.hotel.id, response.data['id'])
    
    def test_incorrect_permission_request(self):
        """
        The test to verify that creating new records or do another request, fails in cases where the requesting user is not of administrator type.
        """
        self.account = Account.objects.create_user(**test_generate_account_data(is_active=True))
        self.client.force_authenticate(user=self.account)
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}')
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 403)
        self.assertIn('cod', response.data)




class RoomPublicViewerTestCase(APITransactionTestCase):
    """
    It is verified that RoomPublicViewer navigation are correct.
    """
    local_urn = '/hotel/viewer/room/'

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
        self.client.force_authenticate(user=self.account)
        self.hotel =  Hotel.objects.create(**test_generate_hotel_data(account=self.account))
        self.hotel_media = HotelMedia.objects.create(**test_generate_hotel_media_data(hotel=self.hotel))
        self.room = Room.objects.create(**test_generate_room_data(hotel=self.hotel, account=self.account))
        self.room_media = RoomMedia.create_model(self, **test_generate_room_media_data(id_rooms=[self.room.id]))

    def tearDown(self):
        self.hotel_media.delete()
        self.room_media.delete()
    
    def test_correct_list_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertIn('queryset', response.data)
        self.assertEqual(self.model.objects.all().count(), len(response.data['queryset']))
    
    def test_correct_retrieve_view(self):
        response = self.client.get(f'{LOCAL_URL}{self.local_urn}{self.room.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('cod', response.data)
        self.assertEqual(self.room.id, response.data['id'])