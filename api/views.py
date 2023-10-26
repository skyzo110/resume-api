import base64
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
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import Http404
from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny
from .models import Opportunity, Applicant, Application, SortApplication, User
from .serializers import DocumentSerializer, OpportunitySerializer, ApplicantSerializer, ApplicationSerializer ,UserSerializer 
from .service import submit_application, authenticate_user
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.admin import UserAdmin
from datetime import date
from django.http import HttpResponseRedirect
from .forms import CustomUserAdminForm
from django.contrib.auth.views import LoginView
import jwt
from django.conf import settings



def user_list(request):
    users = User.objects.all()  # Query the users from your model
    context = {'users': users}
    return render(request, 'user_list.html', context)

User = get_user_model()
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserAdminForm

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            # Create a new user with the submitted data
            form = self.add_form(request.POST)
            if form.is_valid():
                user = form.save()
                self.message_user(request, "User created successfully")
                return HttpResponseRedirect(reverse('admin:yourapp_customuser_changelist'))
        else:
            form = self.add_form()

        return super(CustomUserAdmin, self).add_view(request, form_url, extra_context)



@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        data = request.data
        email = data.get("email")
        password = data.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            # Authentication successful, Django SimpleJWT handles token generation
            if user.is_superuser:
                return Response({'message': 'HR logged in successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User logged in successfully'}, status=status.HTTP_201_CREATED)
        else:
            # Authentication failed
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            # Include the user_id in the response
            response.data['user_id'] = request.user.id
        return response


class GenerateToken(APIView):
    def post(self, request):
        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
        return Response({'access_token': access_token})


class RegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            is_superuser = request.data.get("is_superuser", False)  # Set to True if user should be a superuser
            user = serializer.save(is_staff=is_superuser, is_superuser=is_superuser)

            if is_superuser:
                return Response({'message': 'HR registered successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
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
            applicant = Applicant.objects.get(pk=applicant_id)
            opportunity = Opportunity.objects.get(pk=opportunity_id)

            # Format the similarity score as a percentage with two decimal places
            formatted_score = round(similarity_score, 2)

            application = Application(
                applicant=applicant,
                opportunity=opportunity,
                score=formatted_score
            )
            application.save()

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
                accepted=True  # Set as accepted
            )

            sorted_application.save()  # Save the sorted application
            application.delete()  # Delete the original application

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
                accepted=False  # Set as rejected
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
        # For example, you can order by created_date to get the most recent applications
        recent_applications = Application.objects.order_by('-created_date')[:10]  # Get the top 10 most recent applications

        serializer = ApplicationSerializer(recent_applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def submit_applicant(request):
    if request.method == 'POST':
        data = request.data

        # Handle the document data
        document_data = data.get('document', {})

        # Create a DocumentSerializer instance for document validation
        document_serializer = DocumentSerializer(data=document_data)

        if document_serializer.is_valid():
            # Save the document and get the serialized data as a dictionary
            document = document_serializer.save()
            document_data = document_serializer.data

            # Update the data with the document ID
            data['document'] = document.id

            # Create an ApplicantSerializer instance for applicant validation
            applicant_serializer = ApplicantSerializer(data=data)

            if applicant_serializer.is_valid():
                # Save the applicant
                applicant_serializer.save()
                return Response(applicant_serializer.data, status=status.HTTP_201_CREATED)
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

class ApplicationListCreateView(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

class ApplicationRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer





