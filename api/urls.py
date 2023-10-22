from . import views
from django.urls import path


 

urlpatterns=[
    path('api/cosine_similarity/<int:applicant_id>/<int:opportunity_id>/', views.apply, name='apply'),
    path('submit-opportunity', views.submit_opportunity, name='submit_opportunity'),
    path('opportunities', views.get_all_opportunities, name='get_all_opportunities'),
    path('submit_applicant', views.submit_applicant, name='submit_user'),
    path('applicants', views.get_all_applicants, name='get_all_users'),
    path('api/applications/', views.ApplicationListCreateView.as_view(), name='application-list-create'),
    path('api/applications/<int:pk>/', views.ApplicationRetrieveUpdateDeleteView.as_view(), name='application-retrieve-update-delete'),
    path('accept-application/<int:application_id>/', views.accept_application, name='accept_application'),
    path('reject-application/<int:application_id>/', views.reject_application, name='reject_application'),  
    path('get-accepted-applications/', views.get_accepted_applications, name='get_accepted_applications'),  
    path('get-rejected-applications/', views.get_rejected_applications, name='get_rejected_applications'),
    path('get-recent-applications/', views.get_recent_applications, name='get_recent_applications'), 
    path('api/login/', views.custom_login , name='custom_login'),
]
  

