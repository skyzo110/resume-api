import base64
from inspect import Traceback
import pdb
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework import status
from django.http import Http404
from datetime import datetime
from rest_framework.permissions import AllowAny
from .models import Opportunity, Applicant, Application ,ApplicationStorage
from .serializers import DocumentSerializer, OpportunitySerializer, ApplicantSerializer, ApplicationSerializer, UserLoginSerializer, UserSignInSerializer
from .service import submit_application, user_login
from django.contrib.auth import authenticate, login

    
application_storage = ApplicationStorage()

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
def apply(request,applicant_id, opportunity_id):  
    try:
        response_data=submit_application(applicant_id,opportunity_id)
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def accept_application(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
        application.accepted = True
        application.save()
        
        # Update the accepted_count for the corresponding opportunity
        opportunity = application.opportunity
        opportunity.accepted_count += 1
        opportunity.save()
        
        return Response({'message': 'Application accepted successfully'}, status=status.HTTP_200_OK)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reject_application(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
        application.accepted = False
        application.save()

        # Implement additional logic if needed

        return Response({'message': 'Application rejected successfully'}, status=status.HTTP_200_OK)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_accepted_applications(request):
    accepted_applications = Application.objects.filter(accepted=True)
    accepted_applications_serialized = ApplicationSerializer(accepted_applications, many=True)

    return Response({'accepted_applications': accepted_applications_serialized.data}, status=status.HTTP_200_OK)

# Example view to retrieve rejected applications from the storage
@api_view(['GET'])
def get_rejected_applications(request):
    rejected_applications = Application.objects.filter(accepted=False)
    rejected_applications_serialized = ApplicationSerializer(rejected_applications, many=True)

    return Response({'rejected_applications': rejected_applications_serialized.data}, status=status.HTTP_200_OK)
@api_view(['GET'])
def get_recent_applications (request):
    recent_applications = Application.objects.filter(accepted=None)
    recent_applications_serialized = ApplicationSerializer(recent_applications, many=True)

    return Response({'recent_applications': recent_applications_serialized.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def submit_applicant(request):
        if request.method == 'POST':
            data = request.data

            # First, handle the document data
            document_data = data.get('document', {})
            document_serializer = DocumentSerializer(data=document_data)
            if document_serializer.is_valid():
                document = document_serializer.save()
                #convert from Document to dict
                document = document.__dict__
                pdb.set_trace()
                 
            else:
                return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
            # Next, handle the applicant data
            data['document'] = document 
            applicant_serializer = ApplicantSerializer(data=data)
            
            
            if applicant_serializer.is_valid(): 
                pdb.set_trace()
                applicant_serializer.save()
               
                 
                return Response(applicant_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(applicant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Login the user
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Login failed'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_signin(request):
    serializer = UserSignInSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # Check if the user already exists
        user, created = Applicant.objects.get_or_create(email=email)

        # Set the password for the user
        applicant.set_password(password)
        applicant.save()

        # Authenticate and log in the user
        applicant = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return Response({'message': 'Sign-in successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Sign-in failed'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)