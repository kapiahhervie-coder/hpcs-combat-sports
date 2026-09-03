from django import forms

from .models import CatatanCedera, GuruProfile, KondisiKesehatan, MateriFase, PenilaianFisik, PenilaianKarakter, PenilaianPengetahuan, PenilaianTeknik, RencanaMingguan, Siswa, TINGKAT_CHOICES, TujuanPembelajaran


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


class EditSiswaForm(forms.ModelForm):
    class Meta:
        model = Siswa
        fields = ['nama', 'kelas', 'jenis_kelamin', 'tanggal_lahir', 'fase']
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

class RencanaMingguanForm(forms.ModelForm):
    class Meta:
        model = RencanaMingguan
        fields = ['minggu_ke', 'materi', 'nama_materi_bebas', 'tp', 'alokasi_jp', 'keterangan']

    def __init__(self, *args, fase=None, guru=None, **kwargs):
        super().__init__(*args, **kwargs)
        if fase:
            self.fields['materi'].queryset = MateriFase.objects.filter(fase=fase)
        if fase and guru:
            self.fields['tp'].queryset = TujuanPembelajaran.objects.filter(fase=fase, guru=guru)
        self.fields['materi'].required = False
        self.fields['tp'].required = False


class TujuanPembelajaranForm(forms.ModelForm):
    class Meta:
        model = TujuanPembelajaran
        fields = ['kode', 'elemen', 'deskripsi', 'kktp']
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
            'kktp': forms.Textarea(attrs={'rows': 3}),
        }

class RencanaMingguanForm(forms.ModelForm):
    class Meta:
        model = RencanaMingguan
        fields = ['minggu_ke', 'materi', 'nama_materi_bebas', 'tp', 'alokasi_jp', 'keterangan']

    def __init__(self, *args, fase=None, guru=None, **kwargs):
        super().__init__(*args, **kwargs)
        if fase:
            self.fields['materi'].queryset = MateriFase.objects.filter(fase=fase)
        if fase and guru:
            self.fields['tp'].queryset = TujuanPembelajaran.objects.filter(fase=fase, guru=guru)
        self.fields['materi'].required = False
        self.fields['tp'].required = False


class TujuanPembelajaranForm(forms.ModelForm):
    class Meta:
        model = TujuanPembelajaran
        fields = ['kode', 'elemen', 'deskripsi', 'kktp']
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
            'kktp': forms.Textarea(attrs={'rows': 3}),
        }

class KondisiKesehatanForm(forms.ModelForm):
    class Meta:
        model = KondisiKesehatan
        fields = [
            'golongan_darah', 'alergi', 'riwayat_penyakit', 'kontraindikasi_aktivitas',
            'obat_darurat', 'kontak_darurat_nama', 'kontak_darurat_hubungan',
            'kontak_darurat_telepon', 'tingkat_risiko', 'catatan_tambahan',
        ]
        widgets = {
            'alergi': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Contoh: debu, kacang, obat tertentu'}),
            'riwayat_penyakit': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Contoh: asma, jantung bawaan'}),
            'kontraindikasi_aktivitas': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Contoh: hindari lari jarak jauh tanpa jeda'}),
            'catatan_tambahan': forms.Textarea(attrs={'rows': 3}),
            'tingkat_risiko': forms.RadioSelect,
        }


class CatatanCederaForm(forms.ModelForm):
    class Meta:
        model = CatatanCedera
        fields = ['tanggal_kejadian', 'jenis_cedera', 'deskripsi', 'tindakan_diambil', 'status']
        widgets = {
            'tanggal_kejadian': forms.DateInput(attrs={'type': 'date'}),
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
            'tindakan_diambil': forms.Textarea(attrs={'rows': 2}),
            'status': forms.RadioSelect,
        }


class ImportSiswaForm(forms.Form):
    """
    Form unggah file CSV berisi banyak siswa sekaligus.
    Kolom yang diharapkan: nama, kelas, jenis_kelamin (L/P), tanggal_lahir (YYYY-MM-DD)
    """
    file_csv = forms.FileField(
        label='File CSV Siswa',
        help_text='Kolom: nama, kelas, jenis_kelamin (L/P), tanggal_lahir (YYYY-MM-DD)',
    )

    def clean_file_csv(self):
        f = self.cleaned_data['file_csv']
        if not f.name.lower().endswith('.csv'):
            raise forms.ValidationError('File harus berformat .csv (unduh dulu template kalau belum punya).')
        if f.size > 2 * 1024 * 1024:  # 2MB — lebih dari cukup untuk ribuan baris siswa
            raise forms.ValidationError('Ukuran file terlalu besar (maksimal 2MB).')
        return f