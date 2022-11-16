from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum, Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(to_email, subject, message):
    # message = Mail(
    #     from_email='email@mail.com',
    #     to_emails=to_email,
    #     subject=subject,
    #     html_content=message)
    # try:
    #     sg = SendGridAPIClient('<SENDGRID_API_KEY>')
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    #     print(response.headers)
    # except Exception as e:
    #     print(e)
    message = Mail(
        from_email='sabari.h.dev@gmail.com',
        to_emails=to_email,
        subject=subject,
        html_content=message)
    try:
        sg = SendGridAPIClient(
            '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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


def home_view(request):
    x = models.Stock.objects.all()
    print(x)
    if len(x) == 0:
        blood1 = models.Stock()
        blood1.bloodgroup = "A+"
        blood1.save()

        blood2 = models.Stock()
        blood2.bloodgroup = "A-"
        blood2.save()

        blood3 = models.Stock()
        blood3.bloodgroup = "B+"
        blood3.save()

        blood4 = models.Stock()
        blood4.bloodgroup = "B-"
        blood4.save()

        blood5 = models.Stock()
        blood5.bloodgroup = "AB+"
        blood5.save()

        blood6 = models.Stock()
        blood6.bloodgroup = "AB-"
        blood6.save()

        blood7 = models.Stock()
        blood7.bloodgroup = "O+"
        blood7.save()

        blood8 = models.Stock()
        blood8.bloodgroup = "O-"
        blood8.save()

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'blood/index.html')


def is_donor(user):
    return user.groups.filter(name='DONOR').exists()


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    if is_donor(request.user):
        return redirect('donor/donor-dashboard')

    elif is_patient(request.user):
        return redirect('patient/patient-dashboard')
    else:
        return redirect('admin-dashboard')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    totalunit = models.Stock.objects.aggregate(Sum('unit'))
    dict = {

        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
        'totaldonors': dmodels.Donor.objects.all().count(),
        'totalbloodunit': totalunit['unit__sum'],
        'totalrequest': models.BloodRequest.objects.all().count(),
        'totalapprovedrequest': models.BloodRequest.objects.all().filter(status='Approved').count()
    }
    return render(request, 'blood/admin_dashboard.html', context=dict)


@login_required(login_url='adminlogin')
def admin_blood_view(request):
    dict = {
        'bloodForm': forms.BloodForm(),
        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
    }
    if request.method == 'POST':
        bloodForm = forms.BloodForm(request.POST)
        if bloodForm.is_valid():
            bloodgroup = bloodForm.cleaned_data['bloodgroup']
            stock = models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit = bloodForm.cleaned_data['unit']
            stock.save()
        return HttpResponseRedirect('admin-blood')
    return render(request, 'blood/admin_blood.html', context=dict)


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    donors = dmodels.Donor.objects.all()
    return render(request, 'blood/admin_donor.html', {'donors': donors})


