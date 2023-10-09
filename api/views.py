from rest_framework.response import Response
from rest_framework.decorators import api_view
import docx2txt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Opportunity
from .serializers import OpportunitySerializer  # Assuming you have a serializer for the Opportunity model


@api_view(['GET'])
def getData(request):
    job_description = docx2txt.process('api\Salem_Kamoun_EN.docx')
    resume = docx2txt.process('api/resources/description.docx')
 
    content = [job_description, resume]
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(content)
    mat = cosine_similarity(count_matrix)
    result= str(mat[1][0]*100) + '%'
    output ={"res":result}
    return Response(result)


@api_view(['POST'])
def submit_opportunity(request):
    if request.method == 'POST':
        serializer = OpportunitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Opportunity submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
@api_view(['GET'])
def get_all_opportunities(request):
 
    opportunities = Opportunity.objects.all()

  
    serializer = OpportunitySerializer(opportunities, many=True)
 
    return Response(serializer.data)