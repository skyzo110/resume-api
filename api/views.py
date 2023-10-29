import base64
import shutil
import os
from django.forms import ValidationError
from django.shortcuts import render
from inspect import Traceback
import pdb
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
        if user.id==1:
            user.is_superuser = True
            

        if user is not None:
            # Generate a token for the authenticated user
            token = generate_token(user)

            if user.is_superuser:
                return Response({'message': 'HR logged in successfully', 'token': token,"id":user.id,"is_superusr":user.is_superuser}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'User logged in successfully', 'token': token,"id":user.id,"is_superusr":user.is_superuser}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

       # 




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

            # Generate a token for the registered user
            token = generate_token(user)

            # Include the token in the response
            return Response({'message': message, 'access_token': token,"id":user.id }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

@api_view(['GET'])
def apply(request, applicant_id, opportunity_id):  
    try:
        similarity_score = submit_application(applicant_id, opportunity_id)

        if similarity_score is not None:
            # Create and save a new Application instance with the similarity score as a numeric value
            # applicant = Applicant.objects.get(pk=applicant_id)
            # opportunity = Opportunity.objects.get(pk=opportunity_id)

            # Format the similarity score as a percentage with two decimal places
            # formatted_score = round(similarity_score, 2)

            # application = Application(
            #     applicant=applicant,
            #     opportunity=opportunity,
            #     score=formatted_score
            # )
            #application.save()

            return Response({'detail': 'Application submitted successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to submit the application.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        serializer = ApplicationSerializer(recent_applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            pdb.set_trace()

            # Source file path in the "Downloads" directory
            downloads_dir = os.path.expanduser("~\Downloads")  # Get the path to the user's Downloads directory
            source_file = os.path.join(downloads_dir,document_name)  # Replace 'your_file.txt' with the actual file name

            # Destination file path
            destination_dir = 'C:\\Users\\umoha\\OneDrive\\Bureau\\pfe\\front kemel\\dashboard\\react-ui\\public'  # Replace with the desired destination directory
            destination_file = os.path.join(destination_dir, document_name)  # Replace 'new_file.txt' with the desired destination file name
            pdb.set_trace() 
            # Copy the file
            shutil.copy(source_file, destination_file)
        
            print(data)
             
            # Create an ApplicantSerializer instance for applicant validation
            applicant_serializer = ApplicantSerializer(data=data)
            
           
            if applicant_serializer.is_valid():
                print("valid applicant serializer"),
                pdb.set_trace()
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
def get_sorted_applicants(request, filter):
    if filter not in ('0', '1', '2'):
        return Response({'error': 'Invalid filter value. Use 0 or 1 or 2.'}, status=status.HTTP_400_BAD_REQUEST)

    all_applicants = SortApplication.applicant.filter(accepted=filter)

    if not all_applicants:
        return Response(None, status=status.HTTP_204_NO_CONTENT)  # Return None with a 204 No Content status
    else:
        serializer = ApplicationSerializer(all_applicants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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




