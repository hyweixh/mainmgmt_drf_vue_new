from rest_framework import serializers
from django.db import transaction
from .models import Holidayfree

class HolidayfreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holidayfree
        fields = '__all__'


