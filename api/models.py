from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.contrib.auth import get_user_model
from .managers import CustomUserManager



class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        app_label = 'api'
    id = models.AutoField(primary_key=True)
    username = models.CharField( unique=True)
    email = models.EmailField( unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    
    

class Document(models.Model):
    class Meta:
        app_label = 'api'
    name = models.CharField( blank=True)

    id = models.AutoField(primary_key=True)    
    base64_data = models.CharField()


class Applicant(User):
    class Meta:
        app_label = 'api'
    #user = models.OneToOneField(User, on_delete=models.CASCADE )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)  
    linkedin_profile = models.URLField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)  
    document = models.OneToOneField(Document, on_delete=models.CASCADE, blank=True, null=True)
    

    
     
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
     
    
class HR(User):
   class Meta:
        app_label = 'api'
   #user = models.OneToOneField(User, on_delete=models.CASCADE)
   user_ptr = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True)


class Opportunity(models.Model):
    class Meta:
        app_label = 'api'
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    select_value = models.PositiveIntegerField(default=0)  # Use PositiveIntegerField
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    requirements = models.TextField()
    benefits = models.TextField()
    due_date = models.DateField()
    accepted_count = models.PositiveIntegerField(default=0, editable=False)
    status = models.CharField(max_length=10, default='Open', editable=False)

    def save(self, *args, **kwargs):
        # Calculate the accepted count before saving
        accepted_applications_count = SortApplication.objects.filter(
            opportunity=self, accepted=True
        ).count()
        self.accepted_count = accepted_applications_count

        super(Opportunity, self).save(*args, **kwargs)
    @property
    def current_status(self):
        if self.accepted_count == self.select_value:
            return "Closed"
        else:
            return "Open"

    

    def __str__(self):
        return self.title








class Application(models.Model):
    score = models.FloatField(null=True, blank=True, editable=False)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications_as_applicant')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications_as_opportunity')
    created_date = models.DateTimeField(auto_now_add=True, editable=False)  # Used auto_now_add to set the created_date
    accepted = models.PositiveIntegerField(default=0, editable=False)  # Use PositiveIntegerField
    def save(self, *args, **kwargs):
        if self.score is None:
            # Calculate the cosine similarity here and assign it to the score field
            cosine_similarity_result = self.calculate_cosine_similarity()

            # Update the score field with the calculated result as a numeric value
            self.score = cosine_similarity_result

        super(Application, self).save(*args, **kwargs)


    def calculate_cosine_similarity(self):
        # Perform your cosine similarity calculation here
        # You need to define how you're calculating the similarity between the applicant and opportunity
        # Replace the following line with your actual calculation
        cosine_similarity_result = "none"  

        return cosine_similarity_result

    def get_formatted_score(self):
        return f'{self.score:.2%}'  # Format the score as a percentage with two decimal places

    def __str__(self):
        return f"Application for {self.opportunity} by {self.applicant} scoring {self.get_formatted_score()}"
    
class SortApplication(Application):
   application_ptr = models.OneToOneField(Application, on_delete=models.CASCADE, parent_link=True)   


