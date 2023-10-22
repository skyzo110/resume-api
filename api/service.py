import PyPDF2
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.views.decorators.csrf import csrf_exempt
from sklearn.metrics.pairwise import cosine_similarity
from .models import Applicant, Application, Opportunity
from .serializers import ApplicationSerializer, UserSerializer
import nltk
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.auth import authenticate

nltk.download('stopwords')
nltk.download('punkt')



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
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    similarity_score = cosine_sim[1][0]  # The similarity score between text2 and text1
    return similarity_score

def submit_application(applicant_id, opportunity_id):
    print(applicant_id)
    try:
        # Retrieve the Applicant instance based on the provided ID
        applicant = Applicant.objects.get(pk=applicant_id)

        # Access the uploaded PDF file from the selected_file field
        resume_pdf = applicant.selected_file

        # Use PyPDF2 to read text content from the PDF file
        pdf_reader = PyPDF2.PdfReader(resume_pdf.path)
        resume = ""
        for page in pdf_reader.pages:
            resume += page.extract_text()

        # Retrieve the Opportunity instance based on the provided ID
        opportunity = Opportunity.objects.get(pk=opportunity_id)

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
    except:
        print("exception occured ")

def user_login(username, password):
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_applicant:
            return "applicant"
        elif user.is_hr:
            return "hr"
    else:
        # Handle invalid login
        return "invalid"  # You can return an error message or code


             

    


       