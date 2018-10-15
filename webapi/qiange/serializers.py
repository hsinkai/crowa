from rest_framework import serializers


class UselessSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance