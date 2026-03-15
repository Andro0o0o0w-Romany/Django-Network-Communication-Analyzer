from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('', views.analysis_list, name='analysis_list'),
    path('run/<int:topology_pk>/', views.run_analysis, name='run_analysis'),
    path('results/<int:pk>/', views.analysis_detail, name='analysis_detail'),
    path('results/<int:pk>/delete/', views.analysis_delete, name='analysis_delete'),
]
