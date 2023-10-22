from django.db import models


class User(models.Model):
    class Meta:
        app_label = 'api'
        db_table = "users"
    
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=255, default="*******")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class Document(models.Model):
    class Meta:
        app_label = 'api'
    id = models.AutoField(primary_key=True)    
    base64_data = models.CharField(max_length=10000)
class Applicant(User):
 
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)  # Allowing for non-numeric characters
    linkedin_profile = models.URLField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)  # Allowing for non-numeric characters
    document = models.OneToOneField(Document, on_delete=models.CASCADE)

    active = models.BooleanField(default=True)   
    user_ptr = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        parent_link=True,
        
    )
    active = True

    
class HR(User):
  
    user_ptr = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        parent_link=True,
    )
   


class Opportunity(models.Model):
    class Meta:
        app_label = 'api'
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    select_value = models.IntegerField(default=0)  # Change to IntegerField
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    requirements = models.TextField()
    benefits = models.TextField()
    due_date = models.DateField()
    accepted_count = models.PositiveIntegerField(default=0 ,editable=False)

    @property
    def current_status(self):
        if self.accepted_count == self.select_value:  # Change to Integer comparison
            return "Closed"
        else:
            return "Open"

    def save(self, *args, **kwargs):
        # Calculate the accepted count before saving
        accepted_applications_count = Application.objects.filter(
            opportunity=self, accepted=True  # Change to Boolean
        ).count()
        self.accepted_count = accepted_applications_count

        super(Opportunity, self).save(*args, **kwargs)

    def __str__(self):
        return self.title








class Application(models.Model):
    score = models.CharField(max_length=255, blank=True, editable=False)  # Mark the 'score' field as not editable

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications_as_applicant')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications_as_opportunity')
    accepted = models.BooleanField(default=None)
    #created date

    def save(self, *args, **kwargs):
        if not self.score:
            # Calculate the score only if it's not already set
            # You need to insert your cosine similarity calculation here
            cosine_similarity_result = 0  # Calculate the cosine similarity result

            # Update the score field with the calculated result
            self.score = str(cosine_similarity_result * 100) + '%'

        super(Application, self).save(*args, **kwargs)

    def __str__(self):
        return f"Application for {self.opportunity} by {self.applicant} scoring {self.score}"


class ApplicationStorage:
    def accept_application(self, application_id):
        """Method to accept an application and store it."""
        try:
            application = Application.objects.get(id=application_id)
            application.accepted = True
            application.save()
        except Application.DoesNotExist:
            return False
        return True

    def reject_application(self, application_id):
        """Method to reject an application and store it."""
        try:
            application = Application.objects.get(id=application_id)
            application.accepted = False
            application.save()
        except Application.DoesNotExist:
            return False
        return True

    def get_accepted_applications(self):
        """Method to retrieve the list of accepted applications."""
        return Application.objects.filter(accepted=True)

    def get_rejected_applications(self):
        """Method to retrieve the list of rejected applications."""
        return Application.objects.filter(accepted=False)
    def get_recent_applications(self):
        """Method to retrieve the list of new applications."""
        return Application.objects.filter(accepted=None)

