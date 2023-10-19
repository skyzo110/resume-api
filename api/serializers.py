from rest_framework import serializers
from .models import Applicant, Opportunity, Application

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
class CosineSimilaritySerializer(serializers.Serializer):
    profile_matching = serializers.CharField()