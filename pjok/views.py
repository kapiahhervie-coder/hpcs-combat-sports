import json
from datetime import date
from django.http import HttpResponse, JsonResponse
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

from django.contrib.auth.decorators import login_required
from django.contrib import messages as messages_lib
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import CatatanCedera, KondisiKesehatan, ModulAjar, PenilaianFisik, Siswa, FASE_CHOICES, JENJANG_PER_FASE, SesiAbsensi, Absensi, RencanaMingguan, TujuanPembelajaran, TujuanPembelajaran

from .diagnostik import (
    KOMPONEN_LABEL,
    diagnosa_akar_masalah,
    rekomendasi_perbaikan,
    rubrik_label,
)
from .import_siswa import baca_csv_siswa, buat_template_csv, validasi_baris_siswa
from .forms import CatatanCederaForm, EditSiswaForm, GuruProfileForm, ImportSiswaForm, KondisiKesehatanForm, ModulAjarForm, PenilaianFisikForm, PenilaianKarakterForm, PenilaianPengetahuanForm, PenilaianTeknikForm, PindahFaseForm, RencanaMingguanForm, SiswaForm, TujuanPembelajaranForm
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
    Sementara: semua guru bisa melihat semua fase (akan dibatasi kembali nanti).
    """
    profile = request.user.guruprofile

    siswa_list = Siswa.objects.filter(guru=profile, fase=fase).select_related('kesehatan')

    # Hitung skor kesiapan terbaru per siswa untuk badge di tabel & statistik ringkas
    siswa_data = []
    skor_semua = []
    tier_count = {'SANGAT BAIK': 0, 'BAIK': 0, 'CUKUP': 0, 'PERLU PERHATIAN': 0}
    total_perlu_perhatian_kesehatan = 0

    for s in siswa_list:
        fisik = s.penilaian_fisik.order_by('-tanggal_tes').first()
        kesiapan = None
        tier = None
        if fisik and fisik.skor_l1 is not None:
            kesiapan = round((fisik.skor_l1 + fisik.skor_l2 + fisik.skor_l3 + fisik.skor_l4) / 4, 1)
            skor_semua.append(kesiapan)
            if kesiapan >= 85:
                tier = 'SANGAT BAIK'
            elif kesiapan >= 70:
                tier = 'BAIK'
            elif kesiapan >= 55:
                tier = 'CUKUP'
            else:
                tier = 'PERLU PERHATIAN'
            tier_count[tier] += 1

        # Data kesehatan mungkin belum diisi guru sama sekali — aman kalau None
        kesehatan = getattr(s, 'kesehatan', None)
        perlu_perhatian_kesehatan = bool(kesehatan and kesehatan.perlu_perhatian)
        if perlu_perhatian_kesehatan:
            total_perlu_perhatian_kesehatan += 1

        siswa_data.append({
            'siswa': s,
            'kesiapan': kesiapan,
            'tier': tier,
            'perlu_perhatian_kesehatan': perlu_perhatian_kesehatan,
            'tingkat_risiko': kesehatan.tingkat_risiko if kesehatan else None,
        })

    rata_rata_kesiapan = round(sum(skor_semua) / len(skor_semua), 1) if skor_semua else None
    total_baik_ke_atas = tier_count['SANGAT BAIK'] + tier_count['BAIK']
    total_perlu_perhatian = tier_count['PERLU PERHATIAN']

    selected_siswa_id = request.GET.get('siswa_id')
    selected_siswa = None
    if selected_siswa_id:
        selected_siswa = siswa_list.filter(id=selected_siswa_id).first()

    form_fisik = PenilaianFisikForm()
    form_teknik = PenilaianTeknikForm(fase=fase)
    form_karakter = PenilaianKarakterForm()
    form_pengetahuan = PenilaianPengetahuanForm()

    return render(request, 'pjok/dashboard.html', {
        'siswa_data': siswa_data,
        'total_siswa': siswa_list.count(),
        'rata_rata_kesiapan': rata_rata_kesiapan,
        'total_baik_ke_atas': total_baik_ke_atas,
        'total_perlu_perhatian': total_perlu_perhatian,
        'total_perlu_perhatian_kesehatan': total_perlu_perhatian_kesehatan,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'profile': profile,
        'fase_list': [
            {'kode': k, 'label': v, 'jenjang': JENJANG_PER_FASE.get(k, ''), 'aktif': k == fase}
            for k, v in FASE_CHOICES
        ],
        'siswa_list': siswa_list,
        'selected_siswa': selected_siswa,
        'form_fisik': form_fisik,
        'form_teknik': form_teknik,
        'form_karakter': form_karakter,
        'form_pengetahuan': form_pengetahuan,
    })


@login_required
def tambah_siswa(request):
    """Form tambah siswa baru — terikat ke guru yang login, fase diambil dari halaman asal."""
    profile = request.user.guruprofile
    fase_target = request.GET.get('fase') or profile.fase

    if request.method == 'POST':
        form = SiswaForm(request.POST)
        if form.is_valid():
            siswa = form.save(commit=False)
            siswa.guru = profile
            siswa.fase = request.POST.get('fase') or fase_target
            siswa.save()
            return redirect('pjok:dashboard_fase', fase=siswa.fase)
    else:
        form = SiswaForm()

    return render(request, 'pjok/tambah_siswa.html', {
        'form': form,
        'fase': fase_target,
        'jenjang': JENJANG_PER_FASE.get(fase_target, ''),
    })


@login_required
def import_siswa(request, fase):
    """
    Impor banyak siswa sekaligus dari file CSV. Baris valid tetap disimpan
    meski ada baris lain yang error — guru diberi laporan baris mana yang
    gagal & alasannya, supaya tinggal perbaiki baris itu saja.
    """
    profile = request.user.guruprofile
    hasil = None  # ringkasan hasil impor, ditampilkan setelah submit

    if request.method == 'POST':
        form = ImportSiswaForm(request.POST, request.FILES)
        if form.is_valid():
            baris_mentah, error_header = baca_csv_siswa(request.FILES['file_csv'])

            if error_header:
                hasil = {'sukses': 0, 'gagal': 0, 'error_list': error_header, 'fatal': True}
            else:
                baris_valid, error_list = validasi_baris_siswa(baris_mentah)

                # Cek duplikat sederhana: nama + kelas sama persis dengan siswa yang sudah ada di fase ini
                siswa_ada = set(
                    Siswa.objects.filter(guru=profile, fase=fase)
                    .values_list('nama', 'kelas')
                )

                siswa_baru = []
                dilewati_duplikat = 0
                for b in baris_valid:
                    if (b['nama'], b['kelas']) in siswa_ada:
                        dilewati_duplikat += 1
                        continue
                    siswa_baru.append(Siswa(
                        guru=profile,
                        fase=fase,
                        nama=b['nama'],
                        kelas=b['kelas'],
                        jenis_kelamin=b['jenis_kelamin'],
                        tanggal_lahir=b['tanggal_lahir'],
                    ))

                if siswa_baru:
                    Siswa.objects.bulk_create(siswa_baru)

                hasil = {
                    'sukses': len(siswa_baru),
                    'gagal': len(error_list),
                    'dilewati_duplikat': dilewati_duplikat,
                    'error_list': error_list,
                    'fatal': False,
                }
            form = ImportSiswaForm()  # reset form kosong setelah submit
    else:
        form = ImportSiswaForm()

    return render(request, 'pjok/import_siswa.html', {
        'form': form,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'hasil': hasil,
    })


@login_required
def download_template_csv(request):
    """Unduh template CSV kosong (dengan contoh 2 baris) untuk fitur impor siswa."""
    konten = buat_template_csv()
    response = HttpResponse(konten, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="template_import_siswa.csv"'
    return response


@login_required
def rencana_mingguan(request, fase):
    """Kelola rencana materi mingguan untuk Prota/Prosem, per tahun ajaran & semester."""
    profile = request.user.guruprofile
    tahun_ajaran = request.GET.get('tahun', '2026/2027')
    semester = request.GET.get('semester', 'ganjil')

    if request.method == 'POST':
        minggu_ke = request.POST.get('minggu_ke')
        instance = RencanaMingguan.objects.filter(
            guru=profile, fase=fase, tahun_ajaran=tahun_ajaran,
            semester=semester, minggu_ke=minggu_ke,
        ).first()
        form = RencanaMingguanForm(request.POST, instance=instance, fase=fase, guru=profile)
        if form.is_valid():
            rencana = form.save(commit=False)
            rencana.guru = profile
            rencana.fase = fase
            rencana.tahun_ajaran = tahun_ajaran
            rencana.semester = semester
            rencana.save()
        return redirect(f"{request.path}?tahun={tahun_ajaran}&semester={semester}")

    rencana_list = RencanaMingguan.objects.filter(
        guru=profile, fase=fase, tahun_ajaran=tahun_ajaran, semester=semester,
    ).select_related('materi')
    rencana_map = {r.minggu_ke: r for r in rencana_list}

    JUMLAH_MINGGU = 18
    rows = []
    for i in range(1, JUMLAH_MINGGU + 1):
        rows.append({'minggu_ke': i, 'rencana': rencana_map.get(i)})

    return render(request, 'pjok/rencana_mingguan.html', {
        'rows': rows,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'tahun_ajaran': tahun_ajaran,
        'semester': semester,
        'form_materi_qs': MateriFase.objects.filter(fase=fase),
        'form_tp_qs': TujuanPembelajaran.objects.filter(fase=fase, guru=profile),
    })


@login_required
def daftar_tp(request, fase):
    """Kelola daftar Tujuan Pembelajaran (TP) per elemen CP untuk fase ini."""
    profile = request.user.guruprofile

    if request.method == 'POST':
        tp_id = request.POST.get('tp_id')
        instance = TujuanPembelajaran.objects.filter(id=tp_id, guru=profile, fase=fase).first() if tp_id else None
        form = TujuanPembelajaranForm(request.POST, instance=instance)
        if form.is_valid():
            tp = form.save(commit=False)
            tp.guru = profile
            tp.fase = fase
            tp.save()
        return redirect('pjok:daftar_tp', fase=fase)

    hapus_id = request.GET.get('hapus')
    if hapus_id:
        TujuanPembelajaran.objects.filter(id=hapus_id, guru=profile, fase=fase).delete()
        return redirect('pjok:daftar_tp', fase=fase)

    tp_list = TujuanPembelajaran.objects.filter(guru=profile, fase=fase)
    return render(request, 'pjok/daftar_tp.html', {
        'tp_list': tp_list,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'elemen_choices': TujuanPembelajaran.ELEMEN_CHOICES,
    })


@login_required
def daftar_modul_ajar(request, fase):
    """Daftar semua Modul Ajar yang sudah dibuat guru untuk fase ini."""
    profile = request.user.guruprofile
    modul_list = ModulAjar.objects.filter(guru=profile, fase=fase).prefetch_related('tp').select_related('materi')
    return render(request, 'pjok/daftar_modul_ajar.html', {
        'modul_list': modul_list,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
    })


@login_required
def tambah_modul_ajar(request, fase):
    """Buat Modul Ajar baru, terhubung ke TP yang sudah dirumuskan guru untuk fase ini."""
    profile = request.user.guruprofile

    if request.method == 'POST':
        form = ModulAjarForm(request.POST, fase=fase, guru=profile)
        if form.is_valid():
            modul = form.save(commit=False)
            modul.guru = profile
            modul.fase = fase
            modul.save()
            form.save_m2m()  # simpan relasi many-to-many ke TP setelah objek induk tersimpan
            return redirect('pjok:daftar_modul_ajar', fase=fase)
    else:
        form = ModulAjarForm(fase=fase, guru=profile)

    return render(request, 'pjok/form_modul_ajar.html', {
        'form': form,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'mode': 'tambah',
    })


@login_required
def edit_modul_ajar(request, fase, modul_id):
    """Edit Modul Ajar yang sudah ada."""
    profile = request.user.guruprofile
    modul = get_object_or_404(ModulAjar, id=modul_id, guru=profile, fase=fase)

    if request.method == 'POST':
        form = ModulAjarForm(request.POST, instance=modul, fase=fase, guru=profile)
        if form.is_valid():
            form.save()
            return redirect('pjok:daftar_modul_ajar', fase=fase)
    else:
        form = ModulAjarForm(instance=modul, fase=fase, guru=profile)

    return render(request, 'pjok/form_modul_ajar.html', {
        'form': form,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'mode': 'edit',
        'modul': modul,
    })


@login_required
def hapus_modul_ajar(request, fase, modul_id):
    """Hapus Modul Ajar."""
    profile = request.user.guruprofile
    ModulAjar.objects.filter(id=modul_id, guru=profile, fase=fase).delete()
    return redirect('pjok:daftar_modul_ajar', fase=fase)


@login_required
def daftar_absensi(request, fase):
    """Daftar semua sesi absensi yang pernah diambil untuk fase ini."""
    profile = request.user.guruprofile
    sesi_list = SesiAbsensi.objects.filter(guru=profile, fase=fase).annotate(
        total_hadir=models.Count('daftar_absensi', filter=models.Q(daftar_absensi__status='H')),
        total_siswa=models.Count('daftar_absensi'),
    )
    return render(request, 'pjok/daftar_absensi.html', {
        'sesi_list': sesi_list,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
    })


@login_required
def rekap_absensi(request, fase):
    """Tabel rekap: baris siswa, kolom tanggal sesi, isi status kehadiran."""
    profile = request.user.guruprofile
    siswa_list = Siswa.objects.filter(guru=profile, fase=fase).order_by('nama')
    sesi_list = SesiAbsensi.objects.filter(guru=profile, fase=fase).order_by('tanggal')

    absen_qs = Absensi.objects.filter(sesi__in=sesi_list).select_related('sesi', 'siswa')
    absen_map = {}
    for a in absen_qs:
        absen_map[(a.siswa_id, a.sesi_id)] = a

    rows = []
    for s in siswa_list:
        cells = []
        rekap = {'H': 0, 'I': 0, 'S': 0, 'A': 0}
        for sesi in sesi_list:
            a = absen_map.get((s.id, sesi.id))
            status = a.status if a else None
            if status:
                rekap[status] += 1
            cells.append({'sesi': sesi, 'status': status})
        rows.append({'siswa': s, 'cells': cells, 'rekap': rekap})

    return render(request, 'pjok/rekap_absensi.html', {
        'rows': rows,
        'sesi_list': sesi_list,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
    })


@login_required
def ambil_absensi(request, fase):
    """Ambil/edit absensi untuk fase & tanggal tertentu (?tanggal=YYYY-MM-DD, default hari ini)."""
    profile = request.user.guruprofile
    tanggal_str = request.GET.get('tanggal') or date.today().isoformat()
    tanggal = date.fromisoformat(tanggal_str)

    siswa_list = Siswa.objects.filter(guru=profile, fase=fase).order_by('nama')
    sesi, _ = SesiAbsensi.objects.get_or_create(guru=profile, fase=fase, tanggal=tanggal)

    if request.method == 'POST':
        sesi.catatan_sesi = request.POST.get('catatan_sesi', '')
        sesi.save()
        for s in siswa_list:
            status = request.POST.get(f'status_{s.id}', 'H')
            keterangan = request.POST.get(f'keterangan_{s.id}', '')
            Absensi.objects.update_or_create(
                sesi=sesi, siswa=s,
                defaults={'status': status, 'keterangan': keterangan},
            )
        return redirect('pjok:daftar_absensi', fase=fase)

    absen_map = {a.siswa_id: a for a in sesi.daftar_absensi.all()}
    rows = [{'siswa': s, 'absen': absen_map.get(s.id)} for s in siswa_list]

    return render(request, 'pjok/ambil_absensi.html', {
        'rows': rows,
        'sesi': sesi,
        'tanggal': tanggal,
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'status_choices': Absensi.STATUS_CHOICES,
    })


@login_required
def edit_siswa(request, siswa_id):
    """
    Guru mengedit data dasar siswa miliknya sendiri (nama, kelas, jenis
    kelamin, tanggal lahir). Fase TIDAK bisa diubah di sini — pakai
    pindah_fase_siswa kalau memang perlu memindahkan siswa antar fase.
    """
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)

    if request.method == 'POST':
        form = EditSiswaForm(request.POST, instance=siswa)
        if form.is_valid():
            siswa = form.save()
            return redirect('pjok:dashboard_fase', fase=siswa.fase)
    else:
        form = EditSiswaForm(instance=siswa)

    return render(request, 'pjok/edit_siswa.html', {'form': form, 'siswa': siswa})


@login_required
def pindah_fase_siswa(request, siswa_id):
    """
    Pindahkan siswa ke fase lain — SENGAJA dipisah dari edit_siswa dan
    butuh konfirmasi eksplisit, supaya siswa tidak bisa "kesenggol" pindah
    fase tanpa sadar. Dipakai untuk kasus sah: kenaikan kelas tahun ajaran baru.
    """
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)
    fase_lama = siswa.fase

    if request.method == 'POST':
        if request.POST.get('konfirmasi') != 'ya':
            messages_lib.error(request, "Pemindahan fase dibatalkan — konfirmasi belum dicentang.")
            return redirect('pjok:pindah_fase_siswa', siswa_id=siswa.id)

        form = PindahFaseForm(request.POST, instance=siswa)
        if form.is_valid():
            siswa = form.save()
            messages_lib.success(
                request,
                f"{siswa.nama} dipindahkan dari Fase {fase_lama} ke Fase {siswa.fase}."
            )
            return redirect('pjok:dashboard_fase', fase=siswa.fase)
    else:
        form = PindahFaseForm(instance=siswa)

    return render(request, 'pjok/pindah_fase_siswa.html', {
        'form': form,
        'siswa': siswa,
        'fase_lama': fase_lama,
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
def tambah_penilaian_karakter(request, siswa_id):
    """Form input nilai karakter per aspek (Sportivitas, Kerja Sama, dll)."""
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)

    if request.method == 'POST':
        form = PenilaianKarakterForm(request.POST)
        if form.is_valid():
            penilaian = form.save(commit=False)
            penilaian.siswa = siswa
            penilaian.save()
            return redirect('pjok:detail_siswa', siswa_id=siswa.id)
    else:
        form = PenilaianKarakterForm()

    return render(request, 'pjok/tambah_penilaian_karakter.html', {'form': form, 'siswa': siswa})


@login_required
def tambah_penilaian_pengetahuan(request, siswa_id):
    """Form input nilai pengetahuan gerak (Elemen 2 CP PJOK)."""
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)

    if request.method == 'POST':
        form = PenilaianPengetahuanForm(request.POST)
        if form.is_valid():
            penilaian = form.save(commit=False)
            penilaian.siswa = siswa
            penilaian.save()
            return redirect('pjok:detail_siswa', siswa_id=siswa.id)
    else:
        form = PenilaianPengetahuanForm()

    return render(request, 'pjok/tambah_penilaian_pengetahuan.html', {'form': form, 'siswa': siswa})


@login_required
def detail_siswa(request, siswa_id):
    """
    Laporan diagnostik siswa — mengikuti pola 'Athlete Performance Report' di combat
    sports (radar chart, trend chart, kartu kekuatan/keterbatasan/rekomendasi),
    diadaptasi untuk konteks PJOK: L1-L4 fisik, nilai teknik, diagnosis akar masalah.
    """
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)  # pastikan siswa milik guru ini

    AMBANG = 70
    riwayat_fisik = list(siswa.penilaian_fisik.order_by('tanggal_tes'))
    fisik_terbaru = riwayat_fisik[-1] if riwayat_fisik else None
    teknik_list = siswa.penilaian_teknik.select_related('materi').order_by('-tanggal')
    karakter_list = siswa.penilaian_karakter.order_by('-tanggal')
    pengetahuan_list = siswa.penilaian_pengetahuan.order_by('-tanggal')

    radar_data_json = None
    trend_data_json = None
    months_labels_json = json.dumps([])
    rubrik = {}
    rekomendasi = []
    kekuatan = []
    keterbatasan = []
    kesiapan = None

    if fisik_terbaru:
        skor_map = {
            'l1': fisik_terbaru.skor_l1 or 0,
            'l2': fisik_terbaru.skor_l2 or 0,
            'l3': fisik_terbaru.skor_l3 or 0,
            'l4': fisik_terbaru.skor_l4 or 0,
        }
        kesiapan = round(sum(skor_map.values()) / 4, 1)

        radar_data_json = json.dumps({
            'labels': ['Core & Mobility', 'Strength', 'Power', 'Speed & Agility'],
            'data': [skor_map['l1'], skor_map['l2'], skor_map['l3'], skor_map['l4']],
        })
        rubrik = {
            'l1': rubrik_label(fisik_terbaru.skor_l1),
            'l2': rubrik_label(fisik_terbaru.skor_l2),
            'l3': rubrik_label(fisik_terbaru.skor_l3),
            'l4': rubrik_label(fisik_terbaru.skor_l4),
        }
        rekomendasi = rekomendasi_perbaikan(fisik_terbaru)

        for kode, label in KOMPONEN_LABEL.items():
            if skor_map[kode] >= AMBANG:
                kekuatan.append({'label': label, 'skor': skor_map[kode]})
            else:
                keterbatasan.append({'label': label, 'skor': skor_map[kode]})

        # Tren historis dari seluruh riwayat tes fisik siswa ini
        months_labels_json = json.dumps([r.tanggal_tes.strftime('%d %b') for r in riwayat_fisik])
        trend_data_json = json.dumps({
            'l1': [r.skor_l1 or 0 for r in riwayat_fisik],
            'l2': [r.skor_l2 or 0 for r in riwayat_fisik],
            'l3': [r.skor_l3 or 0 for r in riwayat_fisik],
            'l4': [r.skor_l4 or 0 for r in riwayat_fisik],
        })

    diagnosis_per_materi = []
    materi_dinilai = MateriFase.objects.filter(
        penilaian_teknik__siswa=siswa
    ).distinct()
    for materi in materi_dinilai:
        hasil = diagnosa_akar_masalah(siswa, materi, ambang_batas=AMBANG)
        if hasil:
            diagnosis_per_materi.append({'materi': materi, 'diagnosis': hasil})

    if kesiapan is None:
        tier = None
    elif kesiapan >= 85:
        tier = 'SANGAT BAIK'
    elif kesiapan >= 70:
        tier = 'BAIK'
    elif kesiapan >= 55:
        tier = 'CUKUP'
    else:
        tier = 'PERLU PERHATIAN'

    umur = None
    if siswa.tanggal_lahir:
        hari_ini = date.today()
        umur = hari_ini.year - siswa.tanggal_lahir.year - (
            (hari_ini.month, hari_ini.day) < (siswa.tanggal_lahir.month, siswa.tanggal_lahir.day)
        )

    profil_dominan = None
    if fisik_terbaru:
        semua = kekuatan + keterbatasan
        if semua:
            profil_dominan = max(semua, key=lambda x: x['skor'])['label']

    # Data kesehatan — dipakai untuk banner peringatan di atas halaman detail siswa
    kesehatan = getattr(siswa, 'kesehatan', None)
    riwayat_cedera_terbaru = siswa.riwayat_cedera.all()[:3]

    return render(request, 'pjok/detail_siswa.html', {
        'siswa': siswa,
        'profile': profile,
        'umur': umur,
        'kesehatan': kesehatan,
        'riwayat_cedera_terbaru': riwayat_cedera_terbaru,
        'fisik_terbaru': fisik_terbaru,
        'jumlah_tes': len(riwayat_fisik),
        'teknik_list': teknik_list,
        'karakter_list': karakter_list,
        'pengetahuan_list': pengetahuan_list,
        'radar_data_json': radar_data_json,
        'trend_data_json': trend_data_json,
        'months_labels_json': months_labels_json,
        'rubrik': rubrik,
        'rekomendasi': rekomendasi,
        'kekuatan': kekuatan,
        'keterbatasan': keterbatasan,
        'kesiapan': kesiapan,
        'tier': tier,
        'profil_dominan': profil_dominan,
        'diagnosis_per_materi': diagnosis_per_materi,
        'tanggal_cetak': timezone.now(),
    })


@login_required
def offline_tes_fisik(request, fase):
    """
    Halaman input Tes Fisik yang bisa dipakai TANPA internet.
    Data siswa di-embed langsung ke halaman (bukan diambil via AJAX) supaya
    tetap bisa dipakai walau koneksi putus setelah halaman ini dimuat.
    Isian disimpan ke IndexedDB di browser dulu, baru disinkronkan ke server
    lewat endpoint api_sync_fisik saat koneksi tersedia lagi.
    """
    profile = request.user.guruprofile
    siswa_list = Siswa.objects.filter(guru=profile, fase=fase).order_by('nama')
    siswa_json = json.dumps([{'id': s.id, 'nama': s.nama, 'kelas': s.kelas} for s in siswa_list])

    return render(request, 'pjok/offline_tes_fisik.html', {
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'siswa_json': siswa_json,
    })


def offline_sw(request, fase):
    """
    Service worker untuk fitur offline. Di-serve lewat view (bukan file statis)
    supaya scope-nya jelas dan gampang di-versioning lewat CACHE_NAME.
    """
    sw_code = """
