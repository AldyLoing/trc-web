from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, WasteTransaction

class FormPendaftaran(UserCreationForm):
    email = forms.EmailField(required=True)
    nomor_hape = forms.CharField(max_length=15, required=True)
    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'nik', 'email', 'nomor_hape', 'address', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super(FormPendaftaran, self).save(commit=False)
        user.nomor_hape = self.cleaned_data['nomor_hape']
        if commit:
            user.save()
        return user

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'nomor_hape', 'address', 'role', 'password1', 'password2']

    def clean_role(self):
        user = self.instance
        if not user.is_superuser and self.cleaned_data['role'] == CustomUser.ADMIN_TRX:
            raise forms.ValidationError("Hanya superadmin yang bisa membuat Admin TRC!")
        return self.cleaned_data['role']


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'nik', 'email', 'nomor_hape', 'address', 'role', 'profile_picture']
        labels = {
            "username": "Nama Pengguna",
            "nik": "NIK",
            "email": "Email",
            "nomor_hape": "Nomor Telepon",
            "address": "Alamat",
            "role": "Peran",
            "profile_picture": "Foto Profil",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "nik": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "nomor_hape": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        user_id = self.instance.id  # Ambil ID user yang sedang diedit

        if CustomUser.objects.exclude(id=user_id).filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user_id = self.instance.id  # Ambil ID user yang sedang diedit

        if CustomUser.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["profile_picture", "username", "nik", "email", "nomor_hape", "address"]
        labels = {
            "profile_picture": "Foto Profil",
            "username": "Nama Pengguna",
            "nik": "NIK",
            "email": "Email",
            "nomor_hape": "Nomor Telepon",
            "address": "Alamat",
        }
        widgets = {
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "nik": forms.TextInput(attrs={"class": "form-control", "pattern": "\d{16}", "title": "Masukkan 16 digit angka"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "nomor_hape": forms.TextInput(attrs={"class": "form-control", "pattern": "\d+", "title": "Masukkan hanya angka"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }
        
class WasteTransactionForm(forms.ModelForm):
    class Meta:
        model = WasteTransaction
        fields = ['user', 'category', 'weight_kg']
        labels = {
            'user': 'Nama Pengguna',
            'category': 'Kategori Sampah',
            'weight_kg': 'Berat (kg)',
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

