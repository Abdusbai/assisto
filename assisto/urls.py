from django.urls import path
from django.shortcuts import redirect
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home-page"),
    path("assisto", views.index, name="assisto"),
    path("assisto/ar", views.index_ar, name="assisto_ar"),
    path("assisto/attestation/download/<str:cn>/<str:pr>", views.attestation, name="attestation"),
    path("getResponse", views.getResponse, name="getResponse"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="Logout"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("dashboard/particulier", views.particulier, name="particulier"),
    path("dashboard/particulier/<str:cin>", views.particulier_details, name="particulier_details"),
    path("dashboard/demandes/particulier", views.particulier_demande, name="particulier_demande"),
    path("dashboard/demandes/particulier/details/<str:cin>", views.particulier_demande_details, name="particulier_demande_details"),
    path("dashboard/demandes/<str:pr>/details/<str:cn>/<str:st>", views.accepter_refuser_demande, name="accepter_refuser_demande"),
    path("dashboard/societe", views.societe, name="societe"),
    path("dashboard/societe/<str:rc_num>", views.societe_details, name="societe_details"),
    path("dashboard/demandes/societe", views.societe_demande, name="societe_demande"),
    path("dashboard/demandes/societe/details/<str:rc_num>", views.societe_demande_details, name="societe_demande_details"),
    path("dashboard/cooperative", views.cooperative, name="cooperative"),
    path("dashboard/cooperative/<str:cnc_num>", views.cooperative_details, name="cooperative_details"),
    path("dashboard/demandes/cooperative", views.cooperative_demande, name="cooperative_demande"),
    path("dashboard/demandes/cooperative/details/<str:cnc>", views.cooperative_demande_details, name="cooperative_demande_details"),
    
]
