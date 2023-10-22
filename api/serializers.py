from rest_framework import serializers
from .models import Applicant, Opportunity, Application, User
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document 
        fields = '__all__'

class ApplicantSerializer(serializers.ModelSerializer):
    document = DocumentSerializer ()  # Nested serializer for the document
    class Meta:
        model = Applicant
        fields = '__all__'
    def create(self, validated_data):
        print(validated_data)
        document_data = validated_data.pop('document')  # Extract the document data
        print(document_data)
        document, created = Document.objects.get_or_create(**document_data)
        
        # Create the Applicant with the associated Document
        applicant = Applicant.objects.create(document=document, **validated_data)
        return applicant

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserSignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    # You can add any additional validation you need, such as password requirements

    def validate(self, data):
        # You can add custom validation logic here if needed
        return data