const CACHE_NAME = 'pjok-offline-v1';
const URL_HALAMAN = '/pjok/offline/""" + fase + """/';

self.addEventListener('install', function(event) {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll([URL_HALAMAN]);
    })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(event) {
  // Hanya tangani navigasi ke halaman offline itu sendiri — biarkan request
  // lain (API sync, admin, dll) berjalan normal lewat network.
  if (event.request.mode === 'navigate' && event.request.url.indexOf(URL_HALAMAN) !== -1) {
    event.respondWith(
      fetch(event.request).then(function(response) {
        var responseClone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) { cache.put(event.request, responseClone); });
        return response;
      }).catch(function() {
        return caches.match(event.request);
      })
    );
  }
});
"""
    return HttpResponse(sw_code, content_type='application/javascript')


@login_required
def api_sync_tes_fisik(request):
    """
    Endpoint JSON untuk menyinkronkan isian Tes Fisik yang tadinya disimpan
    offline di localStorage browser. Menerima array entri sekaligus; tiap
    entri diproses independen supaya satu entri gagal tidak menggagalkan yang lain.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    profile = request.user.guruprofile
    try:
        payload = json.loads(request.body)
        entri_list = payload.get('entries', [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Payload tidak valid'}, status=400)

    hasil = []
    field_wajib = [
        'plank_hold_detik', 'sit_and_reach_cm', 'gantung_durasi_tercapai_detik',
        'sit_up_repetisi', 'vertical_jump_cm', 'lari_cepat_detik', 'lari_menengah_detik',
    ]

    for entri in entri_list:
        local_id = entri.get('local_id', '')
        siswa_id = entri.get('siswa_id')
        try:
            siswa = Siswa.objects.get(id=siswa_id, guru=profile)
            data_bersih = {}
            for f in field_wajib:
                nilai = entri.get(f)
                if nilai in (None, ''):
                    raise ValueError(f"Kolom '{f}' kosong")
                data_bersih[f] = int(float(nilai)) if f == 'sit_up_repetisi' else float(nilai)

            standing_broad = entri.get('standing_broad_jump_cm')
            if standing_broad not in (None, ''):
                data_bersih['standing_broad_jump_cm'] = float(standing_broad)

            fisik = PenilaianFisik(siswa=siswa, **data_bersih)
            fisik.save()  # skor_l1-l4 dihitung otomatis di save()

            hasil.append({'local_id': local_id, 'status': 'ok', 'id': fisik.id})
        except Siswa.DoesNotExist:
            hasil.append({'local_id': local_id, 'status': 'error', 'pesan': 'Siswa tidak ditemukan / bukan milik Anda'})
        except (ValueError, TypeError) as e:
            hasil.append({'local_id': local_id, 'status': 'error', 'pesan': str(e)})

    return JsonResponse({'hasil': hasil})


@login_required
def data_kesehatan(request, siswa_id):
    """
    Kelola data kesehatan siswa: alergi, riwayat penyakit, kontraindikasi
    aktivitas, kontak darurat, dan tingkat risiko. Dipakai guru sebelum
    aktivitas fisik berat agar tahu kondisi khusus siswa.
    """
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)  # pastikan siswa milik guru ini
    kesehatan, _ = KondisiKesehatan.objects.get_or_create(siswa=siswa)

    if request.method == 'POST':
        form = KondisiKesehatanForm(request.POST, instance=kesehatan)
        if form.is_valid():
            form.save()
            return redirect('pjok:data_kesehatan', siswa_id=siswa.id)
    else:
        form = KondisiKesehatanForm(instance=kesehatan)

    return render(request, 'pjok/data_kesehatan.html', {
        'siswa': siswa,
        'kesehatan': kesehatan,
        'form': form,
        'riwayat_cedera': siswa.riwayat_cedera.all(),
        'form_cedera': CatatanCederaForm(),
    })


@login_required
def tambah_cedera(request, siswa_id):
    """Catat kejadian cedera baru untuk siswa — riwayat ditampilkan kronologis di data_kesehatan."""
    profile = request.user.guruprofile
    siswa = get_object_or_404(Siswa, id=siswa_id, guru=profile)  # pastikan siswa milik guru ini

    if request.method == 'POST':
        form = CatatanCederaForm(request.POST)
        if form.is_valid():
            cedera = form.save(commit=False)
            cedera.siswa = siswa
            cedera.dicatat_oleh = profile
            cedera.save()

    return redirect('pjok:data_kesehatan', siswa_id=siswa.id)




@login_required
def export_lembar_kosong(request, fase):
    """
    Lembar Penilaian Fisik kosong (Word/docx, siap cetak) untuk diisi manual
    di lapangan saat tidak ada koneksi internet — hasilnya diinput ulang lewat
    form Tes Fisik setelah kembali online.
    """
    profile = request.user.guruprofile
    siswa_list = Siswa.objects.filter(guru=profile, fase=fase).order_by('nama')

    doc = _bikin_dokumen_dasar(
        "LEMBAR PENILAIAN FISIK (KOSONG)\nUntuk diisi manual / offline",
        profile, fase, JENJANG_PER_FASE.get(fase, ''),
    )

    p = doc.add_paragraph()
    p.add_run(f"Tanggal Tes: _______________________          Materi/Sesi: _______________________________").font.size = Pt(10)
    doc.add_paragraph()

    kolom = ['No', 'Nama Siswa', 'Plank\n(detik)', 'Sit&Reach\n(cm)', 'Gantung\n(detik)', 'Sit Up\n(rep)', 'Vert. Jump\n(cm)', 'Lari Cepat\n(detik)', 'Lari Menengah\n(detik)']
    table = doc.add_table(rows=1, cols=len(kolom))
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    for i, judul in enumerate(kolom):
        hdr[i].text = judul

    if siswa_list:
        for i, s in enumerate(siswa_list, start=1):
            cells = table.add_row().cells
            cells[0].text = str(i)
            cells[1].text = s.nama
            for j in range(2, len(kolom)):
                cells[j].text = ''
    else:
        cells = table.add_row().cells
        cells[1].text = '(belum ada siswa terdaftar di fase ini)'

    doc.add_paragraph()
    doc.add_paragraph("Catatan: setelah kembali online, salin hasil pengisian ini ke menu Tes Fisik masing-masing siswa.")

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="Lembar_Kosong_Fisik_Fase{fase}.docx"'
    doc.save(response)
    return response


@login_required
def offline_tes_fisik(request, fase):
    """
    Halaman Input Tes Fisik yang bisa dipakai TANPA internet setelah dibuka
    sekali. Data disimpan dulu di penyimpanan lokal perangkat (localStorage),
    lalu disinkronkan otomatis ke server begitu koneksi kembali tersedia.
    """
    profile = request.user.guruprofile
    siswa_list = list(
        Siswa.objects.filter(guru=profile, fase=fase).order_by('nama').values('id', 'nama', 'kelas')
    )
    return render(request, 'pjok/offline_tes_fisik.html', {
        'fase': fase,
        'jenjang': JENJANG_PER_FASE.get(fase, ''),
        'siswa_json': json.dumps(siswa_list),
    })


def offline_sw(request, fase):
    """
    Service Worker untuk halaman offline_tes_fisik. Di-serve sebagai view
    (bukan file static) supaya scope-nya otomatis terbatas ke /pjok/offline/<fase>/
    saja — sesuai lokasi URL file ini sendiri.
    """
    js = """
const CACHE_NAME = 'pjok-offline-tesfisik-v1';

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.add(self.registration.scope);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil(self.clients.claim());
});

// Strategi: coba jaringan dulu (data selalu fresh kalau online),
// kalau gagal (offline) pakai versi tersimpan di cache.
self.addEventListener('fetch', function (event) {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request)
      .then(function (response) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function (cache) { cache.put(event.request, copy); });
        return response;
      })
      .catch(function () {
        return caches.match(event.request);
      })
  );
});
"""
    return HttpResponse(js, content_type='application/javascript')


@login_required
def api_sync_tes_fisik(request):
    """
    Endpoint sinkronisasi: menerima daftar entri Tes Fisik yang tadinya
    disimpan offline di localStorage klien, lalu menyimpannya ke database.
    Menerima banyak entri sekaligus dalam satu request (payload JSON).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    profile = request.user.guruprofile
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'Payload JSON tidak valid'}, status=400)

    entries = payload.get('entries', [])
    hasil = []

    for entry in entries:
        local_id = entry.get('local_id', '')
        try:
            siswa = Siswa.objects.get(id=entry['siswa_id'], guru=profile)
            PenilaianFisik.objects.create(
                siswa=siswa,
                plank_hold_detik=float(entry['plank_hold_detik']),
                sit_and_reach_cm=float(entry['sit_and_reach_cm']),
                gantung_durasi_tercapai_detik=float(entry['gantung_durasi_tercapai_detik']),
                sit_up_repetisi=int(entry['sit_up_repetisi']),
                vertical_jump_cm=float(entry['vertical_jump_cm']),
                standing_broad_jump_cm=float(entry['standing_broad_jump_cm']) if entry.get('standing_broad_jump_cm') else None,
                lari_cepat_detik=float(entry['lari_cepat_detik']),
                lari_menengah_detik=float(entry['lari_menengah_detik']),
            )
            hasil.append({'local_id': local_id, 'status': 'ok', 'siswa': siswa.nama})
        except Siswa.DoesNotExist:
            hasil.append({'local_id': local_id, 'status': 'error', 'pesan': 'Siswa tidak ditemukan (mungkin sudah dihapus)'})
        except (KeyError, ValueError, TypeError) as e:
            hasil.append({'local_id': local_id, 'status': 'error', 'pesan': f'Data tidak lengkap/salah format: {e}'})

    return JsonResponse({'hasil': hasil})


def _bikin_dokumen_dasar(judul, guru, fase, jenjang):
    doc = Document()
    for section in doc.sections:
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    h = doc.add_heading(judul, level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Mata Pelajaran: PJOK (Pendidikan Jasmani, Olahraga, dan Kesehatan)")
    run.font.size = Pt(11)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.add_run(f"Fase {fase} ({jenjang}) - Sekolah: {guru.sekolah}").font.size = Pt(11)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.add_run(f"Guru Pengampu: {guru.nama_lengkap}").font.size = Pt(11)

    doc.add_paragraph()
    return doc


def _isi_tabel_rencana(doc, rows, dengan_semester=False):
    kolom = 5 if dengan_semester else 4
    table = doc.add_table(rows=1, cols=kolom)
    table.style = 'Light Grid Accent 1'
    hdr = table.rows[0].cells
    hdr[0].text = 'Minggu'
    hdr[1].text = 'Materi Pembelajaran'
    hdr[2].text = 'Alokasi JP'
    hdr[3].text = 'Keterangan'
    if dengan_semester:
        hdr[4].text = 'Semester'

    for row in rows:
        cells = table.add_row().cells
        cells[0].text = str(row['minggu_ke'])
        if row.get('rencana'):
            cells[1].text = row['rencana'].nama_tampil
            cells[2].text = str(row['rencana'].alokasi_jp)
            cells[3].text = row['rencana'].keterangan or ''
        else:
            cells[1].text = '-'
            cells[2].text = '-'
            cells[3].text = ''
        if dengan_semester:
            cells[4].text = row.get('semester_label', '')


@login_required
def export_prosem(request, fase):
    """Generate dokumen Word Program Semester (Prosem)."""
    profile = request.user.guruprofile
    tahun_ajaran = request.GET.get('tahun', '2026/2027')
    semester = request.GET.get('semester', 'ganjil')

    rencana_list = RencanaMingguan.objects.filter(
        guru=profile, fase=fase, tahun_ajaran=tahun_ajaran, semester=semester,
    ).select_related('materi')
    rencana_map = {r.minggu_ke: r for r in rencana_list}
    rows = [{'minggu_ke': i, 'rencana': rencana_map.get(i)} for i in range(1, 19)]

    judul_semester = 'Ganjil' if semester == 'ganjil' else 'Genap'
    doc = _bikin_dokumen_dasar(
        f"PROGRAM SEMESTER {judul_semester.upper()}\nTahun Ajaran {tahun_ajaran}",
        profile, fase, JENJANG_PER_FASE.get(fase, ''),
    )
    _isi_tabel_rencana(doc, rows)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="Prosem_{judul_semester}_{fase}_{tahun_ajaran.replace("/", "-")}.docx"'
    doc.save(response)
    return response


@login_required
def export_prota(request, fase):
    """Generate dokumen Word Program Tahunan (Prota), gabungan semester ganjil + genap."""
    profile = request.user.guruprofile
    tahun_ajaran = request.GET.get('tahun', '2026/2027')

    doc = _bikin_dokumen_dasar(
        f"PROGRAM TAHUNAN\nTahun Ajaran {tahun_ajaran}",
        profile, fase, JENJANG_PER_FASE.get(fase, ''),
    )

    for semester, label in [('ganjil', 'Ganjil'), ('genap', 'Genap')]:
        doc.add_heading(f"Semester {label}", level=2)
        rencana_list = RencanaMingguan.objects.filter(
            guru=profile, fase=fase, tahun_ajaran=tahun_ajaran, semester=semester,
        ).select_related('materi')
        rencana_map = {r.minggu_ke: r for r in rencana_list}
        rows = [{'minggu_ke': i, 'rencana': rencana_map.get(i)} for i in range(1, 19)]
        _isi_tabel_rencana(doc, rows)
        doc.add_paragraph()

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="Prota_{fase}_{tahun_ajaran.replace("/", "-")}.docx"'
    doc.save(response)
    return response


@login_required
def export_modul_ajar(request, fase, modul_id):
    """Generate dokumen Word Modul Ajar — siap cetak/dibagikan, mengikuti format Kurikulum Merdeka."""
    profile = request.user.guruprofile
    modul = get_object_or_404(ModulAjar, id=modul_id, guru=profile, fase=fase)

    doc = _bikin_dokumen_dasar(
        f"MODUL AJAR\n{modul.judul}",
        profile, fase, JENJANG_PER_FASE.get(fase, ''),
    )

    doc.add_heading('A. Informasi Umum', level=2)
    tabel_info = doc.add_table(rows=0, cols=2)
    tabel_info.style = 'Light Grid Accent 1'
    for label, isi in [
        ('Materi', modul.materi.nama_materi if modul.materi else '-'),
        ('Alokasi Waktu', modul.alokasi_waktu),
    ]:
        row = tabel_info.add_row().cells
        row[0].text = label
        row[1].text = isi
    doc.add_paragraph()

    doc.add_heading('B. Tujuan Pembelajaran', level=2)
    tp_list = modul.tp.all()
    if tp_list:
        for tp in tp_list:
            doc.add_paragraph(f"{tp.kode} — {tp.deskripsi}", style='List Bullet')
    else:
        doc.add_paragraph('(Belum ada TP yang dipilih untuk modul ini)')

    if modul.pemahaman_bermakna:
        doc.add_heading('C. Pemahaman Bermakna', level=2)
        doc.add_paragraph(modul.pemahaman_bermakna)

    if modul.pertanyaan_pemantik:
        doc.add_heading('D. Pertanyaan Pemantik', level=2)
        doc.add_paragraph(modul.pertanyaan_pemantik)

    doc.add_heading('E. Kegiatan Pembelajaran', level=2)
    for sub_judul, isi in [
        ('Pendahuluan', modul.kegiatan_pendahuluan),
        ('Inti', modul.kegiatan_inti),
        ('Penutup', modul.kegiatan_penutup),
    ]:
        doc.add_heading(sub_judul, level=3)
        doc.add_paragraph(isi or '(belum diisi)')

    if modul.asesmen:
        doc.add_heading('F. Asesmen', level=2)
        doc.add_paragraph(modul.asesmen)

    if modul.sumber_media:
        doc.add_heading('G. Sumber & Media Belajar', level=2)
        doc.add_paragraph(modul.sumber_media)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    nama_file = modul.judul.replace('/', '-')
    response['Content-Disposition'] = f'attachment; filename="ModulAjar_{nama_file}.docx"'
    doc.save(response)
    return response