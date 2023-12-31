import base64
import shutil
import os
from django.forms import ValidationError
from django.shortcuts import render
from inspect import Traceback
import pdb
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from django.http import Http404
from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny
from .models import Document, Opportunity, Applicant, Application, SortApplication, User
from .serializers import DocumentSerializer, OpportunitySerializer, ApplicantSerializer, ApplicationSerializer ,UserSerializer 
from .service import submit_application, generate_token, send_emails
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.admin import UserAdmin
from datetime import date
from django.http import HttpResponseRedirect
from .forms import CustomUserAdminForm
from django.contrib.auth.views import LoginView
import jwt
from django.contrib.auth.hashers import make_password




def user_list(request):
    users = User.objects.all()  # Query the users from your model
    context = {'users': users}
    return render(request, 'user_list.html', context)

User = get_user_model()
admin.site.unregister(User)

# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserAdminForm

#     def add_view(self, request, form_url='', extra_context=None):
#         if request.method == 'POST':
#             # Create a new user with the submitted data
#             form = self.add_form(request.POST)
#             if form.is_valid():
#                 user = form.save()
#                 self.message_user(request, "User created successfully")
#                 return HttpResponseRedirect(reverse('admin:yourapp_customuser_changelist'))
#         else:
#             form = self.add_form()

#         return super(CustomUserAdmin, self).add_view(request, form_url, extra_context)





@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        data = request.data
        email = data.get("email")
        password = data.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
 
        #check if user is HR or not
        
            

        if user is not None:
            # Generate a token for the authenticated user
            token = generate_token(user)

            
            return Response({'message': 'User logged in successfully', 'token': token,"id":user.id,"is_superusr":user.is_superuser}, status=status.HTTP_200_OK)
            
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

       # 



