from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('network:dashboard'), name='home'),
    path('networks/', include('network.urls', namespace='network')),
    path('analysis/', include('analysis.urls', namespace='analysis')),
    path('rules/', include('rules.urls', namespace='rules')),
]
