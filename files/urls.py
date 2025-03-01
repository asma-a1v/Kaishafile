from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('download/', views.download_view, name='download'),
    path('upload/', views.upload_view, name='upload'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/files/', views.get_files_list, name='get_files_list'),
    path('api/logs/', views.get_logs, name='get_logs'),
    path('master/', views.master_view, name='master'),
] 