import factory
from factory.declarations import Sequence, SubFactory, LazyAttribute
from factory.faker import Faker
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from apps.accounts.models import User
from apps.hospitals.models import Hospital
from apps.donors.models import Donor
from apps.blood_requests.models import BloodRequest, DonorResponse
from apps.locations.models import State, LocalGovernment
from django.utils import timezone
from datetime import timedelta


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f'user{n}')
    email = Sequence(lambda n: f'user{n}@example.com')
    is_active = True
    is_verified = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default _create to handle password hashing"""
        manager = cls._get_manager(model_class)
        if 'password' not in kwargs:
            kwargs['password'] = 'testpass123'
        return manager.create_user(*args, **kwargs)

class StateFactory(DjangoModelFactory):
    class Meta:
        model = State
        django_get_or_create = ('name',)

    name = Sequence(lambda n: f'State {n}')
    code = Sequence(lambda n: f'ST{n:03d}')

class LocalGovernmentFactory(DjangoModelFactory):
    class Meta:
        model = LocalGovernment
        django_get_or_create = ('name', 'state')

    name = Sequence(lambda n: f'LGA {n}')
    state = SubFactory(StateFactory)

class HospitalFactory(DjangoModelFactory):
    class Meta:
        model = Hospital

    user = SubFactory(UserFactory, role=User.UserRoles.HOSPITAL)
    name = Sequence(lambda n: f'Hospital {n}')
    phone = Sequence(lambda n: f'+234800000{n:04d}')
    address = Faker('address')
    primary_location = SubFactory(LocalGovernmentFactory)
    is_verified = True

    @factory.post_generation
    def service_locations(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for location in extracted:
                self.service_locations.add(location)
        else:
            # By default, add the primary location as a service location
            self.service_locations.add(self.primary_location)

class DonorFactory(DjangoModelFactory):
    class Meta:
        model = Donor

    user = SubFactory(UserFactory, role=User.UserRoles.DONOR)
    phone = Sequence(lambda n: f'+234800000{n:04d}')
    blood_type = 'O+'
    is_available = True

    @factory.post_generation
    def service_locations(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for location in extracted:
                self.service_locations.add(location)

class BloodRequestFactory(DjangoModelFactory):
    class Meta:
        model = BloodRequest

    hospital = SubFactory(HospitalFactory)
    blood_type = 'O+'
    contact_phone = Sequence(lambda n: f'+234800000{n:04d}')
    notes = Faker('text', max_nb_chars=200)
    status = BloodRequest.RequestStatus.OPEN

class DonorResponseFactory(DjangoModelFactory):
    class Meta:
        model = DonorResponse

    request = SubFactory(BloodRequestFactory)
    donor = SubFactory(DonorFactory)
    fulfilled = False