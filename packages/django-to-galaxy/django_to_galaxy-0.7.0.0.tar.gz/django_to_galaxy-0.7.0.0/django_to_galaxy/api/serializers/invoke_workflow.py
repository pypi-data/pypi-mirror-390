from rest_framework import serializers

from .upload_to_history import FileSerializer


class DatamapSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, default="")
    src = serializers.CharField()


class InvokeWorkflowSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    history_id = serializers.IntegerField()
    datamap = serializers.DictField(child=DatamapSerializer())


class ExecuteWorkflowSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    galaxy_user_id = serializers.IntegerField()
    fake_datamap = serializers.DictField(child=FileSerializer())


class GenericDictSerializer(serializers.Serializer):
    data = serializers.DictField()
