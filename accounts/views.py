from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, SubscriptionForm, CustomPasswordResetForm
from .models import UserSubscription
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from .models import SubscriptionPlan  # Import the SubscriptionPlan model
from django.utils import timezone
from .models import UserProfile, SubscriptionPlan, UserSubscription
from django.db import IntegrityError
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.http import HttpResponse
from django.urls import reverse



def home(request):
    return render(request, 'index.html')

def details(request):
    return render(request, 'details.html')

def pay(request):
    return render(request, 'pay.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

def buckets(request):
    return render(request, 'buckets.html')

def carts(request):
    return render(request, 'carts.html')

def legal(request):
    return render(request, 'legal.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Create or update user profile
                UserProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'address': form.cleaned_data.get('address'),
                        'phone_number': form.cleaned_data.get('phone_number')
                    }
                )
                # Authentication and login logic here
                return redirect('login')
            except IntegrityError:
                # Handle case where user profile already exists
                # You may want to display an error message or handle this differently
                return HttpResponse("User profile already exists")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    user_subscriptions = UserSubscription.objects.filter(user=user)
    today = timezone.now().date()  # Get the current date
    for subscription in user_subscriptions:
        remaining_days = (subscription.end_date - today).days
        subscription.remaining_days = remaining_days
    return render(request, 'dashboard.html', {'user_subscriptions': user_subscriptions})

@login_required
def subscribe(request):
    user = request.user
    # Check if the user already has an active subscription
    if UserSubscription.objects.filter(user=user, status='Active').exists():
        messages.warning(request, 'You already have an active subscription.')
        return redirect('dashboard')

    if request.method == 'POST':
        subscription_plan_name = request.POST.get('subscription_plan')
        try:
            subscription_plan = SubscriptionPlan.objects.get(name=subscription_plan_name)
            # Save subscription to user's profile
            user_profile = UserProfile.objects.get(user=user)
            user_profile.subscription_plan = subscription_plan
            user_profile.save()

            # Create new user subscription
            UserSubscription.objects.create(
                user=user,
                plan=subscription_plan,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=30),  # Assuming one month duration
                status='Active'  # Set status to Active
            )
            messages.success(request, 'Subscription plan updated successfully!')
            return redirect('dashboard')
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Invalid subscription plan!')
            return redirect('subscribe')
    else:
        return render(request, 'subscribe.html')





class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    email_template_name = 'registration/password_reset_email.html'
    success_url = '/password_reset/done/'

def custom_logout(request):
    logout(request)
    return redirect(reverse('home'))
