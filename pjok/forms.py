from django import forms

from .models import GuruProfile, MateriFase, PenilaianFisik, PenilaianKarakter, PenilaianPengetahuan, PenilaianTeknik, Siswa, TINGKAT_CHOICES


class GuruProfileForm(forms.ModelForm):
    class Meta:
        model = GuruProfile
        fields = ['nama_lengkap', 'sekolah', 'fase', 'nip']


class SiswaForm(forms.ModelForm):
    class Meta:
        model = Siswa
        fields = ['nama', 'kelas', 'jenis_kelamin', 'tanggal_lahir']
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date'}),
        }


class PenilaianFisikForm(forms.ModelForm):
    class Meta:
        model = PenilaianFisik
        fields = [
            'plank_hold_detik', 'sit_and_reach_cm',
            'gantung_durasi_tercapai_detik', 'sit_up_repetisi',
            'vertical_jump_cm', 'standing_broad_jump_cm',
            'lari_cepat_detik', 'lari_menengah_detik',
        ]
        # skor_l1-l4 sengaja tidak dimasukkan — dihitung otomatis lewat save() di models.py


class PenilaianTeknikForm(forms.ModelForm):
    class Meta:
        model = PenilaianTeknik
        fields = ['materi', 'tingkat', 'catatan']
        widgets = {
            'materi': forms.RadioSelect,
            'tingkat': forms.RadioSelect,
            'catatan': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, fase=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tingkat'].choices = TINGKAT_CHOICES
        if fase:
            # Guru hanya bisa pilih materi yang sesuai fase-nya sendiri
            self.fields['materi'].queryset = MateriFase.objects.filter(fase=fase)


class PenilaianKarakterForm(forms.ModelForm):
    class Meta:
        model = PenilaianKarakter
        fields = ['aspek', 'tingkat', 'catatan']
        widgets = {
            'aspek': forms.RadioSelect,
            'tingkat': forms.RadioSelect,
            'catatan': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tingkat'].choices = TINGKAT_CHOICES
        self.fields['aspek'].choices = PenilaianKarakter.ASPEK_CHOICES


class PenilaianPengetahuanForm(forms.ModelForm):
    class Meta:
        model = PenilaianPengetahuan
        fields = ['tingkat', 'catatan']
        widgets = {
            'tingkat': forms.RadioSelect,
            'catatan': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tingkat'].choices = TINGKAT_CHOICES