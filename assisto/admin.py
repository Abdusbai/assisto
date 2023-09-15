from django.contrib import admin
from .models import Acc_User, Demandes, Societe, Particulier, Users, ProofDesc, Cooperative
from django.urls import reverse
from django.utils.html import format_html


class JustificationAdmin(admin.ModelAdmin):
    list_display = ("user_proof", "num_tf", "num_refe", "nom", "p_date", "nom_prenom_president", "duree", "tele", "email", "commune",)
    search_fields = ("user__cin_num", "user__cnc_num", "user__rc_num")
    exclude = ("pdf_name",)


class CooperativeAdmin(admin.ModelAdmin):
    list_display = ("cnc_num", "nom_president", "tele", "commune",)
    search_fields = ("cnc_num__cnc_num__icontains", "nom_president")

    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ["cnc_num"]
        else:  # Creating a new object
            return []
    
    def tele(self, obj):
        return obj.cnc_num.user_tel if obj.cnc_num else ""
    tele.short_description = "Téléphone"
    
    def province(self, obj):
        return obj.cnc_num.province if obj.cnc_num else ""
    province.short_description = "Province"
    
    def commune(self, obj):
        return obj.cnc_num.commune if obj.cnc_num else ""
    commune.short_description = "Commune"


class SocieteAdmin(admin.ModelAdmin):
    list_display = ("rc_num", "nom", "nom_gerant", "tele", "commune",)
    search_fields = ("rc_num__rc_num__icontains", "nom",)
    exclude = ("rc_pdf",)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ["rc_num"]
        else:  # Creating a new object
            return []
    
    def nom(self, obj):
        return obj.rc_num.user_nom if obj.rc_num else ""
    nom.short_description = "Nom"
    
    def tele(self, obj):
        return obj.rc_num.user_tel if obj.rc_num else ""
    tele.short_description = "Téléphone"
    
    def province(self, obj):
        return obj.rc_num.province if obj.rc_num else ""
    province.short_description = "Province"
    
    def commune(self, obj):
        return obj.rc_num.commune if obj.rc_num else ""
    commune.short_description = "Commune"
    

class ParticulierAdmin(admin.ModelAdmin):
    list_display = ("cin_num", "nom", "prenom", "date_naissance", "tele", "province", "adresse")
    search_fields = ("cin_num__cin_num__icontains",)
    exclude = ("cin_pdf",)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ["cin_num"]
        else:  # Creating a new object
            return []
    
    def nom(self, obj):
        return obj.cin_num.user_nom if obj.cin_num else ""
    nom.short_description = "Nom"

    def tele(self, obj):
        return obj.cin_num.user_tel if obj.cin_num else ""
    tele.short_description = "Téléphone"

    def email(self, obj):
        return obj.cin_num.user_email if obj.cin_num else ""
    email.short_description = "E-mail"

    def province(self, obj):
        return obj.cin_num.province if obj.cin_num else ""
    province.short_description = "Province"


class UserAdmin(admin.ModelAdmin):
    list_display = ("email_address", "first_name", "last_name",  "created_on", "last_login", "is_active")
    list_display_links = ["email_address"]
    list_filter = ("created_on", "last_login", "is_active",)
    search_fields = ("first_name", "last_name", "id", "email_address",)
    empty_value_display = '-'
    readonly_fields = ("last_login", )


class PersonnesAdmin(admin.ModelAdmin):
    list_display = ("cin_num", "cnc_num", "rc_num", "profession", "proof", "user_nom", "user_tel", "user_email", "commune")
    list_display_links = ["cin_num", "cnc_num", "rc_num"]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ["cin_num", "cnc_num", "rc_num"]
        else:  # Creating a new object
            return []


class Demande(admin.ModelAdmin):
    list_display = ("user_demande", "datetime", "status", "code_attestation",)
    list_filter = ("datetime",)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ["user_demande", "code_attestation", "datetime"]
        else:  # Creating a new object
            return []
        

admin.site.register(Particulier, ParticulierAdmin)
admin.site.register(Users, PersonnesAdmin)
admin.site.register(ProofDesc, JustificationAdmin)
admin.site.register(Cooperative, CooperativeAdmin)
admin.site.register(Societe, SocieteAdmin)
admin.site.register(Demandes, Demande)
admin.site.register(Acc_User, UserAdmin)
admin.site.site_header = "Assisto"
admin.site.site_title = "Assisto"
admin.site.index_title = "Assisto"
