from django.db import models


class User(models.Model):
    class Meta:
        app_label = 'api'
        db_table = "users"
    
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Applicant(User):
    phone_number = models.CharField(max_length=255)
    linkedin_profile = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    agree_to_terms = models.BooleanField(default=False)
    selected_file = models.FileField(null=True, blank=True)
    user_ptr = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        parent_link=True,
        default=1  # Specify your default value
    )

    applications = models.ManyToManyField('Opportunity', through='Application', related_name='candidates')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
   

class Opportunity(models.Model):
    class Meta:
        app_label = 'api'
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    select_value = models.CharField(max_length=10)
    description = models.TextField()
    due_date = models.DateField()  # Add the due_date field with a DateField
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically generated creation date
    
    applications = models.ManyToManyField('Applicant', through='Application', related_name='opportunities')
    def __str__(self):
        return self.title




class Application(models.Model):
    score = models.CharField(max_length=255, blank=True, editable=False)  # Mark the 'score' field as not editable

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications_as_applicant')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications_as_opportunity')

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


