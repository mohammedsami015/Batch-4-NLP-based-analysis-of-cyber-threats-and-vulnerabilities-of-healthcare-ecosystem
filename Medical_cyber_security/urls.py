from django.contrib import admin
from django.urls import path
from Medical.views import (
    login_view, signup_view, logout_view,
    upload_test_dataset_view, predict_view,home_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),

    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),

    path('upload_test_dataset/', upload_test_dataset_view, name='upload_test_dataset'),
    path('predict/', predict_view, name='predict'),
]