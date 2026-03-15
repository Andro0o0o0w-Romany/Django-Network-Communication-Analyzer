from django.urls import path
from . import views

app_name = 'rules'

urlpatterns = [
    path('', views.ruleset_list, name='ruleset_list'),
    path('create/', views.ruleset_create, name='ruleset_create'),
    path('<int:pk>/', views.ruleset_detail, name='ruleset_detail'),
    path('<int:pk>/edit/', views.ruleset_edit, name='ruleset_edit'),
    path('<int:pk>/delete/', views.ruleset_delete, name='ruleset_delete'),

    # Rules within rulesets
    path('<int:ruleset_pk>/rules/create/', views.rule_create, name='rule_create'),
    path('rules/<int:pk>/edit/', views.rule_edit, name='rule_edit'),
    path('rules/<int:pk>/delete/', views.rule_delete, name='rule_delete'),
    path('rules/<int:pk>/toggle/', views.rule_toggle, name='rule_toggle'),
]
