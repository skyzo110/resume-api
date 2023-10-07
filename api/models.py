from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    applications = models.ManyToManyField('Opportunity', through='Application')

    def __str__(self):
        return self.full_name

class Opportunity(models.Model):
    date = models.DateField()
    job_description = models.TextField()

    def __str__(self):
        return f"Opportunity on {self.date}"

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.full_name} applied for {self.opportunity}"
