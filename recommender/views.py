from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistrationForm, StudentProfileForm
from .models import RecommendationHistory, StudentProfile
from .recommendation_engine import (
    generate_programme_recommendations,
    generate_resource_recommendations,
    get_recommendation_summary,
)


def landing_page(request):
    return render(request, 'recommender/landing.html')


def about_page(request):
    return render(request, 'recommender/about.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            StudentProfile.objects.get_or_create(user=user)
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
            messages.success(request, 'Registration successful. Please complete your profile.')
            return redirect('profile_setup')
    else:
        form = RegistrationForm()
    return render(request, 'recommender/register.html', {'form': form})


def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'recommender/login.html', {'next': next_url, 'username': request.POST.get('username', '')})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


@login_required
def profile_setup(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()
            profile.update_profile_completion()
            profile.save()
            messages.success(request, 'Your profile was updated successfully.')
            return redirect('dashboard')
    else:
        form = StudentProfileForm(instance=profile)
    return render(request, 'recommender/profile_form.html', {'form': form, 'profile': profile})


@login_required
def profile_management(request):
    return profile_setup(request)


@login_required
def dashboard(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    summary = get_recommendation_summary(profile)
    programme_recommendations = generate_programme_recommendations(profile, limit=3)
    resource_recommendations = generate_resource_recommendations(profile, limit=3)
    history = RecommendationHistory.objects.filter(student=profile)[:5]
    return render(
        request,
        'recommender/dashboard.html',
        {
            'profile': profile,
            'summary': summary,
            'programme_recommendations': programme_recommendations,
            'resource_recommendations': resource_recommendations,
            'history': history,
        },
    )


@login_required
def generate_recommendations(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    programmes = generate_programme_recommendations(profile)
    resources = generate_resource_recommendations(profile)

    RecommendationHistory.objects.filter(student=profile, recommendation_type='programme').delete()
    RecommendationHistory.objects.filter(student=profile, recommendation_type='resource').delete()

    for item in programmes:
        RecommendationHistory.objects.create(
            student=profile,
            recommendation_type='programme',
            recommendation_data={
                'programme_id': item['programme'].id,
                'programme_name': item['programme'].name,
                'score': item['score'],
                'explanation': item['explanation'],
            },
        )

    for item in resources:
        RecommendationHistory.objects.create(
            student=profile,
            recommendation_type='resource',
            recommendation_data={
                'resource_id': item['resource'].id,
                'resource_title': item['resource'].title,
                'score': item['score'],
                'explanation': item['explanation'],
            },
        )

    messages.success(request, 'Fresh recommendations have been generated and saved.')
    return redirect('dashboard')


@login_required
def programme_recommendations(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    history_items = RecommendationHistory.objects.filter(student=profile, recommendation_type='programme')
    entries = []
    if history_items:
        for item in history_items:
            data = item.recommendation_data
            entries.append({
                'programme_id': data.get('programme_id'),
                'programme_name': data.get('programme_name'),
                'score': data.get('score'),
                'explanation': data.get('explanation'),
            })
    else:
        for item in generate_programme_recommendations(profile):
            entries.append({
                'programme_id': item['programme'].id,
                'programme_name': item['programme'].name,
                'score': item['score'],
                'explanation': item['explanation'],
            })
    return render(request, 'recommender/recommendations.html', {'recommendations': entries, 'kind': 'programmes'})


@login_required
def resource_recommendations(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    history_items = RecommendationHistory.objects.filter(student=profile, recommendation_type='resource')
    entries = []
    if history_items:
        for item in history_items:
            data = item.recommendation_data
            entries.append({
                'resource_id': data.get('resource_id'),
                'resource_title': data.get('resource_title'),
                'score': data.get('score'),
                'explanation': data.get('explanation'),
            })
    else:
        for item in generate_resource_recommendations(profile):
            entries.append({
                'resource_id': item['resource'].id,
                'resource_title': item['resource'].title,
                'score': item['score'],
                'explanation': item['explanation'],
            })
    return render(request, 'recommender/recommendations.html', {'recommendations': entries, 'kind': 'resources'})


@login_required
def programme_detail(request, pk):
    from .models import AcademicProgramme

    programme = AcademicProgramme.objects.get(pk=pk)
    return render(request, 'recommender/programme_detail.html', {'programme': programme})


@login_required
def resource_detail(request, pk):
    from .models import LearningResource

    resource = LearningResource.objects.get(pk=pk)
    return render(request, 'recommender/resource_detail.html', {'resource': resource})
