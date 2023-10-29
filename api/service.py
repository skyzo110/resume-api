import pdb
from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.views.decorators.csrf import csrf_exempt
from sklearn.metrics.pairwise import cosine_similarity
from .models import Application, Opportunity, Applicant,User
from .serializers import ApplicationSerializer, UserSerializer
import nltk
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.auth import authenticate
import base64
import io
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail

nltk.download('stopwords')
nltk.download('punkt')








def calculate_and_assign_score(application):
    applicant = application.applicant
    opportunity = application.opportunity
    pdb.set_trace()
    # Retrieve and preprocess the resume and job description
    pdf_data = applicant.document.base64_data
    resume = preprocess_resume(applicant.document.b64decode(pdf_data))
    job_description = preprocess_job_description(opportunity.requirements)

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
  
  # Function to calculate cosine similarity
def calculate_cosine_similarity(text1, text2):
    print("Text 1:", text1)
    print("Text 2:", text2)

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_matrix)
    similarity_score = cosine_sim[0][1]  # Get the similarity score

    print("Similarity Score:", similarity_score)

    return similarity_score



@transaction.atomic  # Use atomic transaction for database operations
def submit_application(applicant_id, opportunity_id):
    try:
        # Retrieve the Applicant instance based on the provided ID
        applicant = Applicant.objects.get(pk=applicant_id)

        # Access the uploaded PDF file from the base64 data
        pdf_data = applicant.document.base64_data

        # Decode the base64 data to obtain the PDF content
        resume_pdf = base64.b64decode(pdf_data)

        # Use PyPDF2's PdfReader to read text content from the decoded PDF data
        pdf_reader = PdfReader(io.BytesIO(resume_pdf))
        resume = ""
        for page in pdf_reader.pages:
            resume += page.extract_text()

        # Retrieve the Opportunity instance based on the provided ID
        opportunity = Opportunity.objects.get(pk=opportunity_id)

        # Access the job description from the Opportunity model
        job_description = opportunity.requirements

        # Preprocess the resume and job description
        preprocessed_resume = preprocess_resume(resume)
        preprocessed_job_description = preprocess_job_description(job_description)

        # Calculate cosine similarity
        similarity_score = calculate_cosine_similarity(preprocessed_resume, preprocessed_job_description)

        # Create a new Application instance with the similarity score as a numeric value
        application = Application(
            applicant=applicant,
            opportunity=opportunity,
            score=similarity_score  # Ensure that it's a numeric value
        )
        application.save()  # Save the application

        print("Application submitted successfully.")
        return similarity_score  # Return the similarity score

    except Exception as e:
        print("Exception occurred:", str(e))
        return None  # Return None in case of an exception



def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def send_emails( ):
        subject = 'Hello, World'
        message = 'This is the message body.'
        from_email = 'gundiamohamed@gmail.com'
        recipient_list = ['recipient1@yopmail.com']

        send_mail(subject, message, from_email, recipient_list)
 


