from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser


# Custom registration form with Tailwind-styled widgets
class CustomUserCreationForm(UserCreationForm):
    # Extra email field (not included in default UserCreationForm)
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
        'placeholder': 'Enter your email'
    }))

    class Meta:
        model = CustomUser
        # Fields shown on the registration form
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
                    'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent Tailwind styling to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500',
            'placeholder': 'Confirm your password'
        })
