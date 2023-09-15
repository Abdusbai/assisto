from django.db import models
from assisto.validators import validate_file_extension


class Province(models.Model):
    province_fr = models.CharField(max_length=255)
    province_ar = models.CharField(max_length=255)

    def __str__(self):
        return self.province_fr

    class Meta:
        ordering = ['id']


class Commune(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    commune_fr = models.CharField(max_length=255)
    commune_ar = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.commune_fr


class Profession(models.Model):
    profession_fr = models.CharField(max_length=255)
    profession_ar = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.profession_fr


class Proof(models.Model):
    proof_fr = models.CharField(max_length=255)
    proof_ar = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.proof_fr


class Users(models.Model):
    cin_num = models.CharField(max_length=255, unique=True, null=True, blank=True)
    cnc_num = models.CharField(max_length=255, unique=True, null=True, blank=True)
    rc_num = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profession = models.ForeignKey(Profession, null=True, blank=True, on_delete=models.CASCADE)
    proof = models.ForeignKey(Proof, null=True, blank=True, on_delete=models.CASCADE)
    user_nom = models.CharField(max_length=255, null=True, blank=True)
    user_tel = models.CharField(max_length=255, null=True, blank=True)
    user_email = models.EmailField(max_length=255, null=True, blank=True)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.cin_num is not None:
            return self.cin_num
        elif self.cnc_num is not None:
            return self.cnc_num
        elif self.rc_num is not None:
            return self.rc_num

    class Meta:
        verbose_name_plural = "Personnes"


class Particulier(models.Model):
    cin_num = models.ForeignKey(Users, to_field='cin_num', null=True, blank=True, on_delete=models.CASCADE)
    cin_pdf = models.FileField(upload_to='uploads/', validators=[validate_file_extension], null=True)
    prenom = models.CharField(max_length=255)
    date_naissance = models.DateField()
    adresse = models.CharField(max_length=255)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return str(self.cin_num)

    class Meta:
        verbose_name_plural = "Particulier"


class Cooperative(models.Model):
    cnc_num = models.ForeignKey(Users, to_field='cnc_num', null=True, blank=True, on_delete=models.CASCADE)
    cnc_pdf = models.FileField(upload_to='uploads/', validators=[validate_file_extension], null=True)
    nom_president = models.CharField(max_length=255)

    def __str__(self):
        return str(self.cnc_num)

    class Meta:
        verbose_name_plural = "Coopérative"


class Societe(models.Model):
    rc_num = models.ForeignKey(Users, to_field='rc_num', null=True, blank=True, on_delete=models.CASCADE)
    rc_pdf = models.FileField(upload_to='uploads/',validators=[validate_file_extension], null=True)
    nom_gerant = models.CharField(max_length=255)

    def __str__(self):
        return str(self.rc_num)

    class Meta:
        verbose_name_plural = "Société"


class Demandes(models.Model):
    user_demande = models.ForeignKey(Users, blank=True, on_delete=models.CASCADE, related_name='demandes_set')
    datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.BooleanField(default=False, blank=True, null=True)
    code_attestation = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.user_demande)
    
    class Meta:
        verbose_name_plural = "Demandes"


class ProofDesc(models.Model):
    user_proof = models.ForeignKey(Demandes, null=True, blank=True, on_delete=models.CASCADE, related_name='proofdesc_set')
    num_tf = models.CharField(max_length=255, blank=True, null=True)
    num_refe = models.CharField(max_length=255, blank=True, null=True)
    nom = models.CharField(max_length=255, blank=True, null=True)
    p_date = models.DateField(null=True, blank=True)
    nom_prenom_president = models.CharField(max_length=255, blank=True, null=True)
    duree = models.DateField(max_length=255, blank=True, null=True)
    tele = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, blank=True, null=True)
    pdf_name = models.FileField(upload_to='uploads/', validators=[validate_file_extension], null=True)

    def __str__(self):
        return str(self.user_proof)

    class Meta:
        verbose_name_plural = "Justifications"
        
        
class Acc_User(models.Model):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email_address = models.EmailField(max_length=100, null=False)
    password = models.CharField(max_length=100, null=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, verbose_name="creation date")
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email_address

    class Meta:
        verbose_name_plural = "Utilisateurs"
