from django.urls import path
from . import views

urlpatterns=[
    path('',views.getData),
    path('submit-opportunity', views.submit_opportunity, name='submit_opportunity'),
      path('opportunities', views.get_all_opportunities, name='get_all_opportunities'),

]