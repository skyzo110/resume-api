from django.db import models

class User(models.Model):
    class Meta:
        app_label = 'api'
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    applications = models.ManyToManyField('Opportunity', through='Application')

    def __str__(self):
        return self.full_name

class Opportunity(models.Model):
    class Meta:
        app_label = 'api'
    title = models.CharField(max_length=255)
    select_value = models.CharField(max_length=10)
    description = models.TextField()
    due_date = models.DateField()  # Add the due_date field with a DateField
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically generated creation date

    def __str__(self):
        return self.title

class Application(models.Model):
    class Meta:
        app_label = 'api'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.full_name} applied for {self.opportunity}"
 