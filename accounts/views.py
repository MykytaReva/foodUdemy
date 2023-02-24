from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from .forms import UserForm
from .models import User, UserProfile

from vendor.models import Vendor
from vendor.forms import VendorForm



def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # using the form
            # password = form.cleaned_data['password']
            # print(form.cleaned_data)
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # form.save()

            # create user using method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password
            )
            user.role = User.CUSTOMER
            user.save()

            messages.success(request, 'Account created, check your inbox for the activation email.')

            return redirect('registerUser')
        else:
            print('Invalid form:')
            print(form.errors)
    else:
        form = UserForm()
    # form = UserForm()
    # form.save()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context=context)


def registerVendor(request):
    if request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password
            )
            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            # vendor.vendor_name = form.cleaned_data['vendor_name']
            # vendor.vendor_license = form.cleaned_data['vendor_license']

            vendor.save()
            messages.success(request, 'Your account has been created successfully! Please wait for the approval')
            return redirect('home')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'accounts/registerVendor.html', context=context)