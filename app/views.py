import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Message, Colab


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # List all users for chatting. Except myself.
        context['users'] = User.objects.exclude(id=self.request.user.id) \
            .values('username')
        return context


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat.html'

    def dispatch(self, request, **kwargs):
        # Get the person we are chatting with, if not exist raise 404.
        receiver_username = kwargs['chatname'].replace(
            request.user.username, '').replace('-', '')
        kwargs['receiver'] = get_object_or_404(User, username=receiver_username)
        return super().dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receiver'] = kwargs['receiver']
        context['positive'] = Message.objects.filter(sender=self.request.user.id,
                                                     receiver__username=kwargs['receiver'], status=1).count()
        context['negative'] = Message.objects.filter(sender=self.request.user.id,
                                                     receiver__username=kwargs['receiver'], status=0).count()

        return context


class MessagesAPIView(View):

    def get(self, request, chatname):
        # Grab two users based on the chat name.
        users = User.objects.filter(username__in=chatname.split('-'))
        # Filters messages between this two users.
        result = Message.objects.filter(
            Q(sender=users[0], receiver=users[1]) | Q(sender=users[1], receiver=users[0])
        ).annotate(
            username=F('sender__username'), message=F('text'),
        ).order_by('date_created').values('username', 'message', 'date_created', 'status')

        return JsonResponse(list(result), safe=False)


# Register a new account
@csrf_exempt
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return render(request=request, template_name="registration/login.html")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


# To find the status of the message text from colab API
def analyze(texts):
    return 1
    # colab = Colab.objects.first()
    # url = f"{colab}{texts}"
    # status = requests.get(url)
    # result = status.json()
    # return result['message'][0]
