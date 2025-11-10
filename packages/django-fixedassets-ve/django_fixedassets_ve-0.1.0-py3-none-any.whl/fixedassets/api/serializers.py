from rest_framework import serializers
from fixedassets.models.asset import AssetCategory, Asset
from fixedassets.models.movement import Acquisition, Revaluation, Impairment, Disposal
from fixedassets.models.schedule import DepreciationSchedule, DepreciationLine

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta: model = AssetCategory; fields = "__all__"

class AssetSerializer(serializers.ModelSerializer):
    class Meta: model = Asset; fields = "__all__"

class AcquisitionSerializer(serializers.ModelSerializer):
    class Meta: model = Acquisition; fields = ["asset", "date", "memo"]

class RevaluationSerializer(serializers.ModelSerializer):
    class Meta: model = Revaluation; fields = ["asset", "date", "increase_amount", "decrease_amount", "memo"]

class ImpairmentSerializer(serializers.ModelSerializer):
    class Meta: model = Impairment; fields = ["asset", "date", "amount", "memo"]

class DisposalSerializer(serializers.ModelSerializer):
    class Meta: model = Disposal; fields = ["asset", "date", "proceeds", "memo"]

class DepreciationLineSerializer(serializers.ModelSerializer):
    class Meta: model = DepreciationLine; fields = ["schedule", "date", "amount"]