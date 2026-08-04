from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .diagnostik import diagnosa_akar_masalah
from .forms import GuruProfileForm, PenilaianFisikForm, PenilaianTeknikForm, SiswaForm
from .models import GuruProfile, MateriFase, Siswa


@login_required
def dashboard_redirect(request):
    """Titik masuk setelah login — arahkan ke dashboard fase guru, atau ke setup profil."""
    try:
        profile = request.user.guruprofile
    except GuruProfile.DoesNotExist:
        return redirect('pjok:buat_profile')
    return redirect('pjok:dashboard_fase', fase=profile.fase)


@login_required
def buat_profile(request):
    """Setup profil guru — pilih fase yang diampu."""
    if request.method == 'POST':
        form = GuruProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('pjok:dashboard_fase', fase=profile.fase)
    else:
        form = GuruProfileForm()
    return render(request, 'pjok/buat_profile.html', {'form': form})


@login_required
def dashboard_fase(request, fase):
    """
    Dashboard utama guru untuk fase tertentu.
    Guru hanya bisa mengakses dashboard fase yang sesuai dengan profilnya —
    dan hanya melihat siswa miliknya sendiri, sama seperti proteksi cabor di combat sports.
    """
    profile = request.user.guruprofile
    if profile.fase != fase:
        return redirect('pjok:dashboard_fase', fase=profile.fase)

    siswa_list = profile.siswa.all()
    return render(request, 'pjok/dashboard.html', {
        'siswa_list': siswa_list,
        'fase': fase,
        'jenjang': profile.jenjang,
        'profile': profile,
    })


@login_required
def tambah_siswa(request):
    """Form tambah siswa baru — otomatis terikat ke guru yang login (fase & sekolahnya)."""
    profile = request.user.guruprofile

    if request.method == 'POST':
        form = SiswaForm(request.POST)
        if form.is_valid():
            siswa = form.save(commit=False)
            siswa.guru = profile  # kunci kepemilikan ke guru yang login
            siswa.save()
            return redirect('pjok:dashboard_fase', fase=profile.fase)
    else:
        form = SiswaForm()

    return render(request, 'pjok/tambah_siswa.html', {
        'form': form,
        'fase': profile.fase,
        'jenjang': profile.jenjang,
    })


@login_required
def tambah_penilaian_fisik(request, siswa_id):
    """Form input tes fisik mentah — skor L1-L4 dihitung otomatis lewat save() di models.py."""
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)  # pastikan siswa milik guru ini

    if request.method == 'POST':
        form = PenilaianFisikForm(request.POST)
        if form.is_valid():
            penilaian = form.save(commit=False)
            penilaian.siswa = siswa
            penilaian.save()
            return redirect('pjok:detail_siswa', siswa_id=siswa.id)
    else:
        form = PenilaianFisikForm()

    return render(request, 'pjok/tambah_penilaian_fisik.html', {'form': form, 'siswa': siswa})


@login_required
def tambah_penilaian_teknik(request, siswa_id):
    """Form input nilai teknik/skill per materi — dipakai untuk diagnosis akar masalah."""
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)  # pastikan siswa milik guru ini

    if request.method == 'POST':
        form = PenilaianTeknikForm(request.POST, fase=profile.fase)
        if form.is_valid():
            penilaian = form.save(commit=False)
            penilaian.siswa = siswa
            penilaian.save()
            return redirect('pjok:detail_siswa', siswa_id=siswa.id)
    else:
        form = PenilaianTeknikForm(fase=profile.fase)

    return render(request, 'pjok/tambah_penilaian_teknik.html', {'form': form, 'siswa': siswa})


@login_required
def detail_siswa(request, siswa_id):
    """Detail siswa + diagnosis akar masalah per materi yang sudah dinilai."""
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)  # pastikan siswa milik guru ini

    diagnosis_per_materi = []
    materi_dinilai = MateriFase.objects.filter(
        penilaian_teknik__siswa=siswa
    ).distinct()
    for materi in materi_dinilai:
        hasil = diagnosa_akar_masalah(siswa, materi)
        if hasil:
            diagnosis_per_materi.append({'materi': materi, 'diagnosis': hasil})

    return render(request, 'pjok/detail_siswa.html', {
        'siswa': siswa,
        'diagnosis_per_materi': diagnosis_per_materi,
    })
