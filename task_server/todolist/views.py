import hashlib
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token

from .models import Task, Tasklist, Tag, UserProfile
from .permissions import IsOwnerOrDeny
from .serializers import TaskSerializer, TasklistSerializer, TagSerializer, UserSerializer

USE_MAIL_ACT = False


def confirm_user(request, act_key):
    try:
        user_profile = UserProfile.objects.get(activation_key=act_key)
    except:
        return HttpResponse("Invalid activation key", status=403)
    user = user_profile.user
    user.is_active = True
    user.save()
    return HttpResponse("User successfully activated")


def register_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    try:
        User._default_manager.get(email=email)
        return JsonResponse({"detail": "Email already in use"},
                            status=403)
    except:
        pass
    try:
        user = User.objects.create_user(username, email, password)
    except:
        return JsonResponse({"detail": "User already exists"},
                            status=403)
    foo = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
    act_key = hashlib.sha1((foo + email).encode('utf-8')).hexdigest()
    new_profile = UserProfile(user=user, activation_key=act_key)
    new_profile.save()
    email_subject = "Confirm your registration"
    email_body = "To activate your account, click this link \
                 http://127.0.0.1:8080/confirm/{}".format(act_key)
    if USE_MAIL_ACT:
        send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [email])
        user.is_active = False
    Token.objects.create(user=user)
    user.save()
    return JsonResponse({"detail": "Account created, confirm it by opening link on email"})


class UserView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.id != 29:
            raise PermissionDenied()
        return queryset


class TagCreateView(generics.ListCreateAPIView):
    serializer_class = TagSerializer

    def get_queryset(self):
        queryset = Tag.objects.all()
        task_id = self.kwargs.get('pk', None)
        if task_id is not None:
            queryset = queryset.filter(task=task_id)
        return queryset

    def perform_create(self, serializer):
        task_id = self.kwargs.get('pk', None)
        task = get_object_or_404(Task, pk=task_id)
        serializer.save(task=[task, ])


class TasklistSharedView(generics.ListAPIView):
    serializer_class = TasklistSerializer

    def get_queryset(self):
        queryset = Tasklist.objects.all()
        queryset = queryset.filter(shared=self.request.user)
        return queryset


class TasklistSharedDetailsView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('pk', None)
        if list_id is not None:
            tasklist = Tasklist.objects.get(pk=list_id)
            if self.request.user not in tasklist.shared.all():
                raise PermissionDenied()
            queryset = queryset.filter(tasklist_id=list_id)
        return queryset


class TasklistCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrDeny)
    serializer_class = TasklistSerializer

    def get_queryset(self):
        queryset = Tasklist.objects.all()
        queryset = queryset.filter(owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TasklistDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrDeny)
    queryset = Tasklist.objects.all()
    serializer_class = TasklistSerializer


class TaskCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrDeny)  # ???

    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            tasklist = get_object_or_404(Tasklist, pk=list_id)
            if tasklist.owner != self.request.user:
                # return JsonResponse({"detail": 'You are not owner of this list'}, status=403)
                raise PermissionDenied()
            queryset = queryset.filter(tasklist_id=list_id)
        return queryset

    def perform_create(self, serializer):
        list_id = self.kwargs.get('list_id', None)
        tasklist = get_object_or_404(Tasklist, pk=list_id)
        if tasklist.owner != self.request.user:
            raise PermissionDenied()
        serializer.save(tasklist=tasklist)


class TaskDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrDeny)

    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            queryset = queryset.filter(tasklist_id=list_id)
        return queryset
