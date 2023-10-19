from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import Opportunity, Applicant, Application
from .serializers import OpportunitySerializer, ApplicantSerializer, ApplicationSerializer, CosineSimilaritySerializer
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


nltk.download('stopwords')
nltk.download('punkt')



# @api_view(['GET'])
# def cosine_similarity_view(request, applicant_id, opportunity_id):
#     try:
#         # Retrieve the Applicant instance based on the provided ID
#         applicant = Applicant.objects.get(pk=applicant_id)

#         # Access the uploaded PDF file from the selected_file field
#         resume_pdf = applicant.selected_file

#         # Use PyPDF2 to read text content from the PDF file
#         pdf_reader = PyPDF2.PdfReader(resume_pdf.path)
#         resume = ""
#         for page in pdf_reader.pages:
#             resume += page.extract_text()

#         # Retrieve the Opportunity instance based on the provided ID
#         opportunity = Opportunity.objects.get(pk=opportunity_id)

#         # Access the job description from the Opportunity model
#         job_description = opportunity.description

#         # Preprocess text data
#         stop_words = set(stopwords.words('english'))
#         job_description = ' '.join([word.lower() for word in word_tokenize(job_description) if word.isalnum() and word.lower() not in stop_words])
#         resume = ' '.join([word.lower() for word in word_tokenize(resume) if word.isalnum() and word.lower() not in stop_words])

#         # Calculate cosine similarity
#         tfidf_vectorizer = TfidfVectorizer()
#         tfidf_matrix = tfidf_vectorizer.fit_transform([job_description, resume])
#         cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

#         # Calculate the cosine similarity score
#         similarity_score = cosine_sim[1][0]

#         # Create and save a new Application instance without specifying the score
#         application = Application(
#             applicant=applicant,
#             opportunity=opportunity
#         )
#         application.save()  # This will trigger the score calculation in the Application model's save method

#         # Include the score in the response
#         response_data = {'similarity_percentage': similarity_score * 100, 'score': application.score}
#         serializer = CosineSimilaritySerializer(data=response_data)
#         if serializer.is_valid():
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     except (Applicant.DoesNotExist, Opportunity.DoesNotExist):
#         return Response({'error': 'Applicant or Opportunity not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





    

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

@api_view(['POST'])
def submit_application(request):
    if request.method == 'POST':
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # The application is already saved, so you don't need to save it again here

            # Calculate and assign the similarity score
            application = serializer.instance  # Get the newly created application
            applicant = application.applicant
            opportunity = application.opportunity

            # Calculate cosine similarity (you may want to include the preprocessing steps here)
            similarity_score = calculate_cosine_similarity(applicant.resume, opportunity.description)

            # Set the similarity score to the application
            application.score = similarity_score
            
            # Save the updated application with the new score
            application.save()

            return Response({'message': 'Application submitted successfully with similarity score'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



def calculate_and_assign_score(application):
    applicant = application.applicant
    opportunity = application.opportunity

    # Retrieve and preprocess the resume and job description
    resume = preprocess_resume(applicant.selected_file)
    job_description = preprocess_job_description(opportunity.description)

    # Calculate cosine similarity
    similarity_score = calculate_cosine_similarity(resume, job_description)

    # Assign the score to the application and save it
    application.score = similarity_score
    application.save()

# Function to preprocess resume text
def preprocess_resume(resume_text):
    # Lowercase the text
    resume_text = resume_text.lower()

    # Tokenize the text
    tokens = word_tokenize(resume_text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Join the filtered tokens back into a string
    preprocessed_text = ' '.join(filtered_tokens)

    return preprocessed_text

# Function to preprocess job description text
def preprocess_job_description(job_description_text):
    # Lowercase the text
    job_description_text = job_description_text.lower()

    # Tokenize the text
    tokens = word_tokenize(job_description_text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Join the filtered tokens back into a string
    preprocessed_text = ' '.join(filtered_tokens)

    return preprocessed_text


# Function to calculate cosine similarity
def calculate_cosine_similarity(text1, text2):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    similarity_score = cosine_sim[1][0]  # The similarity score between text2 and text1
    return similarity_score


@api_view(['GET'])
def cosine_similarity_view(request, applicant_id, opportunity_id):
    try:
        # Retrieve the Applicant instance based on the provided ID
        applicant = Applicant.objects.get(pk1=applicant_id)

        # Access the uploaded PDF file from the selected_file field
        resume_pdf = applicant.selected_file

        # Use PyPDF2 to read text content from the PDF file
        pdf_reader = PyPDF2.PdfReader(resume_pdf.path)
        resume = ""
        for page in pdf_reader.pages:
            resume += page.extract_text()

        # Retrieve the Opportunity instance based on the provided ID
        opportunity = Opportunity.objects.get(pk2=opportunity_id)

        # Access the job description from the Opportunity model
        job_description = opportunity.description

        # Preprocess the resume and job description
        preprocessed_resume = preprocess_resume(resume)
        preprocessed_job_description = preprocess_job_description(job_description)

        # Calculate cosine similarity
        similarity_score = calculate_cosine_similarity(preprocessed_resume, preprocessed_job_description)

        # Create and save a new Application instance without specifying the score
        application = Application(
            applicant=applicant,
            opportunity=opportunity
        )

        # Set the similarity score
        application.score = similarity_score * 100

        # Save the application
        application.save()

        # Include the score in the response
        response_data = {'similarity_percentage': similarity_score * 100}
        
        return Response(response_data, status=status.HTTP_200_OK)

    except (Applicant.DoesNotExist, Opportunity.DoesNotExist):
        return Response({'error': 'Applicant or Opportunity not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    




@api_view(['POST'])
def submit_applicant(request):
    if request.method == 'POST':
        serializer = ApplicantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Applicant submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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