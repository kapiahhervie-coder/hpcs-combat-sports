"""
periodization/views.py
Tahap 3 HPCS -- Views & Routing untuk Pilar 3 (Periodisasi).

Semua view WAJIB scoped ke pelatih yang login (kecuali staff/superuser)
-- lihat get_macro_program_queryset(). Ini niru pola yang sudah
diperbaiki di semua app cabang (karate/muaythai/boxing/taekwondo)
supaya tidak mengulang bug IDOR yang sama di fitur baru ini.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views import View

from combat.models import Atlet
from .models import MacroProgram, MesoCycle
from .services import generate_periodisasi_otomatis


def get_macro_program_queryset(user):
    """Scoping kepemilikan: pelatih cuma lihat program milik atlet binaannya sendiri."""
    qs = MacroProgram.objects.select_related('atlet')
    if user.is_staff or user.is_superuser:
        return qs
    return qs.filter(atlet__pelatih=user)


def get_atlet_queryset_lokal(user):
    """Scoping yang sama, versi buat pilihan atlet di form Tambah Program."""
    qs = Atlet.objects.all()
    if user.is_staff or user.is_superuser:
        return qs
    return qs.filter(pelatih=user)


class DaftarMacroProgramView(LoginRequiredMixin, View):
    template_name = 'periodization/daftar_program.html'

    def get(self, request):
        daftar_program = get_macro_program_queryset(request.user).order_by('-tanggal_mulai')
        return render(request, self.template_name, {
            'daftar_program': daftar_program,
            'total_program': daftar_program.count(),
        })


class TambahMacroProgramView(LoginRequiredMixin, View):
    template_name = 'periodization/tambah_program.html'

    def get(self, request):
        daftar_atlet = get_atlet_queryset_lokal(request.user).order_by('nama_atlet')
        return render(request, self.template_name, {'daftar_atlet': daftar_atlet})

    def post(self, request):
        atlet_id = request.POST.get('atlet_id')
        atlet = get_object_or_404(get_atlet_queryset_lokal(request.user), pk=atlet_id)

        program = MacroProgram.objects.create(
            atlet=atlet,
            nama_program=request.POST.get('nama_program', '').strip(),
            event_target=request.POST.get('event_target', 'lainnya'),
            nama_event=request.POST.get('nama_event', '').strip(),
            tanggal_mulai=request.POST.get('tanggal_mulai'),
            tanggal_target=request.POST.get('tanggal_target'),
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


class DetailMacroProgramView(LoginRequiredMixin, View):
    template_name = 'periodization/detail_program.html'

    def get(self, request, program_id):
        program = get_object_or_404(get_macro_program_queryset(request.user), pk=program_id)
        meso_list = program.meso_cycles.order_by('urutan')
        return render(request, self.template_name, {
            'program': program,
            'meso_list': meso_list,
        })


class GenerateOtomatisView(LoginRequiredMixin, View):
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


class KurvaVolumeIntensitasView(LoginRequiredMixin, View):
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