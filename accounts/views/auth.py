from django.contrib.auth import views as auth_views
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.shortcuts import redirect
from accounts.models import Psychologist
from accounts.forms.auth import PsychologistRegistrationForm

class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'

class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return redirect(self.next_page)

class RegisterView(CreateView):
    model = Psychologist
    form_class = PsychologistRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')