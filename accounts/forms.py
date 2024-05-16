
# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm

from .models import SubscriptionPlan

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'address', 'phone_number']

class SubscriptionForm(forms.Form):
    plan = forms.ModelChoiceField(queryset=SubscriptionPlan.objects.all())

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address.")
        return email

    def save(self, domain_override=None, use_https=False, request=None, **kwargs):
        email = self.cleaned_data["email"]
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        for user in active_users:
            context = {
                'request': request,
                'user': user,
                'domain': domain_override,
                'protocol': 'https' if use_https else 'http',
            }
            self.send_mail(
                subject_template_name='registration/password_reset_subject.txt',
                email_template_name='registration/password_reset_email.html',
                context=context,
                from_email=None,
                to_email=user.email,
                html_email_template_name=None,
            )