@login_required(login_url='adminlogin')
def update_donor_view(request, pk):
    donor = dmodels.Donor.objects.get(id=pk)
    user = dmodels.User.objects.get(id=donor.user_id)
    userForm = dforms.DonorUserForm(instance=user)
    donorForm = dforms.DonorForm(request.FILES, instance=donor)
    mydict = {'userForm': userForm, 'donorForm': donorForm}
    if request.method == 'POST':
        userForm = dforms.DonorUserForm(request.POST, instance=user)
        donorForm = dforms.DonorForm(
            request.POST, request.FILES, instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            donor = donorForm.save(commit=False)
            donor.user = user
            donor.bloodgroup = donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request, 'blood/update_donor.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request, pk):
    donor = dmodels.Donor.objects.get(id=pk)
    user = User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return HttpResponseRedirect('/admin-donor')


@login_required(login_url='adminlogin')
def admin_patient_view(request):
    patients = pmodels.Patient.objects.all()
    return render(request, 'blood/admin_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
def update_patient_view(request, pk):
    patient = pmodels.Patient.objects.get(id=pk)
    user = pmodels.User.objects.get(id=patient.user_id)
    userForm = pforms.PatientUserForm(instance=user)
    patientForm = pforms.PatientForm(request.FILES, instance=patient)
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = pforms.PatientUserForm(request.POST, instance=user)
        patientForm = pforms.PatientForm(
            request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.bloodgroup = patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request, 'blood/update_patient.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request, pk):
    patient = pmodels.Patient.objects.get(id=pk)
    user = User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return HttpResponseRedirect('/admin-patient')


@login_required(login_url='adminlogin')
def admin_request_view(request):
    requests = models.BloodRequest.objects.all().filter(status='Pending')
    return render(request, 'blood/admin_request.html', {'requests': requests})


@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    requests = models.BloodRequest.objects.all().exclude(status='Pending')
    return render(request, 'blood/admin_request_history.html', {'requests': requests})


@login_required(login_url='adminlogin')
def admin_donation_view(request):
    donations = dmodels.BloodDonate.objects.all()
    return render(request, 'blood/admin_donation.html', {'donations': donations})


@login_required(login_url='adminlogin')
def update_approve_status_view(request, pk):
    req = models.BloodRequest.objects.get(id=pk)
    message = None
    bloodgroup = req.bloodgroup
    unit = req.unit
    stock = models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit > unit:
        stock.unit = stock.unit-unit
        stock.save()
        req.status = "Approved"
        # TODO: send email to patient about approved request
        if (req.request_by_donor != None):
            print(req.request_by_donor.user.username)
            send_email(req.request_by_donor.user.username, "Blood Request Approved",
                       "Your blood request has been approved")
        else:
            print(req.request_by_patient.user.username)
            send_email(req.request_by_patient.user.username, "Blood Request Approved",
                       "Your blood request has been approved")
        # send_email(req.patient.user.email, "Blood Request Approved",
        #            "Your blood request has been approved")
    else:
        message = "Stock Doest Not Have Enough Blood To Approve This Request, Only " + \
            str(stock.unit)+" Unit Available"
    req.save()

    requests = models.BloodRequest.objects.all().filter(status='Pending')
    return render(request, 'blood/admin_request.html', {'requests': requests, 'message': message})


@ login_required(login_url='adminlogin')
def update_reject_status_view(request, pk):
    req = models.BloodRequest.objects.get(id=pk)
    req.status = "Rejected"
    req.save()
    # TODO: send email to patient about rejected request
    if (req.request_by_donor != None):
        print(req.request_by_donor.user.username)
        send_email(req.request_by_donor.user.username, "Blood Request Rejected",
                   "Your blood request has been rejected")
    else:
        print(req.request_by_patient.user.username)
        send_email(req.request_by_patient.user.username, "Blood Request Rejected",
                   "Your blood request has been rejected")
    return HttpResponseRedirect('/admin-request')


@ login_required(login_url='adminlogin')
def approve_donation_view(request, pk):
    donation = dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group = donation.bloodgroup
    donation_blood_unit = donation.unit

    stock = models.Stock.objects.get(bloodgroup=donation_blood_group)
    stock.unit = stock.unit+donation_blood_unit
    stock.save()

    donation.status = 'Approved'
    donation.save()

    # TODO: send email to donor about approved donation
    send_email(donation.donor.user.username, "Blood Donation Approved",
               "Your Blood Donation Has Been Approved")
    return HttpResponseRedirect('/admin-donation')


@ login_required(login_url='adminlogin')
def reject_donation_view(request, pk):
    donation = dmodels.BloodDonate.objects.get(id=pk)
    donation.status = 'Rejected'
    donation.save()

    # TODO: send email to donor about rejected donation
    send_email(donation.donor.user.username, "Blood Donation Rejected",
               "Your Blood Donation Has Been Rejected")

    return HttpResponseRedirect('/admin-donation')
