from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

 

urlpatterns=[
    path('api/apply/<int:applicant_id>/<int:opportunity_id>/', views.apply, name='apply'),
    path('submit-opportunity', views.submit_opportunity, name='submit_opportunity'),
    path('opportunities', views.get_all_opportunities, name='get_all_opportunities'),
    path('submit_applicant', views.submit_applicant, name='submit_user'),
    path('applicants', views.get_all_applicants, name='get_all_users'),
    path('api/applications/', views.ApplicationListCreateView.as_view(), name='application-list-create'),
    path('api/applications/<int:pk>/', views.ApplicationRetrieveUpdateDeleteView.as_view(), name='application-retrieve-update-delete'),
    path('opportunities/<int:opportunity_id>/', views.get_opportunity_by_id, name='get_opportunity_by_id'),
    path('available-opportunities/', views.get_available_opportunities, name='available_opportunities'),
    path('api/application/<int:application_id>/', views.getApplicationById, name='get_application_by_id'),
    path('accept-application/<int:application_id>/', views.accept_application, name='accept-application'),
    path('reject-application/<int:application_id>/', views.reject_application, name='reject-application'),
    path('get-recent-applications/', views.get_recent_applications, name='get_recent_applications'),
    path('api/login', views.login , name='custom_login'),
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/generate/', views.GenerateToken.as_view(), name='generate_token'),
    path('api/register/', views.RegistrationView.as_view(), name='user-registration'),
    path('users/', views.user_list, name='user-list'),

]


  

