from rest_framework import serializers
from .models import Fields

class FieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = '__all__'
