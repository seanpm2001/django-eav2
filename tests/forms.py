from django.test import TestCase
from django.contrib.admin.sites import AdminSite

import eav
from eav.admin import *
from .models import Patient
from eav.models import Attribute
from eav.forms import BaseDynamicEntityForm
from django.contrib import admin
from django.core.handlers.base import BaseHandler  
from django.test.client import RequestFactory  
from django.forms import ModelForm


class MockRequest(RequestFactory):  
    def request(self, **request):  
        "Construct a generic request object."  
        request = RequestFactory.request(self, **request)  
        handler = BaseHandler()  
        handler.load_middleware()  
        for middleware_method in handler._request_middleware:  
            if middleware_method(request):  
                raise Exception("Couldn't create request mock object - "  
                                "request middleware returned a response")  
        return request


class MockSuperUser:
    def __init__(self):
        self.is_active = True
        self.is_staff = True

    def has_perm(self, perm):
        return True


request = MockRequest().request()
request.user = MockSuperUser()


class Forms(TestCase):
    def setUp(self):
        eav.register(Patient)
        Attribute.objects.create(name='weight', datatype=Attribute.TYPE_FLOAT)
        Attribute.objects.create(name='color', datatype=Attribute.TYPE_TEXT)
        self.instance = Patient.objects.create(name='Jim Morrison')
        self.site = AdminSite()

    def test_fields(self):
        admin = BaseEntityAdmin(Patient, self.site)
        admin.form = BaseDynamicEntityForm
        view = admin.change_view(request, str(self.instance.pk))

        own_fields = 1
        adminform = view.context_data['adminform']

        self.assertEqual(
            len(adminform.form.fields), Attribute.objects.count() + own_fields
        )

    def test_submit(self):
        class PatientForm(ModelForm):
            class Meta:
                model = Patient
                fields = '__all__'

        self.instance.eav.color = 'Blue'
        form = PatientForm(self.instance.__dict__, instance=self.instance)
        jim = form.save()

        self.assertEqual(jim.eav.color, 'Blue')