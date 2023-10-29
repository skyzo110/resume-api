import pdb
from rest_framework import serializers
from .models import Applicant, Opportunity, Application, User
from .models import Document
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document 
        fields = '__all__'
        

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    @staticmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id'] = user.id
        token['email'] = user.email
        token['username'] = user.username   
        # ...

        return token 

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
    
        pdb.set_trace()

        print(document_data)
        document, created = Document.objects.get_or_create(**document_data)
        if validated_data.get('id'):
            print("saving new applicant")
            pdb.set_trace()
            applicant = Applicant.objects.update(document=document, **validated_data)
        elif validated_data.get('id') is None:
            print("saving new applicant")
            pdb.set_trace()
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
        #extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
