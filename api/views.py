import base64
from django.shortcuts import render
from inspect import Traceback
import pdb
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework import status
from django.http import Http404
from datetime import datetime
from rest_framework.permissions import AllowAny
from .models import Opportunity, Applicant, Application, SortApplication
from .serializers import DocumentSerializer, OpportunitySerializer, ApplicantSerializer, ApplicationSerializer, UserLoginSerializer, UserSignInSerializer
from .service import submit_application, user_login
from django.contrib.auth import authenticate, login
from datetime import date
from django.http import HttpResponse
from .forms import AuthenticationForm
from django.contrib.auth.views import LoginView

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

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html' 

# @login_required
# def applicant_view(request):
#     if request.user.is_authenticated:
#         # User is logged in, so you can access user-related information
#         email = request.user.email

#         # Your view logic here, for example, render a template
#         return render(request, 'http://127.0.0.1:3000/auth/signin-2', {
#             'email': email,
            
#         })
#     else:
#         # User is not logged in, handle it accordingly
#         return HttpResponse("Please log in to access this page.")
# def is_hr(user):
#     return user.is_authenticated and user.is_hr  # Define your custom test logic

# @user_passes_test(is_hr)
# def hr_view(request):
#     # Ensure the user is an HR user (authenticated and is_hr is True)
#     if request.user.is_authenticated and request.user.is_hr:
#         # HR-specific view logic here
#         hr_email = request.user.email  
#         return render(request, 'hr_template.html', {'hr_name': hr_email})
#     else:
#         return HttpResponse("You don't have permission to access this page.")
    
# def sign_in(request):
#      if request.method == 'POST':
#          form = AuthenticationForm(request, request.POST)
#          if form.is_valid():
#              # Authenticate the user
#              email = form.cleaned_data['username']
#              password = form.cleaned_data['password']
#              user = authenticate(request, username=email, password=password)
#              if user is not None:
#                  # Log the user in
#                  login(request, user)
#                  return redirect('profile')  # Redirect to the user's profile or another page
#      else:
#          form = AuthenticationForm()
#      return render(request, 'sign_in.html', {'form': form})    