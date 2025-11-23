from rest_framework import serializers
from .models import Vehlossrate

class VehlossrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehlossrate
        fields = '__all__'

