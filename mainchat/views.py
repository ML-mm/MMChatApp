from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from .models import Room
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView


def home(request):
    rooms = Room.objects.all()
    return render(request, "mainchat/index.html", {'rooms': rooms, })


def room_view(request, room_name):
    chat_room, created = Room.objects.get_or_create(name=room_name)
    # staff_room, created = Room.objects.get_or_create(name=room_name, only_staff=True)
    return render(request, 'mainchat/room.html', {'room': chat_room})


class UserRegisterView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    template_name = "mainchat/register.html"
    success_url = reverse_lazy('mainchat:home')
    success_message = "Congrats, you successfully signed up, feel free to use the chat rooms available to you."


class LoginUserView(SuccessMessageMixin, LoginView):
    success_message = "Logged in successfully"
    extra_context = dict(success_url=reverse_lazy('mainchat:home'))



