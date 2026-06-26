from django import forms
from .models import User, Cabor

class PelatihRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Ambil pilihan cabor yang tersedia di database
    cabor_akses = forms.ModelChoiceField(
        queryset=Cabor.objects.all(),
        empty_label="-- Pilih Cabang Olahraga Anda --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'cabor_akses']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password dan konfirmasi password tidak cocok!")
        return cleaned_data