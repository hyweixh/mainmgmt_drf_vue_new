from rest_framework import serializers
from .models import Checklanesoft

class ChecklanesoftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklanesoft
        fields = '__all__'

