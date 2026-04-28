from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Post


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"id": "id_username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"id": "id_password"}),
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"id": "id_username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"id": "id_password"}),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"id": "id_confirm_password"}),
        label="Confirm",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"id": "id_email"}),
        label="E-mail",
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"id": "id_first_name"}),
        label="First Name",
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"id": "id_last_name"}),
        label="Last Name",
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        passWRD = cleaned.get("password")
        cpassWRD = cleaned.get("confirm_password")
        if passWRD and cpassWRD and passWRD != cpassWRD:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "profile_picture"]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text"]