class DocumentCreateView(APIView):
    def post(self, request, format=None):
        document_serializer = DocumentSerializer(data=request.data)
        if document_serializer.is_valid():
            document = document_serializer.save()
            return Response({'document_id': document.id}, status=status.HTTP_201_CREATED)
        return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RegistrationView(APIView):
    def post(self, request):
       # print(request.headers)
   
        serializer = UserSerializer(data=request.data)
        print("request.data",request.data  )
        if serializer.is_valid():
            print("valid")
            is_superuser = request.data.get("is_superuser", False)  # Set to True if the user should be a superuser
            user = serializer.save(is_staff=False, is_superuser=False)

            if is_superuser:
                message = 'HR registered successfully'
            else:
                message = 'User registered successfully'
                
                applicant=Applicant.objects.create(user_ptr_id=user.id)
                applicant.save()


            # Generate a token for the registered user
            token = generate_token(user)

            # Include the token in the response
            return Response({'message': message, 'access_token': token,"id":user.id }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplicantRegistrationView(generics.CreateAPIView):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    def perform_create(self, serializer):
        # Exclude the 'groups' field from the serializer before saving
        serializer.validated_data.pop('groups', None)
        serializer.validated_data.pop('user_permissions', None)
         # Get the password from the serializer data
        password = serializer.validated_data.get('password')

        # Encode the password with a secret key using Django's make_password function
        encoded_password = make_password(password)

        # Replace the original password with the encoded password
        serializer.validated_data['password'] = encoded_password

        # Save the user with the encoded password
        user = serializer.save()

    
        

@api_view(['POST'])
def submit_opportunity(request):
    if request.method == 'POST':
        data =request.data
        print(data)
        data["select_value"] = int(data["select_value"] )
        # Convert the 'due_date' to the expected format
        due_date = datetime.strptime(data['due_date'], '%m/%d/%Y').strftime('%Y-%m-%d')

# Update the data with the formatted 'due_date'
        data['due_date'] = due_date
        print(data)
        serializer = OpportunitySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Opportunity submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, 'message': 'Validation failed'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




@api_view(['GET'])
def get_all_opportunities(request):
    opportunities = Opportunity.objects.all()
    
    for opportunity in opportunities:
        # Calculate the number of accepted applications
        accepted_applications_count = Application.objects.filter(
            opportunity=opportunity, accepted='1'
        ).count()

        # Update the accepted_count field
        opportunity.accepted_count = accepted_applications_count

        # Save the Opportunity object
        opportunity.save()

    serializer = OpportunitySerializer(opportunities, many=True)
    
    return Response(serializer.data)

class ApplicantListCreateView(generics.ListCreateAPIView):
    
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
 
class ApplicantRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    def perform_update(self, serializer):

        # Check if the 'password' field is being updated
        if 'password' in serializer.validated_data:
            # Get the new password from the serializer data
            new_password = serializer.validated_data.get('password')

            # Encode the new password with a secret key using Django's make_password function
            encoded_password = make_password(new_password)

            # Replace the original password with the encoded password
            serializer.validated_data['password'] = encoded_password

        # Perform the update with the encoded password or without it
        serializer.save()

class OpportunityRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer

@api_view(['GET'])
def get_available_opportunities(request):
    current_date = datetime.now().date()
    available_opportunities = Opportunity.objects.filter(
        status='Open',
        due_date__gte=current_date
    )
    serializer = OpportunitySerializer(available_opportunities, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_opportunity_by_id(request, opportunity_id):
    try:
        opportunity = Opportunity.objects.get(pk=opportunity_id)
    except Opportunity.DoesNotExist:
        return Response({'error': 'Opportunity not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OpportunitySerializer(opportunity)

    return Response(serializer.data)

from rest_framework.exceptions import ValidationError

@api_view(['GET'])
def apply(request, applicant_id, opportunity_id):
    try:
        # Check if the application already exists for the same applicant and opportunity
        existing_application = Application.objects.filter(applicant=applicant_id, opportunity=opportunity_id).first()

        if existing_application:
            raise ValidationError("You have already submitted an application for this opportunity.")

        # Calculate the similarity score and submit the application
        similarity_score = submit_application(applicant_id, opportunity_id)

        if similarity_score is not None:
            return Response({'detail': 'Application submitted successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to submit the application.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except ValidationError as ve:
        return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def accept_application(request, application_id):
    if request.method == 'POST':
        try:
            application = Application.objects.get(id=application_id)

            # Create a new SortedApplication instance and copy relevant data
            sorted_application = SortApplication(
                applicant=application.applicant,
                opportunity=application.opportunity,
                score=application.score,
                accepted=1  # Set as accepted
            )
            
            sorted_application.save()  # Save the sorted application
            application.delete()  # Delete the original application

            send_emails() # Send acceptance emails

            return Response({'message': 'Application accepted successfully.'}, status=status.HTTP_200_OK)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['POST'])
def reject_application(request, application_id):
    if request.method == 'POST':
        try:
            application = Application.objects.get(id=application_id)

            # Create a new SortedApplication instance and copy relevant data
            sorted_application = SortApplication(
                applicant=application.applicant,
                opportunity=application.opportunity,
                score=application.score,
                accepted=2  # Set as rejected
            )

            sorted_application.save()  # Save the sorted application
            application.delete()  # Delete the original application

            return Response({'message': 'Application rejected successfully.'}, status=status.HTTP_200_OK)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_recent_applications(request):
    try:
        # Customize the queryset to retrieve recent applications as per your logic
        # For example, you can order by created_date to get the most recent applications and filter by accepted status
        recent_applications = Application.objects.filter(accepted=0).order_by('-created_date')[:10]

        application_data = []  # Create a list to hold the customized data
        for application in recent_applications:
            # Customize the data for each application
            application_data.append({
                'id': application.id,
                'applicantFullName': application.applicant.full_name,
                'score': application.score,
                'created_date': application.created_date,
            })

        return Response(application_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def submit_applicant(request,applicant_id):
    if request.method == 'POST':
        data = request.data
        print(data)
        # Handle the document data
        document_data = data.get('document', {})
        
        # Create a DocumentSerializer instance for document validation
        document_serializer = DocumentSerializer(data=document_data)

        if document_serializer.is_valid():
            print("valid document serializer")
            # Save the document and get the serialized data as a dictionary
            document = document_serializer.save()
            document_data = document_serializer.data
            download_directory = 'C:\\Users\\umoha\\Downloads\\'
            document_name = document_data.get('name')
            

            # Source file path in the "Downloads" directory
            downloads_dir = os.path.expanduser("~\Downloads")  # Get the path to the user's Downloads directory
            source_file = os.path.join(downloads_dir,document_name)  # Replace 'your_file.txt' with the actual file name

            # Destination file path
            destination_dir = 'C:\\Users\\umoha\\OneDrive\\Bureau\\pfe\\front kemel\\dashboard\\react-ui\\public'  # Replace with the desired destination directory
            destination_file = os.path.join(destination_dir, document_name)  # Replace 'new_file.txt' with the desired destination file name
            
            # Copy the file
            shutil.copy(source_file, destination_file)
        
            print(data)
             
            # Create an ApplicantSerializer instance for applicant validation
            applicant_serializer = ApplicantSerializer(data=data)
            
           
            if applicant_serializer.is_valid():
                print("valid applicant serializer"),
                
                # Save the applicant
                applicant=applicant_serializer.save()
               
                return Response(applicant, status=status.HTTP_201_CREATED)
            else:
                # Handle errors in the applicant data
                return Response(applicant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Handle errors in the document data
            return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def getApplicationById(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
        serializer = ApplicationSerializer(application)  # Use your Application serializer
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_all_applicants(request):
    if request.method == 'GET':
        all_applicants = Applicant.objects.all()
        serializer = ApplicantSerializer(all_applicants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_applicants_by_accepted(request):
    # Get the 'accepted' value from the query parameters (e.g., /applications/?accepted=1 or /applications/?accepted=2)
    accepted_value = request.query_params.get('accepted')
    if accepted_value is not None:
        # Ensure that the provided 'accepted' value is either '1' or '2'
        if accepted_value in ['1', '2']:
            
            # Filter sorted applications based on the provided 'accepted' value
            sorted_applications = SortApplication.objects.filter(accepted=accepted_value)

            # Retrieve the associated applicants from the sorted applications
            applicants = [sorted_applicant.applicant for sorted_applicant in sorted_applications]

            # Serialize the retrieved applicants using the appropriate serializer
            serializer = ApplicantSerializer(applicants, many=True)

            return Response(serializer.data, status=200)
        else:
            return Response({'error': 'Invalid accepted value'}, status=400)

    return Response({'error': 'Accepted value not provided'}, status=400)









class ApplicationListCreateView(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

class ApplicationRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


@api_view(['GET'])
def get_user_by_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
@api_view(['GET'])
def get_applicant_by_id(request, user_id):
        try:
            user = Applicant.objects.get(user_ptr_id=user_id)
            serializer = ApplicantSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#get_document_by_id
@api_view(['GET'])
def get_document_by_id(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    

class UserRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer




