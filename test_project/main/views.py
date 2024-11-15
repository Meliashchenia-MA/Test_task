from pathlib import Path
from sqlite3 import IntegrityError
from time import sleep

from PIL import Image
from django.contrib.auth import authenticate, login as user_login, logout
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import os

from .models import User
from .forms import UserProfileForm, UploadModel, UploadForm

import logging

from .model.vision_model import process_image

from django.conf import settings
from django.urls import reverse

logger = logging.getLogger('all')

MODEL_PATH = 'main/model/simple_cnn.pth'

BASE_DIR = Path(__file__).resolve().parent.parent

def home_view(request):
    return render(request, 'main/home.html')


def login_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        usr = authenticate(request, username=login, password=password)
        if usr is not None:
            user_login(request, usr)
            logger.info(f'User {login}logged in')
            return HttpResponseRedirect('/profile')
        else:
            logger.error(f'Error while logging')
            return render(request, template_name='registration/login.html')

    else:
        return render(request, template_name='registration/login.html')


def reg_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        password_c = request.POST.get('password_c')
        email = request.POST.get('email')
        if password == password_c:
            if not User.objects.filter(username=login).exists():
                user = User.objects.create_user(username=login, password=password, email=email)
                user.save()

                usr = authenticate(request, username=login, password=password)
                logger.info(f'User {login} registered and logged in')
                if usr is not None:
                    user_login(request, usr)
                    return HttpResponseRedirect('/')
            else:
                logger.error(f'User {login} already exists')
                return render(request, 'registration/reg.html', {'error': 'User already exists'})
        else:
            logger.error(f'Passwords do not match')
            return render(request, 'registration/reg.html', {'error': 'Passwords do not match'})

    return render(request, 'registration/reg.html')


@login_required(login_url='/login')
def profile_view(request):
    try:
        user = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        logger.error(f'User does not exists')
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            new_username = form.cleaned_data.get('username')
            if User.objects.filter(username=new_username).exclude(username=request.user.username).exists():
                logger.error(f'There is a user with username {new_username}')
                form.add_error('username', 'There is a user with such username')
            else:
                user.username = new_username
                user.email = form.cleaned_data.get('email')
                user.bio = form.cleaned_data.get('bio')
                user.save()
                logger.info(f'User info was changed')
                return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'main/profile.html', {'form': form, 'user': user})

def logout_view(request):
    logout(request)
    logger.info(f'User logged out')
    return HttpResponseRedirect('/login')


@login_required(login_url='/login')
def upload_file(request):
    new_image_path = None
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save(commit=False)
            upload_instance.user = request.user

            uploaded_file = request.FILES['original_image']
            image_name = uploaded_file.name
            image_path = os.path.join('media', 'images', image_name)
            new_image_path = image_path.split(".")[0] + "_labeled." + image_path.split(".")[-1]

            with open(image_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)


            process_image(MODEL_PATH, image_path)
            image_path = os.path.join('images', image_name)
            new_image_path = image_path.split(".")[0] + "_labeled." + image_path.split(".")[-1]
            upload_instance.processed_image = new_image_path
            upload_instance.save()
            request.user.request_count += 1
            request.user.save()
            return redirect(reverse('display_image', args=[upload_instance.id]))
    else:
        form = UploadForm()
    return render(request, 'main/upload.html', {'form': form})


def download_image(request, id, format):
    obj = UploadModel.objects.get(id=id)
    filename = obj.processed_image.path

    valid_formats = ['jpeg', 'png', 'pdf']
    if format not in valid_formats:
        raise Http404("Format not supported")

    with Image.open(filename) as img:
        converted_filename = f"{os.path.splitext(filename)[0]}.{format}"
        img.save(converted_filename, format.upper())

    # Serve the converted image
    response = FileResponse(open(converted_filename, 'rb'), content_type=f'image/{format}')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(converted_filename)}"'
    return response

def display_image(request, id):
    upload_instance = UploadModel.objects.get(id=id)
    processed_image = upload_instance.processed_image
    return render(request, 'main/display_image.html', {'id': id, 'processed_image': processed_image})





