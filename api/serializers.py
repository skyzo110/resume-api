from rest_framework import serializers
from .models import Applicant, Opportunity, Application, User
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document 
        fields = '__all__'
        
    

class ApplicantSerializer(serializers.ModelSerializer):
   # document = DocumentSerializer ()  # Nested serializer for the document
    class Meta:
        model = Applicant
        fields = '__all__'
    def create(self, validated_data):
        print(validated_data)
        document = validated_data.pop('document')  # Extract the document data
        document_data = {
            'id': document.id,  # Use the ID of the Document object
            'base64_data': document.base64_data,  # Replace this with the actual field name
        }

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
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
