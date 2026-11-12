from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import StudentInterest, StudentProfile


class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username', 'autocapitalize': 'none'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}))
    password1 = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Confirm password', strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class StudentProfileForm(forms.ModelForm):
    areas_of_interest = forms.ModelMultipleChoiceField(
        queryset=StudentInterest.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = StudentProfile
        fields = [
            'full_name',
            'age',
            'highest_qualification',
            'academic_background',
            'previous_institution',
            'academic_subjects',
            'subject_grades',
            'areas_of_interest',
            'preferred_fields',
            'career_interests',
            'learning_style',
            'study_mode',
            'academic_goals',
        ]
        widgets = {
            'academic_background': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'previous_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_subjects': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_grades': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_fields': forms.TextInput(attrs={'class': 'form-control'}),
            'career_interests': forms.TextInput(attrs={'class': 'form-control'}),
            'learning_style': forms.TextInput(attrs={'class': 'form-control'}),
            'study_mode': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'highest_qualification': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '')
        if len(full_name.strip()) < 2:
            raise forms.ValidationError('Enter a valid full name.')
        return full_name

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and age < 10:
            raise forms.ValidationError('Age must be 10 or greater.')
        return age
