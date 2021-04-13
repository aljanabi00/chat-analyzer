from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.base import TemplateView

from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.text import Tokenizer
import tensorflow

from .models import Message


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # List all users for chatting. Except myself.
        context['users'] = User.objects.exclude(id=self.request.user.id)\
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


# To find the status of the message text
def analyze(texts):
    model = tensorflow.keras.models.load_model('save.hdf5')
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(texts)
    X = tokenizer.texts_to_sequences(texts)
    sms_proc = pad_sequences(X, maxlen=50, padding='post')
    pred = model.predict(sms_proc)
    pred = pred.reshape([-1, 1, 1])
    pred = (pred > 0.5).astype("int32")
    return pred[0]
