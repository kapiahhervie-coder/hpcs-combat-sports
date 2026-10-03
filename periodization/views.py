"""
periodization/views.py
Tahap 3 HPCS -- Views & Routing untuk Pilar 3 (Periodisasi).

Semua view WAJIB scoped ke pelatih yang login (kecuali staff/superuser)
-- lihat get_macro_program_queryset(). Ini niru pola yang sudah
diperbaiki di semua app cabang (karate/muaythai/boxing/taekwondo)
supaya tidak mengulang bug IDOR yang sama di fitur baru ini.
"""
import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views import View
import io
from datetime import timedelta as _timedelta

from combat.models import Atlet
from combat.views import ProRequiredMixin
from .models import MacroProgram, MesoCycle, MicroCycle, KompetisiTarget, TargetPerforma, SesiLatihan, LatihanItem, PILAR_FOKUS_HARIAN_CHOICES, KATEGORI_LATIHAN_CHOICES, WAKTU_SESI_CHOICES
from .services import generate_periodisasi_otomatis, bangun_pertimbangan

NAMA_HARI = {1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu', 7: 'Minggu'}


def get_macro_program_queryset(user):
    """Scoping kepemilikan: pelatih cuma lihat program milik atlet binaannya sendiri."""
    qs = MacroProgram.objects.select_related('atlet')
    if user.is_staff or user.is_superuser:
        return qs
    return qs.filter(atlet__pelatih=user)


def get_atlet_queryset_lokal(user):
    """
    Scoping yang sama, versi buat pilihan atlet di form Tambah Program.

    Difilter DUA lapis buat coach biasa: pelatih=user (atlet binaannya
    sendiri) DAN cabang=cabor pelatih tersebut -- supaya kalau ada data
    lama/salah assign yang bikin atlet lintas-cabor nyasar ke pelatih
    ini, halaman Periodisasi tetap tidak menampilkannya. Konsisten
    dengan filter cabang yang sudah dikunci di TambahAtletView.
    """
    qs = Atlet.objects.all()
    if user.is_staff or user.is_superuser:
        return qs
    profil = getattr(user, 'profil_pelatih', None)
    if not profil or not profil.cabang:
        return Atlet.objects.none()
    return qs.filter(pelatih=user, cabang=profil.cabang)


def get_meso_cycle_queryset(user):
    """Scoping via macro_program -- 1 lapis turunan dari get_macro_program_queryset."""
    qs = MesoCycle.objects.select_related('macro_program', 'macro_program__atlet')
    if user.is_staff or user.is_superuser:
        return qs
    return qs.filter(macro_program__atlet__pelatih=user)


def get_micro_cycle_queryset(user):
    """Scoping via meso_cycle -> macro_program -- 2 lapis turunan."""
    qs = MicroCycle.objects.select_related('meso_cycle', 'meso_cycle__macro_program')
    if user.is_staff or user.is_superuser:
        return qs
    return qs.filter(meso_cycle__macro_program__atlet__pelatih=user)


def get_sesi_latihan_queryset(user):
    """Scoping via micro_cycle -> meso_cycle -> macro_program -- 3 lapis turunan."""
    qs = SesiLatihan.objects.select_related('micro_cycle', 'micro_cycle__meso_cycle')
    if user.is_staff or user.is_superuser:
        return qs
    return qs.filter(micro_cycle__meso_cycle__macro_program__atlet__pelatih=user)


def get_latihan_item_queryset(user):
    """Scoping via sesi_latihan -> ... -- 4 lapis turunan."""
    qs = LatihanItem.objects.select_related('sesi_latihan')
    if user.is_staff or user.is_superuser:
        return qs
    return qs.filter(sesi_latihan__micro_cycle__meso_cycle__macro_program__atlet__pelatih=user)


class DaftarMacroProgramView(ProRequiredMixin, LoginRequiredMixin, View):
    template_name = 'periodization/daftar_program.html'

    def get(self, request):
        daftar_program = get_macro_program_queryset(request.user).order_by('-tanggal_mulai')
        return render(request, self.template_name, {
            'daftar_program': daftar_program,
            'total_program': daftar_program.count(),
        })


class TambahMacroProgramView(ProRequiredMixin, LoginRequiredMixin, View):
    template_name = 'periodization/tambah_program.html'

    def get(self, request):
        daftar_atlet = get_atlet_queryset_lokal(request.user).order_by('nama_atlet')
        return render(request, self.template_name, {'daftar_atlet': daftar_atlet})

    def post(self, request):
        atlet_id = request.POST.get('atlet_id')
        atlet = get_object_or_404(get_atlet_queryset_lokal(request.user), pk=atlet_id)

        try:
            tanggal_mulai = date.fromisoformat(request.POST.get('tanggal_mulai', ''))
            tanggal_target = date.fromisoformat(request.POST.get('tanggal_target', ''))
        except ValueError:
            messages.error(request, "Format tanggal tidak valid. Pastikan tanggal mulai & target sudah diisi dengan benar.")
            daftar_atlet = get_atlet_queryset_lokal(request.user).order_by('nama_atlet')
            return render(request, self.template_name, {'daftar_atlet': daftar_atlet})

        program = MacroProgram.objects.create(
            atlet=atlet,
            nama_program=request.POST.get('nama_program', '').strip(),
            event_target=request.POST.get('event_target', 'lainnya'),
            nama_event=request.POST.get('nama_event', '').strip(),
            tanggal_mulai=tanggal_mulai,
            tanggal_target=tanggal_target,
            catatan=request.POST.get('catatan', '').strip(),
        )

        # Auto-generate mesocycle langsung kalau pelatih centang opsinya
        if request.POST.get('generate_otomatis') == 'on':
            hasil = generate_periodisasi_otomatis(program)
            if hasil['berhasil']:
                messages.success(request, f"Program '{program.nama_program}' dibuat & {hasil['pesan']}")
            else:
                messages.warning(request, f"Program '{program.nama_program}' dibuat, tapi auto-generate gagal: {hasil['pesan']}")
        else:
            messages.success(request, f"Program '{program.nama_program}' berhasil dibuat.")

        return redirect('periodization:detail_program', program_id=program.id)


class DetailMacroProgramView(ProRequiredMixin, LoginRequiredMixin, View):
    template_name = 'periodization/detail_program.html'

    def get(self, request, program_id):
        program = get_object_or_404(get_macro_program_queryset(request.user), pk=program_id)
        meso_list = program.meso_cycles.order_by('urutan')
        return render(request, self.template_name, {
            'program': program,
            'meso_list': meso_list,
        })


class GenerateOtomatisView(ProRequiredMixin, LoginRequiredMixin, View):
    """
    Action 1-klik: generate MesoCycle otomatis buat 1 MacroProgram.
    POST-only -- ini aksi yang mengubah data, jangan lewat GET/link biasa.
    """
    def post(self, request, program_id):
        program = get_object_or_404(get_macro_program_queryset(request.user), pk=program_id)
        hapus_lama = request.POST.get('hapus_lama') == '1'

        hasil = generate_periodisasi_otomatis(program, hapus_lama=hapus_lama)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(hasil, status=200 if hasil['berhasil'] else 400)

        if hasil['berhasil']:
            messages.success(request, hasil['pesan'])
        else:
            messages.error(request, hasil['pesan'])
        return redirect('periodization:detail_program', program_id=program.id)


class KurvaVolumeIntensitasView(ProRequiredMixin, LoginRequiredMixin, View):
    """
    Endpoint JSON: data kurva Volume vs Intensitas 1 MacroProgram,
    siap dipakai Chart.js/Matplotlib di frontend (Tahap 4).
    """
    def get(self, request, program_id):
        program = get_object_or_404(get_macro_program_queryset(request.user), pk=program_id)
        meso_list = program.meso_cycles.order_by('urutan')

        data = {
            'program': program.nama_program,
            'atlet': program.atlet.nama_atlet,
            'labels': [m.get_nama_fase_display() for m in meso_list],
            'volume': [m.volume_target for m in meso_list],
            'intensitas': [m.intensitas_target for m in meso_list],
            'tanggal_mulai': [m.tanggal_mulai.isoformat() for m in meso_list],
            'tanggal_selesai': [m.tanggal_selesai.isoformat() for m in meso_list],
        }
        return JsonResponse(data)


# ----------------------------------------------------------------------
# KALENDER KOMPETISI (nempel di MacroProgram)
# ----------------------------------------------------------------------

class TambahKompetisiView(ProRequiredMixin, LoginRequiredMixin, View):
    """POST-only -- ditambahkan dari halaman detail_program."""
    def post(self, request, program_id):
        program = get_object_or_404(get_macro_program_queryset(request.user), pk=program_id)

        nama = request.POST.get('nama_kompetisi', '').strip()
        try:
            tanggal_mulai = date.fromisoformat(request.POST.get('tanggal_mulai', ''))
        except ValueError:
            messages.error(request, "Tanggal mulai kompetisi wajib diisi dengan format yang benar.")
            return redirect('periodization:detail_program', program_id=program.id)

        tanggal_selesai_raw = request.POST.get('tanggal_selesai', '')
        tanggal_selesai = None
        if tanggal_selesai_raw:
            try:
                tanggal_selesai = date.fromisoformat(tanggal_selesai_raw)
            except ValueError:
                tanggal_selesai = None

        if not nama:
            messages.error(request, "Nama kompetisi wajib diisi.")
            return redirect('periodization:detail_program', program_id=program.id)

        KompetisiTarget.objects.create(
            macro_program=program,
            nama_kompetisi=nama,
            tanggal_mulai=tanggal_mulai,
            tanggal_selesai=tanggal_selesai,
            level=request.POST.get('level', 'domestik'),
            status=request.POST.get('status', 'OPSIONAL'),
            catatan=request.POST.get('catatan', '').strip(),
        )
        messages.success(request, f"Kompetisi '{nama}' ditambahkan ke kalender.")
        return redirect('periodization:detail_program', program_id=program.id)


class HapusKompetisiView(ProRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, kompetisi_id):
        kompetisi = get_object_or_404(KompetisiTarget.objects.filter(
            macro_program__in=get_macro_program_queryset(request.user)
        ), pk=kompetisi_id)
        program_id = kompetisi.macro_program_id
        nama = kompetisi.nama_kompetisi
        kompetisi.delete()
        messages.success(request, f"Kompetisi '{nama}' dihapus dari kalender.")
        return redirect('periodization:detail_program', program_id=program_id)


# ----------------------------------------------------------------------
# DETAIL MESOCYCLE (objektif fisik, target performa, daftar microcycle)
# ----------------------------------------------------------------------

class DetailMesoCycleView(ProRequiredMixin, LoginRequiredMixin, View):
    template_name = 'periodization/detail_meso.html'

    def get(self, request, meso_id):
        meso = get_object_or_404(get_meso_cycle_queryset(request.user), pk=meso_id)
        return render(request, self.template_name, {
            'meso': meso,
            'target_performa_list': meso.target_performa.all(),
            'micro_list': meso.micro_cycles.order_by('minggu_ke'),
            'sibling_meso_list': meso.macro_program.meso_cycles.order_by('urutan'),
            'pertimbangan_list': bangun_pertimbangan(meso),
        })

    def post(self, request, meso_id):
        """Edit objektif_fisik & porsi fokus L1-L4 langsung dari halaman detail."""
        meso = get_object_or_404(get_meso_cycle_queryset(request.user), pk=meso_id)
        meso.objektif_fisik = request.POST.get('objektif_fisik', '').strip()
        meso.objektif_teknik = request.POST.get('objektif_teknik', '').strip()
        meso.objektif_taktik = request.POST.get('objektif_taktik', '').strip()
        meso.objektif_mental = request.POST.get('objektif_mental', '').strip()
        try:
            meso.fokus_l1_persen = int(request.POST.get('fokus_l1_persen', meso.fokus_l1_persen))
            meso.fokus_l2_persen = int(request.POST.get('fokus_l2_persen', meso.fokus_l2_persen))
            meso.fokus_l3_persen = int(request.POST.get('fokus_l3_persen', meso.fokus_l3_persen))
            meso.fokus_l4_persen = int(request.POST.get('fokus_l4_persen', meso.fokus_l4_persen))
            meso.volume_target = int(request.POST.get('volume_target', meso.volume_target))
            meso.intensitas_target = int(request.POST.get('intensitas_target', meso.intensitas_target))
        except ValueError:
            messages.error(request, "Nilai fokus/volume/intensitas harus berupa angka.")
            return redirect('periodization:detail_meso', meso_id=meso.id)
        meso.save()
        messages.success(request, "Fase berhasil diupdate.")
        return redirect('periodization:detail_meso', meso_id=meso.id)


class TambahTargetPerformaView(ProRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, meso_id):
        meso = get_object_or_404(get_meso_cycle_queryset(request.user), pk=meso_id)
        nama_test = request.POST.get('nama_test', '').strip()
        nilai_target_raw = request.POST.get('nilai_target', '')

        if not nama_test or not nilai_target_raw:
            messages.error(request, "Nama test dan nilai target wajib diisi.")
            return redirect('periodization:detail_meso', meso_id=meso.id)

        try:
            nilai_target = float(nilai_target_raw)
        except ValueError:
            messages.error(request, "Nilai target harus berupa angka.")
            return redirect('periodization:detail_meso', meso_id=meso.id)

        TargetPerforma.objects.create(
            meso_cycle=meso,
            pilar=request.POST.get('pilar', 'CUSTOM'),
            nama_test=nama_test,
            nilai_target=nilai_target,
            satuan=request.POST.get('satuan', '').strip(),
            catatan=request.POST.get('catatan', '').strip(),
        )
        messages.success(request, f"Target '{nama_test}' ditambahkan.")
        return redirect('periodization:detail_meso', meso_id=meso.id)


class HapusTargetPerformaView(ProRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, target_id):
        target = get_object_or_404(TargetPerforma.objects.filter(
            meso_cycle__in=get_meso_cycle_queryset(request.user)
        ), pk=target_id)
        meso_id = target.meso_cycle_id
        target.delete()
        messages.success(request, "Target performa dihapus.")
        return redirect('periodization:detail_meso', meso_id=meso_id)


class TambahMicroCycleView(ProRequiredMixin, LoginRequiredMixin, View):
    """Tambah 1 minggu (MicroCycle) manual di dalam 1 MesoCycle."""
    def post(self, request, meso_id):
        meso = get_object_or_404(get_meso_cycle_queryset(request.user), pk=meso_id)
        try:
            minggu_ke = int(request.POST.get('minggu_ke', ''))
            tanggal_mulai = date.fromisoformat(request.POST.get('tanggal_mulai', ''))
        except (ValueError, TypeError):
            messages.error(request, "Minggu ke- dan tanggal mulai wajib diisi dengan benar.")
            return redirect('periodization:detail_meso', meso_id=meso.id)

        if meso.micro_cycles.filter(minggu_ke=minggu_ke).exists():
            messages.error(request, f"Minggu ke-{minggu_ke} sudah ada di fase ini.")
            return redirect('periodization:detail_meso', meso_id=meso.id)

        MicroCycle.objects.create(
            meso_cycle=meso,
            minggu_ke=minggu_ke,
            tanggal_mulai=tanggal_mulai,
            catatan=request.POST.get('catatan', '').strip(),
        )
        messages.success(request, f"Minggu ke-{minggu_ke} ditambahkan.")
        return redirect('periodization:detail_meso', meso_id=meso.id)


# ----------------------------------------------------------------------
# DETAIL MICROCYCLE (7 hari, sesi latihan per hari)
# ----------------------------------------------------------------------

class DetailMicroCycleView(ProRequiredMixin, LoginRequiredMixin, View):
    template_name = 'periodization/detail_micro.html'

    def get(self, request, micro_id):
        micro = get_object_or_404(get_micro_cycle_queryset(request.user), pk=micro_id)
        sesi_per_hari = {}
        for s in micro.sesi_latihan.all():
            sesi_per_hari.setdefault(s.hari_ke, []).append(s)
        hari_list = [
            {'hari_ke': h, 'nama_hari': NAMA_HARI[h], 'sesi_list': sesi_per_hari.get(h, [])}
            for h in range(1, 8)
        ]
        return render(request, self.template_name, {
            'micro': micro,
            'hari_list': hari_list,
            'pilar_fokus_choices': PILAR_FOKUS_HARIAN_CHOICES,
            'waktu_sesi_choices': WAKTU_SESI_CHOICES,
            'sibling_micro_list': micro.meso_cycle.micro_cycles.order_by('minggu_ke'),
        })


class TambahSesiLatihanView(ProRequiredMixin, LoginRequiredMixin, View):
    """
    Buat/update sesi latihan 1 hari tertentu (hari_ke 1-7) dalam 1
    MicroCycle. Kalau hari itu sudah ada sesinya, di-update -- bukan
    duplikat -- supaya pelatih bisa edit dari form yang sama.
    """
    def post(self, request, micro_id):
        micro = get_object_or_404(get_micro_cycle_queryset(request.user), pk=micro_id)
        try:
            hari_ke = int(request.POST.get('hari_ke', ''))
        except (ValueError, TypeError):
            messages.error(request, "Hari tidak valid.")
            return redirect('periodization:detail_micro', micro_id=micro.id)

        if hari_ke < 1 or hari_ke > 7:
            messages.error(request, "Hari harus antara 1 (Senin) sampai 7 (Minggu).")
            return redirect('periodization:detail_micro', micro_id=micro.id)

        waktu_sesi = request.POST.get('waktu_sesi', 'SORE')

        try:
            durasi_menit = int(request.POST.get('durasi_menit', 0) or 0)
            intensitas = int(request.POST.get('intensitas', 5) or 5)
        except ValueError:
            messages.error(request, "Durasi & intensitas harus berupa angka.")
            return redirect('periodization:detail_micro', micro_id=micro.id)

        SesiLatihan.objects.update_or_create(
            micro_cycle=micro,
            hari_ke=hari_ke,
            waktu_sesi=waktu_sesi,
            defaults={
                'nama_sesi': request.POST.get('nama_sesi', '').strip(),
                'pilar_fokus': request.POST.get('pilar_fokus', 'REST'),
                'durasi_menit': durasi_menit,
                'intensitas': intensitas,
                'catatan': request.POST.get('catatan', '').strip(),
            }
        )
        messages.success(request, f"Sesi hari ke-{hari_ke} ({dict(WAKTU_SESI_CHOICES).get(waktu_sesi, waktu_sesi)}) disimpan.")
        return redirect('periodization:detail_micro', micro_id=micro.id)


class HapusSesiLatihanView(ProRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, sesi_id):
        sesi = get_object_or_404(get_sesi_latihan_queryset(request.user), pk=sesi_id)
        micro_id = sesi.micro_cycle_id
        sesi.delete()
        messages.success(request, "Sesi latihan dihapus.")
        return redirect('periodization:detail_micro', micro_id=micro_id)


# ----------------------------------------------------------------------
# DETAIL SESI LATIHAN (exercise / set / rep / istirahat)
# ----------------------------------------------------------------------

class DetailSesiLatihanView(ProRequiredMixin, LoginRequiredMixin, View):
    template_name = 'periodization/detail_sesi.html'

    def get(self, request, sesi_id):
        sesi = get_object_or_404(get_sesi_latihan_queryset(request.user), pk=sesi_id)
        semua_item = list(sesi.latihan_items.all())

        kategori_groups = []
        for kode, label in KATEGORI_LATIHAN_CHOICES:
            items = [i for i in semua_item if i.kategori == kode]
            if items:
                kategori_groups.append({'kode': kode, 'label': label, 'items': items})

        sesi_per_hari = {}
        for s in sesi.micro_cycle.sesi_latihan.all():
            sesi_per_hari.setdefault(s.hari_ke, []).append(s)
        hari_list = [
            {'hari_ke': h, 'nama_hari': NAMA_HARI[h], 'sesi_list': sesi_per_hari.get(h, [])}
            for h in range(1, 8)
        ]

        return render(request, self.template_name, {
            'sesi': sesi,
            'kategori_groups': kategori_groups,
            'kategori_choices': KATEGORI_LATIHAN_CHOICES,
            'nama_hari': NAMA_HARI[sesi.hari_ke],
            'hari_list': hari_list,
        })


class TambahLatihanItemView(ProRequiredMixin, LoginRequiredMixin, View):
    """
    Bulk-add -- terima banyak baris exercise sekaligus dari 1 form
    (ala isi tabel Excel), bukan 1 exercise per submit. Setiap field
    dikirim sebagai array (nama_latihan[], jumlah_set[], dst) dengan
    index yang selaras antar array; baris dengan nama_latihan kosong
    dilewati (dianggap baris kosong yang tidak diisi pelatih).
    """
    def post(self, request, sesi_id):
        sesi = get_object_or_404(get_sesi_latihan_queryset(request.user), pk=sesi_id)

        kategori_list  = request.POST.getlist('kategori[]')
        nama_list      = request.POST.getlist('nama_latihan[]')
        set_list       = request.POST.getlist('jumlah_set[]')
        rep_list       = request.POST.getlist('jumlah_rep[]')
        waktu_list     = request.POST.getlist('waktu[]')
        istirahat_list = request.POST.getlist('durasi_istirahat_detik[]')
        beban_list     = request.POST.getlist('beban_intensitas[]')
        catatan_list   = request.POST.getlist('catatan[]')
        link_list      = request.POST.getlist('link_video[]')

        def ambil(lst, i, default=''):
            return lst[i].strip() if i < len(lst) and lst[i] else default

        urutan_berikutnya = (sesi.latihan_items.count() or 0) + 1
        items_baru = []

        for i in range(len(nama_list)):
            nama = ambil(nama_list, i)
            if not nama:
                continue  # baris kosong dari form Excel-style, lewati

            try:
                jumlah_set = int(ambil(set_list, i, '1') or 1)
            except ValueError:
                jumlah_set = 1
            try:
                durasi_istirahat_detik = int(ambil(istirahat_list, i, '60') or 60)
            except ValueError:
                durasi_istirahat_detik = 60

            items_baru.append(LatihanItem(
                sesi_latihan=sesi,
                urutan=urutan_berikutnya + len(items_baru),
                kategori=ambil(kategori_list, i, 'INTI'),
                nama_latihan=nama,
                jumlah_set=jumlah_set,
                jumlah_rep=ambil(rep_list, i),
                waktu=ambil(waktu_list, i),
                beban_intensitas=ambil(beban_list, i),
                durasi_istirahat_detik=durasi_istirahat_detik,
                link_video=ambil(link_list, i),
                catatan=ambil(catatan_list, i),
            ))

        if not items_baru:
            messages.error(request, "Tidak ada baris exercise yang diisi.")
            return redirect('periodization:detail_sesi', sesi_id=sesi.id)

        LatihanItem.objects.bulk_create(items_baru)
        messages.success(request, f"{len(items_baru)} exercise ditambahkan.")
        return redirect('periodization:detail_sesi', sesi_id=sesi.id)


class HapusLatihanItemView(ProRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, item_id):
        item = get_object_or_404(get_latihan_item_queryset(request.user), pk=item_id)
        sesi_id = item.sesi_latihan_id
        item.delete()
        messages.success(request, "Item latihan dihapus.")
        return redirect('periodization:detail_sesi', sesi_id=sesi_id)


# ----------------------------------------------------------------------
# CETAK BLANGKO TAHUNAN (PDF) -- format wall-chart ala KONI
# ----------------------------------------------------------------------

FASE_LABEL_BLANGKO = {
    'GPP': 'Persiapan Umum',
    'SPP': 'P. Khusus',
    'PRE_COMP': 'Pra-Kompetisi',
    'COMP': 'Kompetisi',
    'TRANSISI': 'Transisi',
}

FASE_WARNA_BLANGKO = {
    'GPP': '#dbeafe',
    'SPP': '#dcfce7',
    'PRE_COMP': '#fef3c7',
    'COMP': '#fee2e2',
    'TRANSISI': '#f3f4f6',
}


def _cari_meso_untuk_minggu(meso_list, tanggal_minggu):
    for m in meso_list:
        if m.tanggal_mulai <= tanggal_minggu <= m.tanggal_selesai:
            return m
    return None


def _bangun_pdf_blangko_tahunan(program):
    """
    Bangun PDF wall-chart periodisasi tahunan (format ala KONI) dari
    data MacroProgram -- Bulan/Minggu dari tanggal program, Fase dari
    MesoCycle, baris Strength/Speed/Flexibility/Endurance dipetakan
    dari fokus_l1-4_persen & volume_target (lihat catatan pemetaan di
    penjelasan fitur ini -- L1-L4 HPCS tidak 1:1 sama dengan 5
    komponen motorik klasik, jadi ini pendekatan terbaik yang bisa
    ditarik otomatis).
    """
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    styles = getSampleStyleSheet()
    style_judul = ParagraphStyle('judul', parent=styles['Title'], fontSize=14, spaceAfter=4)
    style_sub = ParagraphStyle('sub', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#6b7280'))
    style_sel = ParagraphStyle('sel', parent=styles['Normal'], fontSize=6.5, leading=8, alignment=TA_CENTER)
    style_label = ParagraphStyle('label', parent=styles['Normal'], fontSize=7, leading=8.5, fontName='Helvetica-Bold')

    meso_list = list(program.meso_cycles.order_by('urutan'))
    kompetisi_list = list(program.kompetisi_list.all())
    total_minggu = max(program.durasi_minggu, 1)

    minggu_tanggal = [program.tanggal_mulai + _timedelta(weeks=i) for i in range(total_minggu)]
    meso_per_minggu = [_cari_meso_untuk_minggu(meso_list, t) for t in minggu_tanggal]

    # --- baris Bulan (merge kolom minggu yang bulannya sama) ---
    baris_bulan = []
    for t in minggu_tanggal:
        baris_bulan.append(t.strftime('%b %Y'))

    # --- baris Minggu (nomor urut) ---
    baris_minggu_no = [str(i + 1) for i in range(total_minggu)]

    # --- baris Fase ---
    baris_fase = [FASE_LABEL_BLANGKO.get(m.nama_fase, '-') if m else '-' for m in meso_per_minggu]

    # --- baris % (volume_target x10, skala 1-10 jadi 10-100%) ---
    baris_persen = [f"{m.volume_target * 10}%" if m else '-' for m in meso_per_minggu]

    # --- baris Test/Tryout ---
    baris_test = ['' for _ in range(total_minggu)]
    for k in kompetisi_list:
        for i, t in enumerate(minggu_tanggal):
            akhir_minggu = t + _timedelta(days=6)
            if t <= k.tanggal_mulai <= akhir_minggu:
                baris_test[i] = k.nama_kompetisi[:14]
                break

    # --- baris kualitas fisik (dipetakan dari fokus_l1-4 & volume) ---
    baris_strength   = [f"{m.fokus_l2_persen}%" if m else '-' for m in meso_per_minggu]
    baris_speed      = [f"{m.fokus_l4_persen}%" if m else '-' for m in meso_per_minggu]
    baris_flex       = [f"{m.fokus_l1_persen}%" if m else '-' for m in meso_per_minggu]
    baris_endurance  = [f"Vol {m.volume_target}/10" if m else '-' for m in meso_per_minggu]

    # --- baris teks per fase (Technique/Tactic/Mental/Objective) ---
    def teks_per_minggu(attr):
        return [getattr(m, attr, '') or '-' if m else '-' for m in meso_per_minggu]

    baris_teknik   = teks_per_minggu('objektif_teknik')
    baris_taktik   = teks_per_minggu('objektif_taktik')
    baris_mental   = teks_per_minggu('objektif_mental')
    baris_objektif = teks_per_minggu('objektif_fisik')

    def buat_sel_paragraf(teks):
        return Paragraph(str(teks), style_sel)

    def buat_baris_merge(nama_baris, nilai_list, warna_fase=False):
        """Baris dengan sel di-merge kalau nilai berturutan sama (biar nggak berulang tiap minggu).
        PENTING: tetap harus isi sel placeholder kosong buat tiap kolom yang ke-span --
        reportlab Table butuh jumlah sel di data sama persis dengan jumlah kolom,
        SPAN cuma menyembunyikan visualnya, bukan menghilangkan slotnya."""
        row = [Paragraph(nama_baris, style_label)]
        span_commands = []
        col = 1
        i = 0
        while i < len(nilai_list):
            j = i
            while j + 1 < len(nilai_list) and nilai_list[j + 1] == nilai_list[i]:
                j += 1
            row.append(buat_sel_paragraf(nilai_list[i]))
            for _ in range(j - i):
                row.append(buat_sel_paragraf(''))  # placeholder kolom yang ke-span
            if j > i:
                span_commands.append(('SPAN', (col, '__ROW__'), (col + (j - i), '__ROW__')))
            col += (j - i) + 1
            i = j + 1
        return row, span_commands

    header_bulan = ['Bulan'] + [Paragraph(b, style_sel) for b in baris_bulan]
    header_minggu = ['Minggu'] + [Paragraph(m, style_sel) for m in baris_minggu_no]

    data = [header_bulan, header_minggu]
    row_span_map = {}  # row_index -> list of (col_start, col_end)

    def tambah_baris(nama, nilai_list):
        row, spans = buat_baris_merge(nama, nilai_list)
        data.append(row)
        row_span_map[len(data) - 1] = spans

    tambah_baris('Fase', baris_fase)
    tambah_baris('% Volume', baris_persen)
    tambah_baris('Test/Tryout', baris_test)
    tambah_baris('Strength', baris_strength)
    tambah_baris('Speed', baris_speed)
    tambah_baris('Flexibility', baris_flex)
    tambah_baris('Endurance', baris_endurance)
    tambah_baris('Technique', baris_teknik)
    tambah_baris('Tactic', baris_taktik)
    tambah_baris('Mental', baris_mental)
    tambah_baris('Objective', baris_objektif)

    row_fase_index = 2  # index baris 'Fase' di data (setelah 2 header)

    # --- style tabel ---
    table_style_cmds = [
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d1d5db')),
        ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#111826')),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (0, -1), colors.HexColor('#f3f4f6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
    ]

    # Terapkan SPAN commands, ganti placeholder '__ROW__' dengan index baris asli
    for row_idx, spans in row_span_map.items():
        for cmd in spans:
            _, (c1, _), (c2, _) = cmd
            table_style_cmds.append(('SPAN', (c1, row_idx), (c2, row_idx)))

    # Warna latar baris Fase sesuai warna fase (per grup merge)
    col = 1
    i = 0
    while i < len(baris_fase):
        j = i
        while j + 1 < len(baris_fase) and baris_fase[j + 1] == baris_fase[i]:
            j += 1
        meso_disini = meso_per_minggu[i]
        if meso_disini:
            warna = FASE_WARNA_BLANGKO.get(meso_disini.nama_fase, '#ffffff')
            table_style_cmds.append(('BACKGROUND', (col, row_fase_index), (col + (j - i), row_fase_index), colors.HexColor(warna)))
        col += (j - i) + 1
        i = j + 1

    col_widths = [26 * mm] + [max(6, min(11, 240 / total_minggu)) * mm] * total_minggu

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A3), leftMargin=10 * mm, rightMargin=10 * mm, topMargin=10 * mm, bottomMargin=10 * mm)

    elemen = []
    elemen.append(Paragraph(f"Program Periodisasi Tahunan - {program.nama_program}", style_judul))
    elemen.append(Paragraph(
        f"{program.atlet.nama_atlet} &middot; {program.get_event_target_display()}"
        f"{' (' + program.nama_event + ')' if program.nama_event else ''} &middot; "
        f"{program.tanggal_mulai.strftime('%d %b %Y')} - {program.tanggal_target.strftime('%d %b %Y')}",
        style_sub
    ))
    elemen.append(Spacer(1, 8 * mm))

    tabel = Table(data, colWidths=col_widths, repeatRows=2)
    tabel.setStyle(TableStyle(table_style_cmds))
    elemen.append(tabel)

    doc.build(elemen)
    buf.seek(0)
    return buf


class CetakBlangkoTahunanView(ProRequiredMixin, LoginRequiredMixin, View):
    """
    Generate & download PDF blangko periodisasi tahunan ala KONI,
    ditarik otomatis dari MacroProgram + MesoCycle + KompetisiTarget.
    Butuh library reportlab (pip install reportlab).
    """
    def get(self, request, program_id):
        program = get_object_or_404(get_macro_program_queryset(request.user), pk=program_id)

        if not program.meso_cycles.exists():
            messages.error(request, "Belum ada MesoCycle di program ini. Generate periodisasi dulu sebelum cetak blangko.")
            return redirect('periodization:detail_program', program_id=program.id)

        try:
            buf = _bangun_pdf_blangko_tahunan(program)
        except ImportError:
            messages.error(request, "Library 'reportlab' belum terpasang. Jalankan: pip install reportlab")
            return redirect('periodization:detail_program', program_id=program.id)

        nama_file = f"Blangko_Periodisasi_{program.nama_program.replace(' ', '_')}.pdf"
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nama_file}"'
        return response