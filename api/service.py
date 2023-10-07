import docx2txt
from .models import Application
from .serializers import ApplicationSerializer

def checkExistance(userId, opportunityId, file):
    # Check if an application with the given user, opportunity, and file exists
    exists = Application.objects.filter(
        user_id=userId,
        opportunity_id=opportunityId,
        resume=file
    ).exists()
    
    return exists
def apply(request):

  user = request.user  # Assuming you're using DRF's authentication system
  serializer = ApplicationSerializer(data=request.data)

  if serializer.is_valid():
        # Check if the user has already applied to this opportunity with the same file
        user_id = user.id
        opportunity_id = serializer.validated_data['opportunity'].id
        resume = serializer.validated_data['resume']

        if checkExistance(user_id=user_id, opportunity_id=opportunity_id, resume=resume) :
            return  {'detail': 'You have already applied to this opportunity with the same file.'} 

        # Create a new application
        serializer.save(user=user)
        return  {'detail': 'Application submitted successfully.'}  