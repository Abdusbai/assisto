import json
from audioop import reverse
import uuid
import qrcode
from io import BytesIO
from django.http import JsonResponse, HttpResponseRedirect
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from assisto.models import Particulier, Societe
from django.core.files.storage import FileSystemStorage
import re
from .models import Particulier, Demandes, Users, ProofDesc, Profession, Proof, Province, Commune, Cooperative, Acc_User
import http.client
import random
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
import os


def getResponse(request):
    botResponse = ''  # Initialize a variable to store the bot's response
    if request.method == 'POST':  # Check if the request method is POST
        # Get the uploaded file from the request
        file = request.FILES.get("file")
        fss = FileSystemStorage()  # Create a FileSystemStorage object
        # Save the file to the file system
        filename = fss.save(file.name, file)
        url = fss.url(filename)  # Get the URL of the saved file

        # Check if 'file_number' exists in the session
        if request.session.get('file_number'):
            request.session['file_number'] = 2  # Set 'file_number' to 2
            # Store the URL in 'user_certificate' in the session
            request.session['user_certificate'] = url

            # Get the user type from the session
            user_type = request.session.get('type')
            # Get the proof ID from the session
            proof = request.session.get('preuve_id')

            user = Users()  # Create a Users object
            user.user_nom = request.session.get('user_nom')  # Set the user's name
            # Set the user's telephone number
            user.user_tel = request.session.get('user_tel')
            # Set the user's proof object
            user.proof = Proof.objects.get(pk=int(request.session.get('preuve_id')))
            user.profession = Profession.objects.get(pk=int(request.session.get('profession_id')))  # Set the user's profession object

            proofdesc = ProofDesc()  # Create a ProofDesc object
            if proof == '1':  # Attestation de propriété
                proofdesc.num_tf = request.session.get('num_tf')
            elif proof == '2':  # Acte de propriété
                proofdesc.num_refe = request.session.get('num_refe')
            elif proof == '3':  # Contrat de bai
                proofdesc.num_refe = request.session.get('num_refe')
                # Convert the value of 'p_date' from the session to a date object and assign it to 'proofdesc.p_date'
                proofdesc.p_date = datetime.strptime(request.session.get('p_date'), "%d/%m/%Y").date()
                # Convert the value of 'duree' from the session to a date object and assign it to 'proofdesc.duree'
                proofdesc.duree = datetime.strptime(request.session.get('duree'), "%d/%m/%Y").date()
            # (Procuration, Attestation administrative, Attestation administrative, Attestation de vaccination, Attestation administrative)
            elif proof == '4' or proof == '5' or proof == '7' or proof == '8' or proof == '10':
                proofdesc.num_refe = request.session.get('num_refe')
                proofdesc.p_date = datetime.strptime(request.session.get('p_date'), "%d/%m/%Y").date()
            # (Adhésion Coop agricole, Adhésion Coop d'élevage, Adhésion Coop d'apiculture)
            elif proof == '6' or proof == '9' or proof == '11':
                proofdesc.nom = request.session.get('nom')
                proofdesc.nom_prenom_president = request.session.get('nom_prenom_president')
                proofdesc.tele = request.session.get('tele')
                proofdesc.email = request.session.get('email')
                proofdesc.commune = Commune.objects.get(pk=int(request.session.get('commune_id_prof')))

            proofdesc.pdf_name = request.session.get('user_certificate')  # Set the PDF name in proofdesc

            if user_type == '1':  # If user type is 'Particulier'
                user.cin_num = request.session.get('cin_num').upper()
                user.save()
                
                demandes = Demandes()
                demandes.user_demande = user
                demandes.save()

                particulier = Particulier()  # Create a Particulier object
                particulier.cin_num = Users.objects.get(cin_num=request.session.get('cin_num').upper())
                particulier.prenom = request.session.get('par_prenom')
                particulier.date_naissance = datetime.strptime(request.session.get('par_date_naissance'), "%d/%m/%Y").date()
                particulier.adresse = request.session.get('par_adresse')
                particulier.cin_pdf = request.session.get('user_card')
                particulier.province = Province.objects.get(pk=int(request.session.get('province_id')))
                particulier.save()

                proofdesc.user_proof = demandes
                proofdesc.save()

            elif user_type == '2':   # If user type is 'Coopérative'
                user.cnc_num = request.session.get('cnc_num').upper()
                user.user_email = request.session.get('email_coo')
                user.commune = Commune.objects.get(pk=int(request.session.get('commune_id_cop')))
                print(f"user_commune session: {request.session.get('commune_id_cop')}")
                print(f"user_commune: {user.commune}")
                user.save()
                
                demandes = Demandes()
                demandes.user_demande = user
                demandes.save()

                cooperative = Cooperative()  # Create a Cooperative object
                cooperative.cnc_num = Users.objects.get(cnc_num=request.session.get('cnc_num').upper())
                cooperative.cnc_pdf = request.session.get('user_card')
                cooperative.nom_president = request.session.get('nom_prenom_president_Coo')
                cooperative.save()

                proofdesc.user_proof = demandes
                proofdesc.save()             

            elif user_type == '3':   # If user type is 'Société'
                user.rc_num = request.session.get('rc_num').upper()
                user.user_email = request.session.get('email_coo')
                user.commune = Commune.objects.get(pk=int(request.session.get('commune_id_cop')))
                print(f"user_commune session: {request.session.get('commune_id_cop')}")
                print(f"user_commune: {user.commune}")
                user.save()
                
                demandes = Demandes()
                demandes.user_demande = user
                demandes.save()

                societe = Societe()  # Create a Societe object
                societe.rc_num = Users.objects.get(rc_num=request.session.get('rc_num').upper())
                societe.rc_pdf = request.session.get('user_card')
                societe.nom_gerant = request.session.get('nom_prenom_ger_soc')
                societe.save()

                proofdesc.user_proof = demandes
                proofdesc.save()

        else:
            request.session['file_number'] = 1
            request.session['user_card'] = url

        file_size = file.size / 1024  # Calculate the file size in KB
        file_size_string = ''  # Initialize a variable to store the file size string

        if file_size <= 999:  # If file size is less than or equal to 999 KB
            # Format the file size as KB
            file_size_string = f"{int(file_size)} KB"
        elif file_size > 999:  # If file size is greater than 999 KB
            file_size_mb = file_size / 1024  # Calculate the file size in MB
            # Format the file size as MB
            file_size_string = f"{round(file_size_mb, 2)} MB"

        data = {
            'file_url': url,
            'file_name': file.name,
            'file_size': str(file_size_string),
            'file_number': request.session.get('file_number')
        }  # Create a dictionary with file data

        if int(request.session.get('file_number')) == 2:
            del request.session['file_number']

        return JsonResponse(data)  # Return the file data as a JSON response
    else:
        # Get the current step from the request
        step = int(request.GET.get('stepMessage'))
        # Get the user's message from the request
        userMessage = request.GET.get('userMessage')
        lang = request.GET.get('lang')  # Get the language from the request
        ask_again = ''  # Initialize a variable to store a prompt to ask the user again

        if step == 0:  # If it's the first step
            if 'file_number' in request.session:
                del request.session['file_number']
            if userMessage.strip() == '1':  # If the user chooses option 1 (Particulier)
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>رقم بطاقة التعريف الوطنية (CIN)</strong>"
                else:
                    botResponse = "Veuillez indiquer le <strong>numéro de CIN</strong>"
                # Store the user's choice in the session
                request.session['type'] = userMessage.strip()
                step = 1  # Move to the next step
            elif userMessage.strip() == '2':  # If the user chooses option 2 (Coopérative)
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>الرقم الوطني للتعاونية (CNC)</strong>"
                else:
                    botResponse = "Veuillez indiquer le <strong>numéro national de la coopérative</strong>"
                # Store the user's choice in the session
                request.session['type'] = userMessage.strip()
                step = 2  # Move to the next step
            elif userMessage.strip() == '3':  # If the user chooses option 3 (Société)
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>رقم السجل التجاري (RC)</strong>"
                else:
                    botResponse = "Veuillez indiquer le <strong>numéro de Registre de Commerce (RC)</strong>"
                # Store the user's choice in the session
                request.session['type'] = userMessage.strip()
                step = 3  # Move to the next step
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 1:  # If it's step 1 (Particulier)
            # If the entered CIN number is valid
            if re.match(r'^[A-Za-z]{1,2}\d{1,10}$', userMessage.strip()):
                # Store the CIN number in the session
                request.session['cin_num'] = userMessage.strip()
                has_particulier = Particulier.objects.filter(cin_num__cin_num=userMessage.strip().upper()).exists()  # Check if Particulier with the given CIN number exists
                if has_particulier:  # If Particulier exists
                    has_demandes_with_true_status = Particulier.objects.filter(
                        cin_num__cin_num=userMessage.strip().upper(), cin_num__demandes_set__status=False)
                    if has_demandes_with_true_status:  # If there are demandes with true status
                        if lang == 'ar':
                            botResponse = "طلبكم قيد المعالجة، المرجو إعادة المحاولة لاحقا"
                        else:
                            botResponse = "Votre demande est en cours de traitement, veuillez réessayer plus tard"
                    else:
                        # Generate a random 4-digit verification code and convert it to a string
                        verification_code = str(random.randint(1000, 9999))
                        # Store the verification code in the session with the key 'verification_code_02'
                        request.session['verification_code_02'] = verification_code
                        # Store the stripped and uppercase version of 'userMessage' in the session with the key 'user_att'
                        request.session['user_att'] = userMessage.strip().upper()
                        # Store the string "particulier" in the session with the key 'u_type'
                        request.session['u_type'] = "particulier"
                        # Retrieve the Users object with the 'cin_num' attribute matching the stripped and uppercase version of 'userMessage' and assign it to 'u'
                        u = Users.objects.get(cin_num=userMessage.strip().upper())
                        # Create a hidden version of the user's telephone number by replacing characters with asterisks
                        hidden_number = u.user_tel[:-6] + '****' + u.user_tel[-2:]
                        send_sms(u.user_tel, f"{verification_code} est le code pour vérifier votre numéro de téléphone.")
                        print(verification_code)
                        if lang == 'ar':
                            botResponse = f"المرجو إدخال الرمز الذي تم إرساله إلى رقم هاتفك <strong>{hidden_number}</strong>"
                        else:
                            botResponse = f"Veuillez entrer le code qui a été envoyé à votre numéro de téléphone <strong>{hidden_number}</strong>"
                        step = 4
                else:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الإسم العائلي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le<strong> nom</strong>"
                    step = 5
            else:
                if lang == 'ar':
                    ask_again = "رقم بطاقة التعريف الوطنية (CIN) الذي أدخلتم<strong> غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer un numéro de CIN <strong>valide</strong>, veuillez réessayer !"

        elif step == 2:  # If it's step 2 (Coopérative)
            # If the entered CNC number is valid
            if re.match(r'^[A-Za-z]{1,2}[0-9]{1,7}$', userMessage.strip()):
                # Store the CNC number in the session
                request.session['cnc_num'] = userMessage.strip()
                has_cooperative = Cooperative.objects.filter(cnc_num__cnc_num=userMessage.strip().upper()).exists()  # Check if Cooperative with the given CNC number exists
                if has_cooperative:
                    has_demandes_with_true_status = Cooperative.objects.filter(cnc_num__cnc_num=userMessage.strip().upper(), cnc_num__demandes_set__status=False)
                    if has_demandes_with_true_status:  # If there are demandes with true status
                        if lang == 'ar':
                            botResponse = "طلبكم قيد المعالجة، المرجو إعادة المحاولة لاحقا"
                        else:
                            botResponse = "Votre demande est en cours de traitement, veuillez réessayer plus tard"
                    else:
                        verification_code = str(random.randint(1000, 9999))
                        request.session['verification_code_02'] = verification_code
                        request.session['user_att'] = userMessage.strip().upper()
                        request.session['u_type'] = "cooperative"
                        u = Users.objects.get(cnc_num=userMessage.strip().upper())
                        hidden_number = u.user_tel[:-6] + '****' + u.user_tel[-2:]
                        send_sms(u.user_tel, f"{verification_code} est le code pour vérifier votre numéro de téléphone.")
                        print(verification_code)
                        if lang == 'ar':
                            botResponse = f"المرجو إدخال الرمز الذي تم إرساله إلى رقم هاتفك <strong>{hidden_number}</strong>"
                        else:
                            botResponse = f"Veuillez entrer le code qui a été envoyé à votre numéro de téléphone <strong>{hidden_number}</strong>"
                        step = 4
                else:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>إسم التعاونية</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>nom de la coopérative</strong>"
                    step = 600
            else:
                if lang == 'ar':
                    ask_again = "الرقم الوطني للتعاونية (CNC) الذي أدخلتم<strong> غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer un numéro de CNC <strong>valide</strong>, veuillez réessayer !"

        elif step == 3:  # If it's step 3 (Société)
            # If the entered RC number is valid
            if re.match(r'^[A-Za-z]{1,2}[0-9]{1,7}$', userMessage.strip()):
                # Store the RC number in the session
                request.session['rc_num'] = userMessage.strip()
                has_Societe = Societe.objects.filter(rc_num__rc_num=userMessage.strip().upper()).exists()
                if has_Societe:  # If Societe exists
                    has_demandes_with_true_status = Societe.objects.filter(rc_num__rc_num=userMessage.strip().upper(), rc_num__demandes_set__status=False)
                    if has_demandes_with_true_status:  # If there are demandes with true status
                        if lang == 'ar':
                            botResponse = "طلبكم قيد المعالجة، المرجو إعادة المحاولة لاحقا"
                        else:
                            botResponse = "Votre demande est en cours de traitement, veuillez réessayer plus tard"
                    else:
                        verification_code = str(random.randint(1000, 9999))
                        request.session['verification_code_02'] = verification_code
                        request.session['user_att'] = userMessage.strip().upper()
                        request.session['u_type'] = "societe"
                        u = Users.objects.get(rc_num=userMessage.strip().upper())
                        hidden_number = u.user_tel[:-6] + '****' + u.user_tel[-2:]
                        send_sms(u.user_tel, f"{verification_code} est le code pour vérifier votre numéro de téléphone.")
                        print(verification_code)
                        if lang == 'ar':
                            botResponse = f"المرجو إدخال الرمز الذي تم إرساله إلى رقم هاتفك <strong>{hidden_number}</strong>"
                        else:
                            botResponse = f"Veuillez entrer le code qui a été envoyé à votre numéro de téléphone <strong>{hidden_number}</strong>"
                        step = 4
                else:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>إسم الشركة</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>nom de l'entreprise</strong>"
                    step = 600
            else:
                if lang == 'ar':
                    ask_again = "رقم السجل التجاري (RC) الذي أدخلتم<strong> غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer un numéro de RC <strong>valide</strong>, veuillez réessayer !"

        elif step == 600:
            if re.match(r'^[A-Za-z]+$', userMessage.strip()) and len(userMessage.strip()) <= 240:
                request.session['user_nom'] = userMessage.strip().capitalize()
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الإسم الكامل لمسير الشركة</strong> على شكل: <strong> الإسم العائلي الإسم الشخصي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>nom complet du gérant de l'entreprise</strong> au format: <strong>Nom Prénom</strong>"
                else:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الإسم الكامل لرئيس التعاونية</strong> على شكل: <strong> الإسم العائلي الإسم الشخصي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>nom complet du président de la coopérative</strong> au format: <strong>Nom Prénom</strong"
                step = 601
            else:
                if lang == 'ar':
                    ask_again = "الإسم الذي أدخلتم <strong>غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer un nom <strong>valide</strong>, veuillez réessayer !"

        elif step == 601:
            if re.match(r'^[A-Za-z]+ [A-Za-z]+(?: [A-Za-z]+)*$', userMessage.strip()) and len(userMessage.strip()) <= 240:
                if request.session.get('type') == '3':
                    request.session['nom_prenom_ger_soc'] = userMessage.strip().capitalize()
                else:
                    request.session['nom_prenom_president_Coo'] = userMessage.strip().capitalize()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>رقم الهاتف</strong> على شكل: <strong/>0xxxxxxxxx<strong>"
                else:
                    botResponse = "Veuillez indiquer le <strong>numéro de téléphone</strong> au format: <strong>0xxxxxxxxx</strong>"
                step = 602
            else:
                if lang == 'ar':
                    ask_again = "الإسم الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال الإسم الكامل على شكل: <strong> الإسم العائلي الإسم الشخصي</strong>"
                else:
                    ask_again = "Veuillez indiquer un nom complet <strong>valides</strong> au format: <strong>Nom Prénom</strong> !"

        elif step == 602:
            if re.match(r'^(05|06|07)[0-9]{8}$', userMessage.strip()):
                verification_code = str(random.randint(1000, 9999))
                request.session['user_tel'] = userMessage.strip()
                request.session['verification_code'] = verification_code
                send_sms(userMessage.strip(), f"{verification_code} est le code pour vérifier votre numéro de téléphone.")
                print(verification_code)
                if lang == 'ar':
                    botResponse = f"المرجو إدخال الرمز الذي تم إرساله إلى رقم الهاتف <strong>{userMessage.strip()}</strong>"
                else:
                    botResponse = f"Veuillez entrer le code qui a été envoyé au numéro de téléphone <strong>{userMessage.strip()}</strong>"
                step = 603
            else:
                if lang == 'ar':
                    ask_again = "رقم الهاتف الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال رقم هاتف على شكل: <strong/>0xxxxxxxxx<strong>"
                else:
                    ask_again = "Veuillez indiquer un numéro de téléphone <strong>valide</strong> au format: <strong>0xxxxxxxxx</strong> !"

        elif step == 603:
            verification_code = request.session.get('verification_code')
            if verification_code == userMessage.strip():
                del request.session['verification_code']
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>البريد الإلكتروني</strong>"
                else:
                    botResponse = "Veuillez indiquer <strong>l'adresse e-mail</strong>"
                step = 604
            else:
                if lang == 'ar':
                    botResponse = "الرمز الذي أدخلتم <strong>غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    botResponse = "Le code que vous avez entré est incorrect, veuillez réessayer !<br>"

        elif step == 604:
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', userMessage.strip()):
                request.session['email_coo'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = """
                                <span class='mb'>المرجو اختيار مقاطعتك:</span>
                                    <strong>1:</strong> بركان<br>
                                    <strong>2:</strong> الدريوش<br>
                                    <strong>3:</strong> فكيك<br>
                                    <strong>4:</strong> جرسيف<br>
                                    <strong>5:</strong> جرادة<br>
                                    <strong>6:</strong> الناظور<br>
                                    <strong>7:</strong> وجدة-أنكاد<br>
                                    <strong>8:</strong> تاوريرت
                                """
                else:
                    botResponse = """
                                    <span class='mb'>Veuillez sélectionner votre <strong>province</strong> :</span>
                                        <strong>1:</strong> Berkane<br>
                                        <strong>2:</strong> Driouch<br>
                                        <strong>3:</strong> Figuig<br>
                                        <strong>4:</strong> Guercif<br>
                                        <strong>5:</strong> Jerada<br>
                                        <strong>6:</strong> Nador<br>
                                        <strong>7:</strong> Oujda-Angad<br>
                                        <strong>8:</strong> Taourirt
                                """
                step = 605
            else:
                if lang == 'ar':
                    ask_again = "البريد الإلكتروني الذي أدخلتم <strong>غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer une adresse e-mail <strong>valide</strong> !"

        elif step == 605:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 8:
                request.session['province_coop'] = userMessage.strip()
                if int(userMessage.strip()) == 1:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>1:</strong> بركان<br>
                                        <strong>2:</strong> أحفير<br>
                                        <strong>3:</strong> سيدي سليمان الشراعة<br>
                                        <strong>4:</strong> بوهديلة<br>
                                        <strong>5:</strong> أكليم<br>
                                        <strong>6:</strong> عين الركادة<br>
                                        <strong>7:</strong> السعيدية<br>
                                        <strong>8:</strong> مداغ
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>1:</strong> Berkane<br>
                                        <strong>2:</strong> Ahfir<br>
                                        <strong>3:</strong> Sidi Slimane Echcharaa<br>
                                        <strong>4:</strong> Bouhdila<br>
                                        <strong>5:</strong> Aklim<br>
                                        <strong>6:</strong> Ain Erreggada<br>
                                        <strong>7:</strong> Saïdia<br>
                                        <strong>8:</strong> Madagh
                                    """
                    step = 606
                elif int(userMessage.strip()) == 2:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>9:</strong> تاليلت<br>
                                        <strong>10:</strong> واردانة<br>
                                        <strong>11:</strong> محاجر<br>
                                        <strong>12:</strong> بني توزين<br>
                                        <strong>13:</strong> ميدار<br>
                                        <strong>14:</strong> إفرني<br>
                                        <strong>15:</strong> تافرسيت<br>
                                        <strong>16:</strong> أزلاف<br>
                                        <strong>17:</strong> تصفت (كسيتة)<br>
                                        <strong>18:</strong> إجرمواس<br>
                                        <strong>19:</strong> أولاد أمغار<br>
                                        <strong>20:</strong> بودينار<br>
                                        <strong>21:</strong> بني مرغنين<br>
                                        <strong>22:</strong> تمسمان<br>
                                        <strong>23:</strong> تروكوت<br>
                                        <strong>24:</strong> أمطالسة<br>
                                        <strong>25:</strong> عين زهرة<br>
                                        <strong>26:</strong> أولاد بوبكر<br>
                                        <strong>27:</strong> دار الكبداني<br>
                                        <strong>28:</strong> أمجاو<br>
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>9:</strong> Talilit<br>
                                        <strong>10:</strong> Ouardana<br>
                                        <strong>11:</strong> M'Hajer<br>
                                        <strong>12:</strong> Bni Touzine<br>
                                        <strong>13:</strong> Midar<br>
                                        <strong>14:</strong> Iferni<br>
                                        <strong>15:</strong> Tafersit<br>
                                        <strong>16:</strong> Azlaf<br>
                                        <strong>17:</strong> Tsaft (Kassita)<br>
                                        <strong>18:</strong> Ijermaouas<br>
                                        <strong>19:</strong> Oulad Amghar<br>
                                        <strong>20:</strong> Boudinar<br>
                                        <strong>21:</strong> Bni Marghnine<br>
                                        <strong>22:</strong> Temsamane<br>
                                        <strong>23:</strong> Trougout<br>
                                        <strong>24:</strong> Mtalssa<br>
                                        <strong>25:</strong> Aïn Zohra<br>
                                        <strong>26:</strong> Oulad Boubker<br>
                                        <strong>27:</strong> Dar El Kebdani<br>
                                        <strong>28:</strong> Amejjaou
                                    """
                    step = 607
                elif int(userMessage.strip()) == 3:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>29:</strong> بني تاجيت<br>
                                        <strong>30:</strong> بوعنان<br>
                                        <strong>31:</strong> عين الشعير<br>
                                        <strong>32:</strong> عين شاوتر<br>
                                        <strong>33:</strong> بومريم<br>
                                        <strong>34<:/strong> تالسينت<br>
                                        <strong>35:</strong> بوشعون<br>
                                        <strong>36:</strong> بني ڭيل<br>
                                        <strong>37:</strong> عبو لكحل<br>
                                        <strong>38:</strong> معتركة<br>
                                        <strong>39:</strong> تندرارة<br>
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>29:</strong> Bni Tadjite<br>
                                        <strong>30:</strong> Bouanane<br>
                                        <strong>31:</strong> Aïn Chaïr<br>
                                        <strong>32:</strong> Aïn Chaouter<br>
                                        <strong>33:</strong> Boumerieme<br>
                                        <strong>34:</strong> Talsint<br>
                                        <strong>35:</strong> Bouchaouene<br>
                                        <strong>36:</strong> Bni Guil<br>
                                        <strong>37:</strong> Abbou Lakhal<br>
                                        <strong>38:</strong> Maatarka<br>
                                        <strong>39:</strong> Tendrara
                                    """
                    step = 608
                elif int(userMessage.strip()) == 4:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>40:</strong> جرسيف<br>
                                        <strong>41:</strong> مزكيتام<br>
                                        <strong>42:</strong> جماعة صاكا<br>
                                        <strong>43:</strong> الصباب<br>
                                        <strong>44:</strong> بركين<br>
                                        <strong>45:</strong> هوارة أولاد رحو<br>
                                        <strong>46:</strong> لمريجة<br>
                                        <strong>47:</strong> راس القصر<br>
                                        <strong>48:</strong> تادرت<br>
                                        <strong>49:</strong> أولاد بوريمة<br>
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>40:</strong> Guercif<br>
                                        <strong>41:</strong> Mazaghatam<br>
                                        <strong>42:</strong> Jamaa Sakka<br>
                                        <strong>43:</strong> Asbab<br>
                                        <strong>44:</strong> Berkine<br>
                                        <strong>45:</strong> Houara Ouled Rahou<br>
                                        <strong>46:</strong> Lamrijja<br>
                                        <strong>47:</strong> Ras El Qasr<br>
                                        <strong>48:</strong> Tadart<br>
                                        <strong>49:</strong> Ouled Bourima
                                    """
                    step = 609
                elif int(userMessage.strip()) == 5:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>50:</strong> العوينات<br>
                                        <strong>51:</strong> ڭنفودة<br>
                                        <strong>52:</strong> ڭفايت<br>
                                        <strong>53:</strong> البكاطة<br>
                                        <strong>54:</strong> رأس عصفور<br>
                                        <strong>55:</strong> سيدي بوبكر<br>
                                        <strong>56:</strong> تيولي<br>
                                        <strong>57:</strong> بني مطهر<br>
                                        <strong>58:</strong> أولاد سيدي عبد الحكيم<br>
                                        <strong>59:</strong> مريجة<br>
                                        <strong>60:</strong> أولاد غزييل<br>
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>50:</strong> Laaouinate<br>
                                        <strong>51:</strong> Guenfouda<br>
                                        <strong>52:</strong> Gafaït<br>
                                        <strong>53:</strong> Lebkata<br>
                                        <strong>54:</strong> Ras Asfour<br>
                                        <strong>55:</strong> Sidi Boubker<br>
                                        <strong>56:</strong> Tiouli<br>
                                        <strong>57:</strong> Bni Mathar<br>
                                        <strong>58:</strong> Ouled Sidi Abdelhakem<br>
                                        <strong>59:</strong> Mrija<br>
                                        <strong>60:</strong> Ouled Ghziyel
                                    """
                    step = 610
                elif int(userMessage.strip()) == 6:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>61:</strong> العروي<br>
                                        <strong>62:</strong> بني انصار<br>
                                        <strong>63:</strong> بني شيكر<br>
                                        <strong>64:</strong> فرخانة<br>
                                        <strong>65:</strong> إحدادن<br>
                                        <strong>66:</strong> جعدار<br>
                                        <strong>67:</strong> قرية أركمان<br>
                                        <strong>68:</strong> قاسطا<br>
                                        <strong>69:</strong> الناظور<br>
                                        <strong>70:</strong> رأس الما<br>
                                        <strong>71:</strong> سلوان<br>
                                        <strong>72:</strong> تفرسيت<br>
                                        <strong>73:</strong> تويمة<br>
                                        <strong>74:</strong> زايو<br>
                                        <strong>75:</strong> أزغنغان<br>
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>61:</strong> Al Aaroui<br>
                                        <strong>62:</strong> Bni Ansar<br>
                                        <strong>63:</strong> Bni Chiker<br>
                                        <strong>64:</strong> Farkhana<br>
                                        <strong>65:</strong> Ihddaden<br>
                                        <strong>66:</strong> Jaadar<br>
                                        <strong>67:</strong> Kariat Arekmane<br>
                                        <strong>68:</strong> Kassita<br>
                                        <strong>69:</strong> Nador<br>
                                        <strong>70:</strong> Ras El Ma<br>
                                        <strong>71:</strong> Selouane<br>
                                        <strong>72:</strong> Tafarssite<br>
                                        <strong>73:</strong> Taouima<br>
                                        <strong>74:</strong> Zaio<br>
                                        <strong>75:</strong> Azghanghane
                                    """
                    step = 611
                elif int(userMessage.strip()) == 7:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>76:</strong> بني درار<br>
                                        <strong>77:</strong> وجدة<br>
                                        <strong>78:</strong> أنكاد<br>
                                        <strong>79:</strong> نعيمة<br>
                                        <strong>80:</strong> عين الصفا<br>
                                        <strong>81:</strong> بني خالد<br>
                                        <strong>82:</strong> عسلي<br>
                                        <strong>83:</strong> مستفركي<br>
                                        <strong>84:</strong> بسارة<br>
                                        <strong>85:</strong> سيدي بولنوار<br>
                                        <strong>86:</strong> سيدي موسى لمهاية<br>
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>76:</strong> Bni Drar<br>
                                        <strong>77:</strong> Oujda<br>
                                        <strong>78:</strong> Angad<br>
                                        <strong>79:</strong> Naima<br>
                                        <strong>80:</strong> Ain Sfa<br>
                                        <strong>81:</strong> Bni Khaled<br>
                                        <strong>82:</strong> Isly<br>
                                        <strong>83:</strong> Mestferki<br>
                                        <strong>84:</strong> Bsara<br>
                                        <strong>85:</strong> Sidi Boulenouar<br>
                                        <strong>86:</strong> Sidi Moussa Lemhaya
                                    """
                    step = 612
                elif int(userMessage.strip()) == 8:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>87:</strong> القطيطير<br>
                                        <strong>88:</strong> أهل وادزا<br>
                                        <strong>89:</strong> ملج الويدان<br>
                                        <strong>90:</strong> عين لحجر<br>
                                        <strong>91:</strong> مشرع حمادي<br>
                                        <strong>92:</strong> مستغمر<br>
                                        <strong>93:</strong> تنشرفي<br>
                                        <strong>94:</strong> سيدي علي بلقاسم<br>
                                        <strong>95:</strong> سيدي لحسن<br>
                                        <strong>96:</strong> العطف<br>
                                        <strong>97:</strong> أولاد محمد<br>
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>87:</strong> Gteter<br>
                                        <strong>88:</strong> Ahl Oued Za<br>
                                        <strong>89:</strong> Melg El Ouidane<br>
                                        <strong>90:</strong> Ain Lehjer<br>
                                        <strong>91:</strong> Mechraa Hammadi<br>
                                        <strong>92:</strong> Mestegmer<br>
                                        <strong>93:</strong> Tancherfi<br>
                                        <strong>94:</strong> Sidi Ali Bel Quassem<br>
                                        <strong>95:</strong> Sidi Lahsen<br>
                                        <strong>96:</strong> El Atef<br>
                                        <strong>97:</strong> Ouled M'Hamed
                                    """
                    step = 613
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 606:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 8:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"1-8: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 607:
            if userMessage.strip().isdigit() and 9 <= int(userMessage.strip()) <= 28:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"9-28: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 608:
            if userMessage.strip().isdigit() and 29 <= int(userMessage.strip()) <= 39:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"29-39: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 609:
            if userMessage.strip().isdigit() and 40 <= int(userMessage.strip()) <= 49:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"40-49: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 610:
            if userMessage.strip().isdigit() and 50 <= int(userMessage.strip()) <= 60:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"50-60: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 611:
            if userMessage.strip().isdigit() and 61 <= int(userMessage.strip()) <= 75:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"61-75: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو الضغط على الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو الضغط على الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 612:
            if userMessage.strip().isdigit() and 76 <= int(userMessage.strip()) <= 86:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"76-86: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 613:
            if userMessage.strip().isdigit() and 87 <= int(userMessage.strip()) <= 97:
                request.session['commune_id_cop'] = userMessage.strip()
                print(f"87-97: {request.session.get('commune_id_cop')}")
                if request.session.get('type') == '3':
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل التجاري (RC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre du commerce (RC)</strong></span>"
                else:
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة السجل المحلي للتعاونيات (CNC)</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du registre local des coopératives (CNC)</strong></span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 4:
            verification_code = request.session.get('verification_code_02')
            u_type = request.session.get('u_type')
            if verification_code == userMessage.strip():
                del request.session['verification_code_02']
                if u_type == "particulier":
                    botResponse = f"""
                            <span class="file-download">
                            <img src="static/assisto/img/pdf.png" alt="pdf logo" class="pdf-logo">
                            <span class="file-infos">
                                <p class="file-name">Attestation_agricole_{request.session.get('user_att')}</p>
                                <p>
                                <span class="file-size">372 kb</span>
                                </p>
                            </span>
                            <a href="assisto/attestation/download/{request.session.get('user_att')}/particulier" class="download-link">
                                <svg xmlns="http://www.w3.org/2000/svg" class="download-logo" viewBox="0 0 512 512">
                                <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"
                                    d="M176 262.62L256 342l80-79.38M256 330.97V170" />
                                <path d="M256 64C150 64 64 150 64 256s86 192 192 192 192-86 192-192S362 64 256 64z" fill="none"
                                    stroke="currentColor" stroke-miterlimit="10" />
                                </svg>
                            </a>
                            </span>"""  # constructs an HTML snippet for displaying a file download link for an agricultural attestation
                elif u_type == "cooperative":
                    botResponse = f"""
                        <span class="file-download">
                        <img src="static/assisto/img/pdf.png" alt="pdf logo" class="pdf-logo">
                        <span class="file-infos">
                            <p class="file-name">Attestation_agricole_{request.session.get('user_att')}</p>
                            <p>
                            <span class="file-size">372 kb</span>
                            </p>
                        </span>
                        <a href="assisto/attestation/download/{request.session.get('user_att')}/cooperative" class="download-link">
                            <svg xmlns="http://www.w3.org/2000/svg" class="download-logo" viewBox="0 0 512 512">
                            <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"
                                d="M176 262.62L256 342l80-79.38M256 330.97V170" />
                            <path d="M256 64C150 64 64 150 64 256s86 192 192 192 192-86 192-192S362 64 256 64z" fill="none"
                                stroke="currentColor" stroke-miterlimit="10" />
                            </svg>
                        </a>
                        </span>"""
                elif u_type == "societe":
                    botResponse = f"""
                        <span class="file-download">
                        <img src="static/assisto/img/pdf.png" alt="pdf logo" class="pdf-logo">
                        <span class="file-infos">
                            <p class="file-name">Attestation_agricole_{request.session.get('user_att')}</p>
                            <p>
                            <span class="file-size">372 kb</span>
                            </p>
                        </span>
                        <a href="assisto/attestation/download/{request.session.get('user_att')}/societe" class="download-link">
                            <svg xmlns="http://www.w3.org/2000/svg" class="download-logo" viewBox="0 0 512 512">
                            <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"
                                d="M176 262.62L256 342l80-79.38M256 330.97V170" />
                            <path d="M256 64C150 64 64 150 64 256s86 192 192 192 192-86 192-192S362 64 256 64z" fill="none"
                                stroke="currentColor" stroke-miterlimit="10" />
                            </svg>
                        </a>
                        </span>"""
                del request.session['u_type']
                del request.session['user_att']
                return JsonResponse({'response': botResponse, 'att': True, 'step': step, 'again': ask_again})
            else:
                if lang == 'ar':
                    botResponse = "الرمز الذي أدخلتم <strong>غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    botResponse = "Le code que vous avez entré est incorrect, veuillez réessayer !<br>"

        elif step == 5:
            if re.match(r'^[A-Za-z]+$', userMessage.strip()) and len(userMessage.strip()) <= 240:
                request.session['user_nom'] = userMessage.strip().capitalize()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>الإسم الشخصي</strong>"
                else:
                    botResponse = "Veuillez indiquer le <strong>prénom</strong>"
                step = 6
            else:
                if lang == 'ar':
                    ask_again = "الإسم العائلي الذي أدخلتم<strong> غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer un nom <strong>valide</strong> !"

        elif step == 6:
            if re.match(r'^[A-Za-z]+$', userMessage.strip()) and len(userMessage.strip()) <= 240:
                request.session['par_prenom'] = userMessage.strip(
                ).capitalize()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>تاريخ الميلاد</strong> على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    botResponse = "Veuillez indiquer votre <strong>date de naissance</strong> au format: <strong>JJ/MM/AAAA</strong>"
                step = 7
            else:
                if lang == 'ar':
                    ask_again = "الإسم الشخصي الذي أدخلتم<strong> غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer un prénom <strong>valide</strong> !"

        elif step == 7:
            if re.match(r'^(0[1-9]|1\d|2\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}$', userMessage.strip()):
                request.session['par_date_naissance'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>رقم الهاتف</strong> على شكل: <strong/>0xxxxxxxxx<strong>"
                else:
                    botResponse = "Veuillez indiquer votre <strong>numéro de téléphone</strong> au format: <strong>0xxxxxxxxx</strong>"
                step = 8
            else:
                if lang == 'ar':
                    ask_again = "التاريخ الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال تاريخ على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    ask_again = "Veuillez indiquer une date <strong>valide</strong> au format: <strong>JJ/MM/AAAA</strong> !"

        elif step == 8:
            if re.match(r'^(05|06|07)[0-9]{8}$', userMessage.strip()):
                verification_code = str(random.randint(1000, 9999))
                request.session['user_tel'] = userMessage.strip()
                request.session['verification_code'] = verification_code
                send_sms(userMessage.strip(), f"{verification_code} est le code pour vérifier votre numéro de téléphone.")
                print(verification_code)
                if lang == 'ar':
                    botResponse = f"المرجو إدخال الرمز الذي تم إرساله إلى رقم هاتفك <strong>{userMessage.strip()}</strong>"
                else:
                    botResponse = f"Veuillez entrer le code qui a été envoyé à votre numéro de téléphone <strong>{userMessage.strip()}</strong>"
                step = 9
            else:
                if lang == 'ar':
                    ask_again = "رقم الهاتف الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال رقم هاتف على شكل: <strong/>0xxxxxxxxx<strong>"
                else:
                    ask_again = "Veuillez indiquer un numéro de téléphone <strong>valide</strong> au format: <strong>0xxxxxxxxx</strong> !"

        elif step == 9:
            verification_code = request.session.get('verification_code')

            if verification_code == userMessage.strip():
                del request.session['verification_code']
                if lang == 'ar':
                    botResponse = """
                                <span class='mb'>المرجو اختيار مقاطعتك:</span>
                                    <strong>1:</strong> بركان<br>
                                    <strong>2:</strong> الدريوش<br>
                                    <strong>3:</strong> فكيك<br>
                                    <strong>4:</strong> جرسيف<br>
                                    <strong>5:</strong> جرادة<br>
                                    <strong>6:</strong> الناظور<br>
                                    <strong>7:</strong> وجدة-أنكاد<br>
                                    <strong>8:</strong> تاوريرت
                                """
                else:
                    botResponse = """
                                    <span class='mb'>Veuillez sélectionner votre <strong>province</strong> :</span>
                                        <strong>1:</strong> Berkane<br>
                                        <strong>2:</strong> Driouch<br>
                                        <strong>3:</strong> Figuig<br>
                                        <strong>4:</strong> Guercif<br>
                                        <strong>5:</strong> Jerada<br>
                                        <strong>6:</strong> Nador<br>
                                        <strong>7:</strong> Oujda-Angad<br>
                                        <strong>8:</strong> Taourirt
                                """
                step = 10
            else:
                if lang == 'ar':
                    botResponse = "الرمز الذي أدخلتم <strong>غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    botResponse = "Le code que vous avez entré est incorrect, veuillez réessayer !<br>"

        elif step == 10:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 8:
                request.session['province_id'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>العنوان</strong>"
                else:
                    botResponse = "Veuillez indiquer l'<strong>adresse</strong>"
                step = 11
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 11:
            if len(userMessage.strip()) <= 240:
                request.session['par_adresse'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو الضغط على الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من بطاقة التعريف الوطنية (CIN)</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du CIN</strong> (recto verso)</span>"
                step = 12
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "العنوان الذي أدخلتم<strong> غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer une adresse <strong>valide</strong> !"

        elif step == 12:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 3:
                request.session['profession_id'] = userMessage.strip()
                if int(userMessage.strip()) == 1:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار أحد المستندات التالية المتوفرة:</span>
                                        <strong>1:</strong> شهادة الملكية<br>
                                        <strong>2:</strong> عقد الملكية<br>
                                        <strong>3:</strong> عقد الكراء<br>
                                        <strong>4:</strong> وكالة<br>
                                        <strong>5:</strong> شهادة إدارية<br>
                                        <strong>6:</strong> انخراط بتعاونية فلاحية<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez choisir l'un des <strong>documents disponibles suivants:</strong> :</span>
                                        <strong>1:</strong> Attestation de propriété<br>
                                        <strong>2:</strong> Acte de propriété<br>
                                        <strong>3:</strong> Contrat de bail<br>
                                        <strong>4:</strong> Procuration<br>
                                        <strong>5:</strong> Attestation administrative<br>
                                        <strong>6:</strong> Adhésion Coop agricole<br>
                                    """
                    step = 13
                elif int(userMessage.strip()) == 2:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار أحد المستندات التالية المتوفرة:</span>
                                        <strong>1:</strong> شهادة إدارية<br>
                                        <strong>2:</strong> شهادة التلقيح<br>
                                        <strong>3:</strong> إنخراط بتعاونية لتربية الماشية<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez choisir l'un des <strong>documents disponibles suivants:</strong> :</span>
                                        <strong>1:</strong> Attestation administrative<br>
                                        <strong>2:</strong> Attestation de vaccination<br>
                                        <strong>3:</strong> Adhésion Coop d'élevage<br>
                                    """
                    step = 14
                elif int(userMessage.strip()) == 3:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار أحد المستندات التالية المتوفرة:</span>
                                        <strong>1:</strong> شهادة إدارية<br>
                                        <strong>2:</strong> انخراط بتعاونية لتربية النحل<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez choisir l'un des <strong>documents disponibles suivants:</strong> :</span>
                                        <strong>1:</strong> Attestation administrative<br>
                                        <strong>2:</strong> Adhésion Coop d'apiculture<br>
                                    """
                    step = 15
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 13:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 6:
                request.session['preuve_id'] = userMessage.strip()
                if int(userMessage.strip()) == 1:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>رقم الرسم العقاري (N° T.F)</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro du titre foncier (N° T.F)</strong>"
                    step = 16
                elif int(userMessage.strip()) == 2:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الرقم المرجعي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro de référence</strong>"
                    step = 17
                elif int(userMessage.strip()) == 3:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الرقم المرجعي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro de référence</strong>"
                    step = 18
                elif int(userMessage.strip()) == 4:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الرقم المرجعي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro de référence</strong>"
                    step = 21
                elif int(userMessage.strip()) == 5:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الرقم المرجعي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro de référence</strong>"
                    step = 23
                elif int(userMessage.strip()) == 6:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الإسم</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>nom</strong>"
                    step = 25
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 14:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 3:
                request.session['preuve_id'] = int(userMessage.strip()) + 6
                if int(userMessage.strip()) == 1:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الرقم المرجعي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro de référence</strong>"
                    step = 23
                elif int(userMessage.strip()) == 2:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الرقم المرجعي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro de référence</strong>"
                    step = 38
                elif int(userMessage.strip()) == 3:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الإسم</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>nom</strong>"
                    step = 25
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 15:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 2:
                request.session['preuve_id'] = int(userMessage.strip()) + 9
                if int(userMessage.strip()) == 1:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الرقم المرجعي</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>numéro de référence</strong>"
                    step = 23
                elif int(userMessage.strip()) == 2:
                    if lang == 'ar':
                        botResponse = "المرجو إدخال <strong>الإسم</strong>"
                    else:
                        botResponse = "Veuillez indiquer le <strong>nom</strong>"
                    step = 25
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 16:
            request.session['num_tf'] = userMessage.strip()
            if lang == 'ar':
                botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من شهادة الملكية</span></strong>"
            else:
                botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie d'attestation de propriété</strong></span>"
            step = 555
            return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})

        elif step == 17:
            request.session['num_refe'] = userMessage.strip()
            if lang == 'ar':
                botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عقد الملكية</span></strong>"
            else:
                botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie d'acte de propriété</strong></span>"
            step = 556
            return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})

        elif step == 18:
            request.session['num_refe'] = userMessage.strip()
            if lang == 'ar':
                botResponse = "المرجو إدخال <strong>تاريخ عقد الكراء</strong> على شكل: <strong/>سنة/شهر/يوم<strong>"
            else:
                botResponse = "Veuillez indiquer la <strong>date du contrat de bail</strong> au format: <strong>JJ/MM/AAAA</strong>"
            step = 19

        elif step == 19:
            if re.match(r'^(0[1-9]|1\d|2\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}$', userMessage.strip()):
                request.session['p_date'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>تاريخ إنتهاء صلاحية عقد الكراء</strong> على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    botResponse = "Veuillez indiquer la <strong>date d'expiration du contrat de bail</strong> au format: <strong>JJ/MM/AAAA</strong>"
                step = 20
            else:
                if lang == 'ar':
                    ask_again = "التاريخ الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال تاريخ على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    ask_again = "Veuillez indiquer une date <strong>valide</strong> au format: <strong>JJ/MM/AAAA</strong> !"

        elif step == 20:
            if re.match(r'^(0[1-9]|1\d|2\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}$', userMessage.strip()):
                date_string1 = request.session.get('p_date')

                # Convert date_string1 to datetime object
                date1 = datetime.strptime(date_string1, "%d/%m/%Y").date()

                # Convert userMessage.strip() to datetime object
                date2 = datetime.strptime(
                    userMessage.strip(), "%d/%m/%Y").date()

                if date2 > date1:
                    request.session['duree'] = userMessage.strip()
                    if lang == 'ar':
                        botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عقد الكراء</span></strong>"
                    else:
                        botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie du contrat de bail</strong></span>"
                    step = 557
                    return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
                else:
                    if lang == 'ar':
                        botResponse = "تاريخ عقد الكراء يجب أن يكون<strong> أكبر</strong> من تاريخ إنتهاء صلاحيته، المرجو إعادة المحاولة !"
                    else:
                        botResponse = "La date du contrat de bail doit être <strong>supérieure</strong> à la date d'espiration, veuillez réessayer !"

            else:
                if lang == 'ar':
                    ask_again = "التاريخ الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال تاريخ على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    ask_again = "Veuillez indiquer une date <strong>valide</strong> au format: <strong>JJ/MM/AAAA</strong> !"

        elif step == 21:
            request.session['num_refe'] = userMessage.strip()
            if lang == 'ar':
                botResponse = "المرجو إدخال <strong>تاريخ الوكالة</strong> على شكل: <strong/>سنة/شهر/يوم<strong>"
            else:
                botResponse = "Veuillez indiquer la <strong>date de la procuration</strong> au format: <strong>JJ/MM/AAAA</strong>"
            step = 22

        elif step == 22:
            if re.match(r'^(0[1-9]|1\d|2\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}$', userMessage.strip()):
                request.session['p_date'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من التوكيل</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong> copie de la procuration</strong></span>"
                step = 558
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "التاريخ الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال تاريخ على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    ask_again = "Veuillez indiquer une date <strong>valide</strong> au format: <strong>JJ/MM/AAAA</strong> !"

        elif step == 23:
            request.session['num_refe'] = userMessage.strip()
            if lang == 'ar':
                botResponse = "المرجو إدخال <strong>تاريخ الشهادة الإدارية</strong> على شكل: <strong/>سنة/شهر/يوم<strong>"
            else:
                botResponse = "Veuillez indiquer la <strong>date de l'attestation administrative</strong> au format: <strong>JJ/MM/AAAA</strong>"
            step = 24

        elif step == 24:
            if re.match(r'^(0[1-9]|1\d|2\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}$', userMessage.strip()):
                request.session['p_date'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من الشهادة الإدارية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant une <strong>copie d'attestation administrative</strong></span>"
                step = 558
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "التاريخ الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال تاريخ على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    ask_again = "Veuillez indiquer une date <strong>valide</strong> au format: <strong>JJ/MM/AAAA</strong> !"

        elif step == 25:
            request.session['nom'] = userMessage.strip()
            if lang == 'ar':
                botResponse = "المرجو إدخال <strong>الإسم الكامل لرئيس التعاونية</strong> على شكل: <strong> الإسم العائلي الإسم الشخصي</strong>"
            else:
                botResponse = "Veuillez indiquer le <strong>nom complet du président de la coopérative</strong> au format: <strong>Nom Prénom</strong"
            step = 26

        elif step == 26:
            if re.match(r'^[A-Za-z]+ [A-Za-z]+(?: [A-Za-z]+)*$', userMessage.strip()) and len(
                    userMessage.strip()) <= 240:
                request.session['nom_prenom_president'] = userMessage.strip().capitalize()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>رقم الهاتف</strong> على شكل: <strong/>0xxxxxxxxx<strong>"
                else:
                    botResponse = "Veuillez indiquer le <strong>numéro de téléphone</strong> au format: <strong>0xxxxxxxxx</strong>"
                step = 27
            else:
                if lang == 'ar':
                    ask_again = "الإسم الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال الإسم الكامل على شكل: <strong> الإسم العائلي الإسم الشخصي</strong>"
                else:
                    ask_again = "Veuillez indiquer un nom complet <strong>valides</strong> au format: <strong>Nom Prénom</strong> !"

        elif step == 27:
            if re.match(r'^(05|06|07)[0-9]{8}$', userMessage.strip()):
                request.session['tele'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "المرجو إدخال <strong>البريد الإلكتروني</strong>"
                else:
                    botResponse = "Veuillez indiquer <strong>l'adresse e-mail</strong>"
                step = 28
            else:
                if lang == 'ar':
                    ask_again = "رقم الهاتف الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال رقم هاتف على شكل: <strong/>0xxxxxxxxx<strong>"
                else:
                    ask_again = "Veuillez indiquer un numéro de téléphone <strong>valide</strong> au format: <strong>0xxxxxxxxx</strong> !"

        elif step == 28:
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', userMessage.strip()):
                request.session['email'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = """
                                <span class='mb'>المرجو اختيار مقاطعتك:</span>
                                    <strong>1:</strong> بركان<br>
                                    <strong>2:</strong> الدريوش<br>
                                    <strong>3:</strong> فكيك<br>
                                    <strong>4:</strong> جرسيف<br>
                                    <strong>5:</strong> جرادة<br>
                                    <strong>6:</strong> الناظور<br>
                                    <strong>7:</strong> وجدة-أنكاد<br>
                                    <strong>8:</strong> تاوريرت
                                """
                else:
                    botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>province</strong> :</span>
                                    <strong>1:</strong> Berkane<br>
                                    <strong>2:</strong> Driouch<br>
                                    <strong>3:</strong> Figuig<br>
                                    <strong>4:</strong> Guercif<br>
                                    <strong>5:</strong> Jerada<br>
                                    <strong>6:</strong> Nador<br>
                                    <strong>7:</strong> Oujda-Angad<br>
                                    <strong>8:</strong> Taourirt
                                """
                step = 29
            else:
                if lang == 'ar':
                    ask_again = "البريد الإلكتروني الذي أدخلتم <strong>غير صحيح</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "Veuillez indiquer une adresse e-mail <strong>valide</strong> !"

        elif step == 29:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 8:
                request.session['province_prof'] = userMessage.strip()
                if int(userMessage.strip()) == 1:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>1:</strong> بركان<br>
                                        <strong>2:</strong> أحفير<br>
                                        <strong>3:</strong> سيدي سليمان الشراعة<br>
                                        <strong>4:</strong> بوهديلة<br>
                                        <strong>5:</strong> أكليم<br>
                                        <strong>6:</strong> عين الركادة<br>
                                        <strong>7:</strong> السعيدية<br>
                                        <strong>8:</strong> مداغ
                                    """
                    else:
                        botResponse = """
                                        <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                        <strong>1:</strong> Berkane<br>
                                        <strong>2:</strong> Ahfir<br>
                                        <strong>3:</strong> Sidi Slimane Echcharaa<br>
                                        <strong>4:</strong> Bouhdila<br>
                                        <strong>5:</strong> Aklim<br>
                                        <strong>6:</strong> Ain Erreggada<br>
                                        <strong>7:</strong> Saïdia<br>
                                        <strong>8:</strong> Madagh
                                    """
                    step = 30
                elif int(userMessage.strip()) == 2:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>9:</strong> تاليلت<br>
                                        <strong>10:</strong> واردانة<br>
                                        <strong>11:</strong> محاجر<br>
                                        <strong>12:</strong> بني توزين<br>
                                        <strong>13:</strong> ميدار<br>
                                        <strong>14:</strong> إفرني<br>
                                        <strong>15:</strong> تافرسيت<br>
                                        <strong>16:</strong> أزلاف<br>
                                        <strong>17:</strong> تصفت (كسيتة)<br>
                                        <strong>18:</strong> إجرمواس<br>
                                        <strong>19:</strong> أولاد أمغار<br>
                                        <strong>20:</strong> بودينار<br>
                                        <strong>21:</strong> بني مرغنين<br>
                                        <strong>22:</strong> تمسمان<br>
                                        <strong>23:</strong> تروكوت<br>
                                        <strong>24:</strong> أمطالسة<br>
                                        <strong>25:</strong> عين زهرة<br>
                                        <strong>26:</strong> أولاد بوبكر<br>
                                        <strong>27:</strong> دار الكبداني<br>
                                        <strong>28:</strong> أمجاو<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                    <strong>9:</strong> Talilit<br>
                                    <strong>10:</strong> Ouardana<br>
                                    <strong>11:</strong> M'Hajer<br>
                                    <strong>12:</strong> Bni Touzine<br>
                                    <strong>13:</strong> Midar<br>
                                    <strong>14:</strong> Iferni<br>
                                    <strong>15:</strong> Tafersit<br>
                                    <strong>16:</strong> Azlaf<br>
                                    <strong>17:</strong> Tsaft (Kassita)<br>
                                    <strong>18:</strong> Ijermaouas<br>
                                    <strong>19:</strong> Oulad Amghar<br>
                                    <strong>20:</strong> Boudinar<br>
                                    <strong>21:</strong> Bni Marghnine<br>
                                    <strong>22:</strong> Temsamane<br>
                                    <strong>23:</strong> Trougout<br>
                                    <strong>24:</strong> Mtalssa<br>
                                    <strong>25:</strong> Aïn Zohra<br>
                                    <strong>26:</strong> Oulad Boubker<br>
                                    <strong>27:</strong> Dar El Kebdani<br>
                                    <strong>28:</strong> Amejjaou
                                """
                    step = 31
                elif int(userMessage.strip()) == 3:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>29:</strong> بني تاجيت<br>
                                        <strong>30:</strong> بوعنان<br>
                                        <strong>31:</strong> عين الشعير<br>
                                        <strong>32:</strong> عين شاوتر<br>
                                        <strong>33:</strong> بومريم<br>
                                        <strong>34<:/strong> تالسينت<br>
                                        <strong>35:</strong> بوشعون<br>
                                        <strong>36:</strong> بني ڭيل<br>
                                        <strong>37:</strong> عبو لكحل<br>
                                        <strong>38:</strong> معتركة<br>
                                        <strong>39:</strong> تندرارة<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                    <strong>29:</strong> Bni Tadjite<br>
                                    <strong>30:</strong> Bouanane<br>
                                    <strong>31:</strong> Aïn Chaïr<br>
                                    <strong>32:</strong> Aïn Chaouter<br>
                                    <strong>33:</strong> Boumerieme<br>
                                    <strong>34:</strong> Talsint<br>
                                    <strong>35:</strong> Bouchaouene<br>
                                    <strong>36:</strong> Bni Guil<br>
                                    <strong>37:</strong> Abbou Lakhal<br>
                                    <strong>38:</strong> Maatarka<br>
                                    <strong>39:</strong> Tendrara
                                """
                    step = 32
                elif int(userMessage.strip()) == 4:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>40:</strong> جرسيف<br>
                                        <strong>41:</strong> مزكيتام<br>
                                        <strong>42:</strong> جماعة صاكا<br>
                                        <strong>43:</strong> الصباب<br>
                                        <strong>44:</strong> بركين<br>
                                        <strong>45:</strong> هوارة أولاد رحو<br>
                                        <strong>46:</strong> لمريجة<br>
                                        <strong>47:</strong> راس القصر<br>
                                        <strong>48:</strong> تادرت<br>
                                        <strong>49:</strong> أولاد بوريمة<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                    <strong>40:</strong> Guercif<br>
                                    <strong>41:</strong> Mazaghatam<br>
                                    <strong>42:</strong> Jamaa Sakka<br>
                                    <strong>43:</strong> Asbab<br>
                                    <strong>44:</strong> Berkine<br>
                                    <strong>45:</strong> Houara Ouled Rahou<br>
                                    <strong>46:</strong> Lamrijja<br>
                                    <strong>47:</strong> Ras El Qasr<br>
                                    <strong>48:</strong> Tadart<br>
                                    <strong>49:</strong> Ouled Bourima
                                """
                    step = 33
                elif int(userMessage.strip()) == 5:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>50:</strong> العوينات<br>
                                        <strong>51:</strong> ڭنفودة<br>
                                        <strong>52:</strong> ڭفايت<br>
                                        <strong>53:</strong> البكاطة<br>
                                        <strong>54:</strong> رأس عصفور<br>
                                        <strong>55:</strong> سيدي بوبكر<br>
                                        <strong>56:</strong> تيولي<br>
                                        <strong>57:</strong> بني مطهر<br>
                                        <strong>58:</strong> أولاد سيدي عبد الحكيم<br>
                                        <strong>59:</strong> مريجة<br>
                                        <strong>60:</strong> أولاد غزييل<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                    <strong>50:</strong> Laaouinate<br>
                                    <strong>51:</strong> Guenfouda<br>
                                    <strong>52:</strong> Gafaït<br>
                                    <strong>53:</strong> Lebkata<br>
                                    <strong>54:</strong> Ras Asfour<br>
                                    <strong>55:</strong> Sidi Boubker<br>
                                    <strong>56:</strong> Tiouli<br>
                                    <strong>57:</strong> Bni Mathar<br>
                                    <strong>58:</strong> Ouled Sidi Abdelhakem<br>
                                    <strong>59:</strong> Mrija<br>
                                    <strong>60:</strong> Ouled Ghziyel
                                """
                    step = 34
                elif int(userMessage.strip()) == 6:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>61:</strong> العروي<br>
                                        <strong>62:</strong> بني انصار<br>
                                        <strong>63:</strong> بني شيكر<br>
                                        <strong>64:</strong> فرخانة<br>
                                        <strong>65:</strong> إحدادن<br>
                                        <strong>66:</strong> جعدار<br>
                                        <strong>67:</strong> قرية أركمان<br>
                                        <strong>68:</strong> قاسطا<br>
                                        <strong>69:</strong> الناظور<br>
                                        <strong>70:</strong> رأس الما<br>
                                        <strong>71:</strong> سلوان<br>
                                        <strong>72:</strong> تفرسيت<br>
                                        <strong>73:</strong> تويمة<br>
                                        <strong>74:</strong> زايو<br>
                                        <strong>75:</strong> أزغنغان<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                    <strong>61:</strong> Al Aaroui<br>
                                    <strong>62:</strong> Bni Ansar<br>
                                    <strong>63:</strong> Bni Chiker<br>
                                    <strong>64:</strong> Farkhana<br>
                                    <strong>65:</strong> Ihddaden<br>
                                    <strong>66:</strong> Jaadar<br>
                                    <strong>67:</strong> Kariat Arekmane<br>
                                    <strong>68:</strong> Kassita<br>
                                    <strong>69:</strong> Nador<br>
                                    <strong>70:</strong> Ras El Ma<br>
                                    <strong>71:</strong> Selouane<br>
                                    <strong>72:</strong> Tafarssite<br>
                                    <strong>73:</strong> Taouima<br>
                                    <strong>74:</strong> Zaio<br>
                                    <strong>75:</strong> Azghanghane
                                """
                    step = 35
                elif int(userMessage.strip()) == 7:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>76:</strong> بني درار<br>
                                        <strong>77:</strong> وجدة<br>
                                        <strong>78:</strong> أنكاد<br>
                                        <strong>79:</strong> نعيمة<br>
                                        <strong>80:</strong> عين الصفا<br>
                                        <strong>81:</strong> بني خالد<br>
                                        <strong>82:</strong> عسلي<br>
                                        <strong>83:</strong> مستفركي<br>
                                        <strong>84:</strong> بسارة<br>
                                        <strong>85:</strong> سيدي بولنوار<br>
                                        <strong>86:</strong> سيدي موسى لمهاية<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                    <strong>76:</strong> Bni Drar<br>
                                    <strong>77:</strong> Oujda<br>
                                    <strong>78:</strong> Angad<br>
                                    <strong>79:</strong> Naima<br>
                                    <strong>80:</strong> Ain Sfa<br>
                                    <strong>81:</strong> Bni Khaled<br>
                                    <strong>82:</strong> Isly<br>
                                    <strong>83:</strong> Mestferki<br>
                                    <strong>84:</strong> Bsara<br>
                                    <strong>85:</strong> Sidi Boulenouar<br>
                                    <strong>86:</strong> Sidi Moussa Lemhaya
                            """
                    step = 36
                elif int(userMessage.strip()) == 8:
                    if lang == 'ar':
                        botResponse = """
                                    <span class='mb'>المرجو اختيار جماعتك:</span>
                                        <strong>87:</strong> القطيطير<br>
                                        <strong>88:</strong> أهل وادزا<br>
                                        <strong>89:</strong> ملج الويدان<br>
                                        <strong>90:</strong> عين لحجر<br>
                                        <strong>91:</strong> مشرع حمادي<br>
                                        <strong>92:</strong> مستغمر<br>
                                        <strong>93:</strong> تنشرفي<br>
                                        <strong>94:</strong> سيدي علي بلقاسم<br>
                                        <strong>95:</strong> سيدي لحسن<br>
                                        <strong>96:</strong> العطف<br>
                                        <strong>97:</strong> أولاد محمد<br>
                                    """
                    else:
                        botResponse = """
                                    <span class='mb'>Veuillez indiquer votre <strong>commune</strong> :</span>
                                    <strong>87:</strong> Oujda<br>
                                    <strong>88:</strong> Angad<br>
                                    <strong>89:</strong> Naima<br>
                                    <strong>90:</strong> Ain Sfa<br>
                                    <strong>91:</strong> Bni Khaled<br>
                                    <strong>92:</strong> Isly<br>
                                    <strong>93:</strong> Mestferki<br>
                                    <strong>94:</strong> Bsara<br>
                                    <strong>95:</strong> Sidi Boulenouar<br>
                                    <strong>96:</strong> Sidi Moussa Lemhaya<br>
                                    <strong>97:</strong> Ouled M'Hamed
                                """
                    step = 37
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 30:
            if userMessage.strip().isdigit() and 1 <= int(userMessage.strip()) <= 8:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"1-8: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                botResponse = "Veuillez sélectionner une option <strong>valide</strong> !"

        elif step == 31:
            if userMessage.strip().isdigit() and 9 <= int(userMessage.strip()) <= 28:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"9-28: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 32:
            if userMessage.strip().isdigit() and 29 <= int(userMessage.strip()) <= 39:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"29-39: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 33:
            if userMessage.strip().isdigit() and 40 <= int(userMessage.strip()) <= 49:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"40-49: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 34:
            if userMessage.strip().isdigit() and 50 <= int(userMessage.strip()) <= 60:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"50-60: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 35:
            if userMessage.strip().isdigit() and 61 <= int(userMessage.strip()) <= 75:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"61-75: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 36:
            if userMessage.strip().isdigit() and 76 <= int(userMessage.strip()) <= 86:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"76-86: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 37:
            if userMessage.strip().isdigit() and 87 <= int(userMessage.strip()) <= 97:
                request.session['commune_id_prof'] = userMessage.strip()
                print(f"87-97: {request.session.get('commune_id_prof')}")
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من عضوية التعاونية الفلاحية</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Adhésion Coop agricole</strong></span>"
                step = 559
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "الخيار الذي اخترتم <strong>غير موجود</strong>، المرجو إعادة المحاولة !"
                else:
                    ask_again = "L'option que vous avez choisie <strong>n'existe pas</strong>, veuillez réessayer !"

        elif step == 38:
            request.session['num_refe'] = userMessage.strip()
            if lang == 'ar':
                botResponse = "المرجو إدخال <strong>تاريخ شهادة التلقيح</strong> على شكل: <strong/>سنة/شهر/يوم<strong>"
            else:
                botResponse = "Veuillez indiquer la <strong>date de l'attestation de vaccination</strong> au format <strong>JJ/MM/AAAA</strong>"
            step = 39

        elif step == 39:
            if re.match(r'^(0[1-9]|1\d|2\d|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}$', userMessage.strip()):
                request.session['p_date'] = userMessage.strip()
                if lang == 'ar':
                    botResponse = "<span class='fileupload-container'>المرجو فوق الزر <img src='../static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> لتحديد ملف PDF يحتوي على <strong>نسخة من شهادة التلقيح</span></strong>"
                else:
                    botResponse = "<span class='fileupload-container'>Veuillez cliquer sur le bouton <img src='static/assisto/img/filebtn.png' class='fileupload' alt='chatbot logo'> pour sélectionner un fichier PDF contenant votre <strong>Attestation de vaccination</strong></span>"
                step = 558
                return JsonResponse({'response': botResponse, 'again': '', 'step': step, 'upload_file': True})
            else:
                if lang == 'ar':
                    ask_again = "التاريخ الذي أدخلتم <strong>غير صحيح</strong>، المرجو إدخال تاريخ على شكل: <strong/>سنة/شهر/يوم<strong>"
                else:
                    ask_again = "Veuillez indiquer une date <strong>valide</strong> au format: <strong>JJ/MM/AAAA</strong> !"

        elif step == 555:
            pass
        return JsonResponse({'response': botResponse, 'step': step, 'again': ask_again})


def index(request):
    return render(request, "assisto/index.html")


def home(request):
    return redirect('assisto')


def index_ar(request):
    return render(request, "assisto/index_ar.html")


# display the Particulier list
def particulier(request):
    # Get the value of the 'search' parameter from the GET request
    search_query = request.GET.get('search')

    # Query the Particulier model to retrieve a single instance based on the cin_num attribute matching the search_query (converted to uppercase)
    # Exclude instances where the related proofdesc and demandes have a status of False
    particulier_01 = Particulier.objects.filter(cin_num=search_query.upper()).exclude(cin_num__demandes_set__status=False).first() if search_query else None

    # If particulier_01 is None, query all instances of Particulier excluding those where the related proofdesc and demandes have a status of False
    # Order the instances by descending ID
    # If particulier_01 is not None, create a list containing only particulier_01
    particulier = Particulier.objects.exclude(cin_num__demandes_set__status=False).order_by('-id') if not particulier_01 else [particulier_01]

    # Create a Paginator object with the particulier queryset, specifying 8 objects per page
    paginator = Paginator(particulier, 8)

    # Get the current page number from the GET request
    page_number = request.GET.get('page')

    # Get the Page object for the current page number
    page_obj = paginator.get_page(page_number)

    # Render the particulier.html template with the particuliers queryset and the page_obj
    return render(request, "assisto/demandeurs/particulier.html", {
        'particuliers': particulier,
        'page_obj': page_obj
    })


def particulier_details(request, cin):
    if request.method == 'GET':
        # Retrieve a single instance of Particulier based on the cin_num attribute matching the provided cin (converted to uppercase)
        particulier = get_object_or_404(Particulier, cin_num=cin.upper())

        demande = particulier.cin_num.demandes_set.all()      
            
        # Get all related proofdesc instances for the particulier
        proof_descs = ProofDesc.objects.filter(user_proof__in=demande)

        # Iterate over the proof_descs queryset
        for proof_desc in proof_descs:
            # Retrieve specific attributes from each proof_desc instance
            num_tf = proof_desc.num_tf
            num_refe = proof_desc.num_refe
            p_date = proof_desc.p_date

            if proof_desc.duree and proof_desc.p_date:
                # Calculate the number of days between duree and p_date
                days = (proof_desc.duree - proof_desc.p_date).days
            else:
                days = None

            nom = proof_desc.nom
            nom_prenom_president = proof_desc.nom_prenom_president
            tele = proof_desc.tele
            email = proof_desc.email
            commune = proof_desc.commune
            province = None
            if commune is not None and commune.province:
                province = commune.province
            pdf_file = proof_desc.pdf_name

        # Render the details_particulier_demande.html template with the retrieved data
        return render(request, "assisto/demandeurs/details_particulier_demande.html", {
            'particulier': particulier,
            'num_tf': num_tf,
            'num_refe': num_refe,
            'p_date': p_date,
            'days': days,
            'nom': nom,
            'nom_prenom_president': nom_prenom_president,
            'tele': tele,
            'email': email,
            'province': province,
            'commune': commune,
            'pdf_file': pdf_file,
            'demande': demande
        })


def particulier_demande(request):
    search_query = request.GET.get('search')

    # Retrieve a single instance of Particulier based on the cin_num attribute matching the provided search_query (converted to uppercase)
    particulier_01 = Particulier.objects.filter(cin_num=search_query.upper()).exclude(cin_num__demandes_set__status=True).first() if search_query else None

    # Retrieve all Particulier instances that have associated proofdesc instances with a status of False
    particulier = Particulier.objects.filter(cin_num__demandes_set__status=False).order_by('-id') if not particulier_01 else [particulier_01]

    # Paginate the particulier queryset
    paginator = Paginator(particulier, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the particulier.html template with the retrieved data and a 'demande' variable set to True
    return render(request, "assisto/demandeurs/particulier.html", {
        'particuliers': particulier,
        'page_obj': page_obj,
        'demande': True,
    })


def particulier_demande_details(request, cin):
    if request.method == 'GET':

        # Retrieve the Particulier instance with the provided cin_num (converted to uppercase)
        particulier = get_object_or_404(Particulier, cin_num=cin.upper())

        demande = particulier.cin_num.demandes_set.all()
        
        # Retrieve all associated proofdesc instances for the particulier
        proof_descs = ProofDesc.objects.filter(user_proof__in=demande)

        # Loop through the proofdesc instances and assign the values to the corresponding variables
        for proof_desc in proof_descs:
            num_tf = proof_desc.num_tf
            num_refe = proof_desc.num_refe
            p_date = proof_desc.p_date

            if proof_desc.duree and proof_desc.p_date:
                days = (proof_desc.duree - proof_desc.p_date).days
            else:
                days = None

            nom = proof_desc.nom
            nom_prenom_president = proof_desc.nom_prenom_president
            tele = proof_desc.tele
            email = proof_desc.email
            commune = proof_desc.commune
            province = None
            if commune is not None and commune.province:
                province = commune.province
            pdf_file = proof_desc.pdf_name

        # Render the particulier_details.html template with the retrieved data
        return render(request, "assisto/demandes_details/particulier_details.html", {
            'particulier': particulier,
            'num_tf': num_tf,
            'num_refe': num_refe,
            'p_date': p_date,
            'days': days,
            'nom': nom,
            'nom_prenom_president': nom_prenom_president,
            'tele': tele,
            'email': email,
            'commune': commune,
            'province': province,
            'pdf_file': pdf_file
        })


def accepter_refuser_demande(request, pr, cn, st):
    if st == "accepter":
        # Accept the demande
        if pr == 'particulier':
            # Retrieve the user object associated with the particulier
            user = get_object_or_404(Users, cin_num=cn)         
            # Retrieve the demande object for a particulier
            demande = get_object_or_404(Demandes, user_demande=user)
            
            # Send an SMS notification to the user
            send_sms(user.user_tel, "Votre attestation agricole est prêt.")
            print("Votre attestation agricole est prêt.")
            # Get an optional message from the request
            message = request.GET.get('message')
            if message:
                # Send an additional SMS message if a message is provided
                send_sms(user.user_tel, message)
                print(message)
        
        elif pr == 'cooperative':
            user = get_object_or_404(Users, cnc_num=cn)
            demande = get_object_or_404(Demandes, user_demande=user)
            
            send_sms(user.user_tel, "Votre attestation agricole est prêt.")
            message = request.GET.get('message')
            if message:
                send_sms(user.user_tel, message)
                
        elif pr == 'societe':
            user = get_object_or_404(Users, rc_num=cn)
            demande = get_object_or_404(Demandes, user_demande=user)
            
            send_sms(user.user_tel, "Votre attestation agricole est prêt.")
            message = request.GET.get('message')
            if message:
                send_sms(user.user_tel, message)

        # Update the status of the demande to True (accepted)
        demande.status = True
        # Generate a unique code for the attestation
        demande.code_attestation = str(uuid.uuid4())
        demande.save()  # Save the changes to the demande object

        # Add a success message to the request
        messages.success(request, 'Demande acceptée avec succès.')

    elif st == "refuser":
        # Refuse the demande
        if pr == 'particulier':
            user = get_object_or_404(Users, cin_num=cn)
            send_sms(user.user_tel,"Votre demande de certificat agricole a été refusée.")
            message = request.GET.get('message')
            if message:
                send_sms(user.user_tel, message)
            user.delete()  # Delete the user object associated with the particulier
        elif pr == 'cooperative':
            user = get_object_or_404(Users, cnc_num=cn)
            send_sms(user.user_tel, "Votre demande de certificat agricole a été refusée.")
            message = request.GET.get('message')
            if message:
                send_sms(user.user_tel, message)
            user.delete()
        elif pr == 'societe':
            user = get_object_or_404(Users, rc_num=cn)
            send_sms(user.user_tel,"Votre demande de certificat agricole a été refusée.")
            message = request.GET.get('message')
            if message:
                send_sms(user.user_tel, message)
            user.delete()

        messages.success(request, 'Demande supprimée avec succès.')

    # Redirect to the appropriate demande page based on pr
    if pr == 'particulier':
        return redirect("/dashboard/demandes/particulier")
    elif pr == 'cooperative':
        return redirect("/dashboard/demandes/cooperative")
    elif pr == 'societe':
        return redirect("/dashboard/demandes/societe")


def cooperative(request):
    search_query = request.GET.get('search')
    cooperative_01 = Cooperative.objects.filter(cnc_num=search_query.upper()).exclude(cnc_num__demandes_set__status=False).first() if search_query else None
    cooperative = Cooperative.objects.exclude(cnc_num__demandes_set__status=False).order_by('-id') if not cooperative_01 else [cooperative_01]

    paginator = Paginator(cooperative, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "assisto/demandeurs/cooperative.html", {
        'cooperatives': cooperative,
        'page_obj': page_obj
    })


def cooperative_details(request, cnc_num):
    if request.method == 'GET':
        cooperative = get_object_or_404(Cooperative, cnc_num=cnc_num.upper())
        
        demande = cooperative.cnc_num.demandes_set.all()
        
        proof_descs = ProofDesc.objects.filter(user_proof__in=demande)
        for proof_desc in proof_descs:
            num_tf = proof_desc.num_tf
            num_refe = proof_desc.num_refe
            p_date = proof_desc.p_date

            if proof_desc.duree and proof_desc.p_date:
                days = (proof_desc.duree - proof_desc.p_date).days
            else:
                days = None

            nom = proof_desc.nom
            nom_prenom_president = proof_desc.nom_prenom_president
            tele = proof_desc.tele
            email = proof_desc.email
            commune = proof_desc.commune
            province = None
            if commune is not None and commune.province:
                province = commune.province
            pdf_file = proof_desc.pdf_name

        return render(request, "assisto/demandeurs/details_cooperative_demande.html", {
            'cooperative': cooperative,
            'num_tf': num_tf,
            'num_refe': num_refe,
            'p_date': p_date,
            'days': days,
            'nom': nom,
            'nom_prenom_president': nom_prenom_president,
            'tele': tele,
            'email': email,
            'province': province,
            'commune': commune,
            'pdf_file': pdf_file,
            'demande': demande
        })


def cooperative_demande(request):
    search_query = request.GET.get('search')
    cooperative_01 = Cooperative.objects.filter(cnc_num=search_query.upper()).exclude(cnc_num__demandes_set__status=True).first() if search_query else None
    cooperative = Cooperative.objects.filter(cnc_num__demandes_set__status=False).order_by('-id') if not cooperative_01 else [cooperative_01]

    paginator = Paginator(cooperative, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "assisto/demandeurs/cooperative.html", {
        'cooperatives': cooperative,
        'page_obj': page_obj,
        'demande': True
    })


def cooperative_demande_details(request, cnc):
    if request.method == 'GET':
        cooperative = get_object_or_404(Cooperative, cnc_num=cnc.upper())
        
        demande = cooperative.cnc_num.demandes_set.all()
        
        proof_descs = ProofDesc.objects.filter(user_proof__in=demande)

        for proof_desc in proof_descs:
            num_tf = proof_desc.num_tf
            num_refe = proof_desc.num_refe
            p_date = proof_desc.p_date

            if proof_desc.duree and proof_desc.p_date:
                days = (proof_desc.duree - proof_desc.p_date).days
            else:
                days = None

            nom = proof_desc.nom
            nom_prenom_president = proof_desc.nom_prenom_president
            tele = proof_desc.tele
            email = proof_desc.email
            commune = proof_desc.commune
            province = None
            if commune is not None and commune.province:
                province = commune.province
            pdf_file = proof_desc.pdf_name

        return render(request, "assisto/demandes_details/cooperative_details.html", {
            'cooperative': cooperative,
            'num_tf': num_tf,
            'num_refe': num_refe,
            'p_date': p_date,
            'days': days,
            'nom': nom,
            'nom_prenom_president': nom_prenom_president,
            'tele': tele,
            'email': email,
            'province': province,
            'commune': commune,
            'pdf_file': pdf_file
        })


def societe(request):
    search_query = request.GET.get('search')
    societe_01 = Societe.objects.filter(rc_num=search_query.upper()).exclude(rc_num__demandes_set__status=False).first() if search_query else None
    societe = Societe.objects.exclude(rc_num__demandes_set__status=False).order_by('-id') if not societe_01 else [societe_01]

    paginator = Paginator(societe, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "assisto/demandeurs/societe.html", {
        'societes': societe,
        'page_obj': page_obj
    })


def societe_details(request, rc_num):
    if request.method == 'GET':
        societe = get_object_or_404(Societe, rc_num=rc_num.upper())
        demande = societe.rc_num.demandes_set.all()
        proof_descs = ProofDesc.objects.filter(user_proof__in=demande)
        for proof_desc in proof_descs:
            num_tf = proof_desc.num_tf
            num_refe = proof_desc.num_refe
            p_date = proof_desc.p_date

            if proof_desc.duree and proof_desc.p_date:
                days = (proof_desc.duree - proof_desc.p_date).days
            else:
                days = None

            nom = proof_desc.nom
            nom_prenom_president = proof_desc.nom_prenom_president
            tele = proof_desc.tele
            email = proof_desc.email
            commune = proof_desc.commune
            province = None
            if commune is not None and commune.province:
                province = commune.province
            pdf_file = proof_desc.pdf_name

        return render(request, "assisto/demandeurs/details_societe_demande.html", {
            'societe': societe,
            'num_tf': num_tf,
            'num_refe': num_refe,
            'p_date': p_date,
            'days': days,
            'nom': nom,
            'nom_prenom_president': nom_prenom_president,
            'tele': tele,
            'email': email,
            'province': province,
            'commune': commune,
            'pdf_file': pdf_file,
            'demande': demande
        })


def societe_demande(request):
    search_query = request.GET.get('search')
    societe_01 = Societe.objects.filter(rc_num=search_query.upper()).exclude(rc_num__demandes_set__status=True).first() if search_query else None
    societe = Societe.objects.filter(rc_num__demandes_set__status=False).order_by('-id') if not societe_01 else [societe_01]

    paginator = Paginator(societe, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "assisto/demandeurs/societe.html", {
        'societes': societe,
        'page_obj': page_obj,
        'demande': True
    })


def societe_demande_details(request, rc_num):
    if request.method == 'GET':
        societe = get_object_or_404(Societe, rc_num=rc_num.upper())
        
        demande = societe.rc_num.demandes_set.all()
        
        proof_descs = ProofDesc.objects.filter(user_proof__in=demande)
        for proof_desc in proof_descs:
            num_tf = proof_desc.num_tf
            num_refe = proof_desc.num_refe
            p_date = proof_desc.p_date

            if proof_desc.duree and proof_desc.p_date:
                days = (proof_desc.duree - proof_desc.p_date).days
            else:
                days = None

            nom = proof_desc.nom
            nom_prenom_president = proof_desc.nom_prenom_president
            tele = proof_desc.tele
            email = proof_desc.email            
            commune = proof_desc.commune
            province = None
            if commune is not None and commune.province:
                province = commune.province
            pdf_file = proof_desc.pdf_name

        return render(request, "assisto/demandes_details/societe_details.html", {
            'societe': societe,
            'num_tf': num_tf,
            'num_refe': num_refe,
            'p_date': p_date,
            'days': days,
            'nom': nom,
            'nom_prenom_president': nom_prenom_president,
            'tele': tele,
            'email': email,
            'province': province,
            'commune': commune,
            'pdf_file': pdf_file
        })


def attestation(request, cn, pr):
    # Generate attestation for particulier
    if pr == 'particulier':
        # Retrieve the particulier object
        particulier = get_object_or_404(Particulier, cin_num=cn.upper())
        # Retrieve the demande object
        demande = particulier.cin_num.demandes_set.get(user_demande=Users.objects.get(cin_num=cn.upper())) 

        att_code = demande.code_attestation  # Get the attestation code from the demande

        # generate a QR code using the qrcode library
        qr = qrcode.QRCode(
            version=1,  # the size and data capacity of the QR code
            # the error correction level for the QR code. ERROR_CORRECT_L stands for 7% error correction
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            # the size of each box (pixel) in the QR code. In this case, it's set to 10
            box_size=10,
            border=4,  # the width of the white border around the QR code. In this case, it's set to 4
        )
        # add the data (in this case, the att_code) to the QR code
        qr.add_data(att_code)
        # generate the QR code based on the added data (the fit parameter, when set to True, adjusts the QR code to fit the data more efficiently)
        qr.make(fit=True)

        # Create a BytesIO object to store the image data
        qr_image_buffer = BytesIO()
        # Generate the QR code image with specified fill color and background color
        qr_image = qr.make_image(fill_color="black", back_color="white")
        # Save the QR code image to the BytesIO buffer
        qr_image.save(qr_image_buffer)
        # Reset the stream position to the beginning
        qr_image_buffer.seek(0)

        return render(request, "assisto/attestation.html", {
            'particulier': particulier,
            'current_date': timezone.now(),
            'att_code': att_code,
            'qr_image_buffer': qr_image_buffer.getvalue(),
        })

    elif pr == 'cooperative':
        cooperative = get_object_or_404(Cooperative, cnc_num=cn.upper())
        demande = cooperative.cnc_num.demandes_set.get(user_demande=Users.objects.get(cnc_num=cn.upper())) 

        att_code = demande.code_attestation

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(att_code)
        qr.make(fit=True)

        # Create a BytesIO object to store the image data
        qr_image_buffer = BytesIO()
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(qr_image_buffer)
        qr_image_buffer.seek(0)

        return render(request, "assisto/attestation.html", {
            'cooperative': cooperative,
            'current_date': timezone.now(),
            'att_code': att_code,
            'qr_image_buffer': qr_image_buffer.getvalue(),
        })
    elif pr == 'societe':
        societe = get_object_or_404(Societe, rc_num=cn.upper())
        demande = societe.rc_num.demandes_set.get(user_demande=Users.objects.get(rc_num=cn.upper())) 

        att_code = demande.code_attestation

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(att_code)
        qr.make(fit=True)

        # Create a BytesIO object to store the image data
        qr_image_buffer = BytesIO()
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(qr_image_buffer)
        qr_image_buffer.seek(0)

        return render(request, "assisto/attestation.html", {
            'societe': societe,
            'current_date': timezone.now(),
            'att_code': att_code,
            'qr_image_buffer': qr_image_buffer.getvalue(),
        })


def logout(request):
    # Retrieve the user based on the email address stored in the session
    user = Acc_User.objects.get(email_address=request.session['email_address'])

    # Update the last login time for the user
    user.last_login = datetime.now()
    user.save()

    # Remove the stored session data for email address, first name, and last name
    del request.session['email_address']
    del request.session['first_name']
    del request.session['last_name']

    # Redirect the user to the login page
    return HttpResponseRedirect("/login")


def login(request):
    if request.method == 'GET':
        # Check if the user is already logged in
        if 'email_address' in request.session:
            return HttpResponseRedirect("/dashboard")
        else:
            return render(request, "assisto/login.html")

    elif request.method == 'POST':
        # Retrieve the email and password from the POST request
        email_address = request.POST.get('email')
        pwd = request.POST.get('password')

        # Check if a user with the provided email and password exists
        user = Acc_User.objects.filter(
            email_address=email_address, password=pwd).exists()
        if user:
            # Retrieve the logged-in user
            logged_user = Acc_User.objects.get(email_address=email_address)
            if logged_user.is_active:
                # Store the email address, first name, and last name in the session
                request.session['email_address'] = email_address
                request.session['first_name'] = str(logged_user.first_name)
                request.session['last_name'] = str(logged_user.last_name)

                # Redirect the user to the dashboard
                return HttpResponseRedirect("/dashboard")
            else:
                return render(request, "assisto/login.html", {
                    "error": True,
                    "ds_msg": "Votre compte a été désactivé !"
                })
        else:
            return render(request, "assisto/login.html", {
                "info": True,
                "ds_msg": "L'adresse e-mail ou le mot de passe que vous avez saisi n'est pas correct !"
            })


def dashboard(request):
    if request.method == 'GET':
        if 'email_address' in request.session:
            return render(request, "assisto/dashboard.html")
        else:
            return HttpResponseRedirect("/login")
    return render(request, "assisto/dashboard.html")


def send_sms(phone_number, msg):
    BASE_URL = "xrzylg.api.infobip.com"
    API_KEY = os.environ.get('API_KEY')
    SENDER = os.environ.get('SENDER')
    RECIPIENT = "212" + phone_number[1:]

    conn = http.client.HTTPSConnection(BASE_URL)

    payload1 = {
        "messages": [
            {
                "from": SENDER,
                "destinations": [
                    {"to": RECIPIENT}
                ],
                "text": msg
            }
        ]
    }

    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    conn.request("POST", "/sms/2/text/advanced", json.dumps(payload1), headers)
    res = conn.getresponse()
    data = res.read()
    # print(data.decode("utf-8"))
