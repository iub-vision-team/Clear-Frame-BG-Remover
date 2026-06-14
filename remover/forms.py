from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
import os


class ImageUploadForm(forms.Form):
    """
    Form for uploading an image for background removal.
    Validates file type (JPG/PNG) and file size (max 5MB).
    """
    image = forms.ImageField(
        label='Select Image',
        help_text='Allowed formats: JPG, PNG. Maximum size: 5 MB.',
        widget=forms.ClearableFileInput(attrs={
            'accept': '.jpg,.jpeg,.png',
            'class': 'form-control',
            'id': 'imageInput',
        })
    )

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validate file extension
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                raise forms.ValidationError(
                    f'Unsupported file type "{ext}". Please upload a JPG or PNG image.'
                )

            # Validate file size
            if image.size > settings.MAX_UPLOAD_SIZE:
                size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
                raise forms.ValidationError(
                    f'File size exceeds {size_mb:.0f} MB. Please upload a smaller image.'
                )

        return image


class CustomUserCreationForm(UserCreationForm):
    """
    Extended registration form that also collects email, first name, last name.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', 'form-control')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form to let users update their profile (first name, last name, email).
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
