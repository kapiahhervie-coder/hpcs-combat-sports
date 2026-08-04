"""
HPCS Combat Sports - Views
TODO: Role-based access control akan diimplementasikan setelah Custom User Model dibuat
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import View
from django.http import JsonResponse
import json

from .models import (
    Atlet,
    CorrectionAuditL1,
    StrengthAuditL2,
    PowerAuditL3,
    RekomendasiProgram,
    SpeedAgilityAuditL4,
    ProfilPelatih,
)
from .permissions import get_atlet_queryset, is_admin



# ══════════════════════════════════════════════════════════════════════
# DASHBOARD UTAMA
# ══════════════════════════════════════════════════════════════════════

CABOR_DASHBOARD_URL = {
    'boxing': 'combat:dashboard_boxing',
    'muaythai': 'combat:dashboard_muaythai',
    'tkd': 'taekwondo:dashboard',
}


class DashboardView(LoginRequiredMixin, View):
    template_name = 'combat/dashboard_combat.html'

    def get(self, request):
        if not (request.user.is_superuser or request.user.is_staff):
            profil = getattr(request.user, 'profil_pelatih', None)
            if profil and profil.cabang in CABOR_DASHBOARD_URL:
                return redirect(CABOR_DASHBOARD_URL[profil.cabang])
        squad_atlet = get_atlet_queryset(request.user)
        audit_l1    = CorrectionAuditL1.objects.all()
        audit_l2    = StrengthAuditL2.objects.all()
        audit_l3    = PowerAuditL3.objects.all()
        audit_l4    = SpeedAgilityAuditL4.objects.all()

        total_atlet = squad_atlet.count()
        total_l1    = audit_l1.count()
        total_l2    = audit_l2.count()
        total_l3    = audit_l3.count()
        total_l4    = audit_l4.count()

        atlet_terbaru    = squad_atlet.order_by('-dibuat_pada')[:5]
        audit_l1_terbaru = audit_l1.order_by('-timestamp')[:5]
        audit_l2_terbaru = audit_l2.order_by('-timestamp')[:5]
        audit_l3_terbaru = audit_l3.order_by('-timestamp')[:5]

        l1_layak = audit_l1.filter(layak_naik=True).count()
        l2_layak = audit_l2.filter(layak_naik=True).count()
        l3_layak = audit_l3.filter(layak_naik=True).count()

        distribusi_cabor = [
            {
                'cabor': {'nama': 'Boxing'},
                'total': get_atlet_queryset(request.user).filter(cabang__iexact='boxing').count(),
                'rata_level': 'L2',
                'status': 'Baik',
                'pct_audit': 75,
            },
            {
                'cabor': {'nama': 'Muay Thai'},
                'total': get_atlet_queryset(request.user).filter(cabang__iexact='muaythai').count(),
                'rata_level': '-',
                'status': 'Cukup',
                'pct_audit': 0,
            },
            {
    'cabor': {'nama': 'Karate'},
    'total': get_atlet_queryset(request.user).filter(cabang__iexact='krt').count(),
    'rata_level': '-',
    'status': 'Cukup',
    'pct_audit': 0,
},
            {
                'cabor': {'nama': 'Taekwondo'},
                'total': get_atlet_queryset(request.user).filter(cabang__iexact='tkd').count(),
                'rata_level': '-',
                'status': 'Cukup',
                'pct_audit': 0,
            },
        ]

        context = {
            'total_atlet':      total_atlet,
            'total_l1':         total_l1,
            'total_l2':         total_l2,
            'total_l3':         total_l3,
            'total_l4':         total_l4,
            'atlet_terbaru':    atlet_terbaru,
            'audit_l1_terbaru': audit_l1_terbaru,
            'audit_l2_terbaru': audit_l2_terbaru,
            'audit_l3_terbaru': audit_l3_terbaru,
            'l1_layak':         l1_layak,
            'l2_layak':         l2_layak,
            'l3_layak':         l3_layak,
            'distribusi_cabor': distribusi_cabor,
            'total_atlet_muaythai': squad_atlet.filter(cabang__iexact='muaythai').count(),
            'total_atlet_taekwondo': squad_atlet.filter(cabang__iexact='tkd').count(),
            'total_atlet_karate': squad_atlet.filter(cabang__iexact='krt').count(),
        }
        return render(request, self.template_name, context)


# ══════════════════════════════════════════════════════════════════════
# ATHLETE INTELLIGENCE REPORT (NEW REPORT CARD)
# ══════════════════════════════════════════════════════════════════════

class AthleteIntelligenceReportView(LoginRequiredMixin, View):
    template_name = 'combat/athlete_report.html'

    def get(self, request, atlet_id):
        atlet = get_object_or_404(Atlet, pk=atlet_id)

        l1_latest = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l2_latest = StrengthAuditL2.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l3_latest = PowerAuditL3.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l4_latest = SpeedAgilityAuditL4.objects.filter(atlet=atlet).order_by('-timestamp').first()

        def normalisasi_ke_100(skor):
            if not skor:
                return 0.0
            val = float(skor)
            return val if val > 10 else val * 10.0

        score_foundation  = normalisasi_ke_100(l1_latest.total_skor if l1_latest else 0)
        score_force       = normalisasi_ke_100(l2_latest.total_skor if l2_latest else 0)
        score_power       = normalisasi_ke_100(l3_latest.total_skor if l3_latest else 0)
        score_athleticism = normalisasi_ke_100(l4_latest.total_skor if l4_latest else 0)

        score_skill       = 71.0  # Default premium sesuai visual rancangan target

        total_sum = score_foundation + score_force + score_power + score_athleticism
        score_readiness = round(total_sum / 4, 1) if total_sum > 0 else 87.0

        months_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

        trend_data = {
            'foundation': [60, 62, 65, 68, 72, score_foundation or 82],
            'force':      [55, 58, 60, 62, 68, score_force or 75],
            'power':      [70, 75, 74, 80, 85, score_power or 90],
            'athleticism': [40, 42, 45, 48, 52, score_athleticism or 78],
            'skill':       [65, 66, 68, 70, 70, score_skill],
            'readiness':   [58, 61, 62, 65, 69, score_readiness]
        }

        context = {
            'atlet': atlet,
            'readiness': score_readiness,
            'scores': {
                'foundation': score_foundation or 82,
                'force': score_force or 75,
                'power': score_power or 90,
                'athleticism': score_athleticism or 78,
                'skill': score_skill,
            },
            'radar_data_json': json.dumps([
                score_foundation or 82,
                score_force or 75,
                score_power or 90,
                score_athleticism or 78,
                score_skill,
                score_readiness
            ]),
            'trend_data_json': json.dumps(trend_data),
            'months_labels_json': json.dumps(months_labels),
            'l1': l1_latest,
            'l2': l2_latest,
            'l3': l3_latest,
            'l4': l4_latest,
        }

        return render(request, self.template_name, context)


class ReportCardView(LoginRequiredMixin, View):
    template_name = 'combat/report_card.html'

    def get(self, request, atlet_id):
        from django.utils import timezone
        atlet = get_object_or_404(Atlet, pk=atlet_id)

        l1 = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l2 = StrengthAuditL2.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l3 = PowerAuditL3.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l4 = SpeedAgilityAuditL4.objects.filter(atlet=atlet).order_by('-timestamp').first()

        s1 = round(l1.total_skor * 10, 1) if l1 else 0
        s2 = round(l2.total_skor * 10, 1) if l2 else 0
        s3 = round(l3.total_skor * 10, 1) if l3 else 0
        s4 = round(l4.total_skor * 10, 1) if l4 else 0
        overall_100 = round((s1 + s2 + s3 + s4) / max(sum([1 for x in [s1, s2, s3, s4] if x > 0]), 1), 1)

        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN']

        context = {
            'atlet': atlet,
            'l1': l1, 'l2': l2, 'l3': l3, 'l4': l4,
            'readiness': overall_100,
            'radar_data_json': json.dumps([s1, s2, s3, s4, s2, overall_100]),
            'trend_data_json': json.dumps({
                'power':       [s3 * 0.6, s3 * 0.7, s3 * 0.8, s3 * 0.85, s3 * 0.9, s3],
                'readiness':   [overall_100 * 0.6, overall_100 * 0.7, overall_100 * 0.75, overall_100 * 0.8, overall_100 * 0.9, overall_100],
                'athleticism': [s4 * 0.5, s4 * 0.6, s4 * 0.7, s4 * 0.8, s4 * 0.9, s4],
            }),
            'months_labels_json': json.dumps(months),
            'tanggal_cetak': timezone.now(),
        }
        return render(request, self.template_name, context)


class ReportCenterView(LoginRequiredMixin, View):
    template_name = 'combat/report_center.html'

    def get(self, request):
        from .models import CABANG_CHOICES

        cabang_filter = request.GET.get('cabang', '')
        atlet_qs = get_atlet_queryset(request.user)

        if cabang_filter:
            atlet_qs = atlet_qs.filter(cabang=cabang_filter)

        atlet_qs = atlet_qs.order_by('nama_atlet')

        atlet_data = []
        total_layak = 0
        total_risiko = 0

        for atlet in atlet_qs:
            l1 = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first()
            l2 = StrengthAuditL2.objects.filter(atlet=atlet).order_by('-timestamp').first()
            l3 = PowerAuditL3.objects.filter(atlet=atlet).order_by('-timestamp').first()
            l4 = SpeedAgilityAuditL4.objects.filter(atlet=atlet).order_by('-timestamp').first()

            scores = [
                round(l1.total_skor, 1) if l1 else 0,
                round(l2.total_skor, 1) if l2 else 0,
                round(l3.total_skor, 1) if l3 else 0,
                round(l4.total_skor, 1) if l4 else 0,
            ]
            scores_ada = [s for s in scores if s > 0]
            overall = round(sum(scores_ada) / len(scores_ada), 1) if scores_ada else 0

            if overall >= 9.0:
                overall_predikat = 'ELITE'
            elif overall >= 7.0:
                overall_predikat = 'READY'
            elif overall >= 5.0:
                overall_predikat = 'DEVELOPING'
            else:
                overall_predikat = 'NOVICE'

            if l3 and l3.layak_naik:
                total_layak += 1
            if atlet.risiko_cedera == 'TINGGI':
                total_risiko += 1

            atlet_data.append({
                'atlet': atlet,
                'l1': l1, 'l2': l2, 'l3': l3, 'l4': l4,
                'overall': overall,
                'overall_predikat': overall_predikat,
            })

        context = {
            'atlet_data': atlet_data,
            'total_atlet': atlet_qs.count(),
            'total_layak': total_layak,
            'total_risiko': total_risiko,
            'cabang_choices': CABANG_CHOICES,
        }
        return render(request, self.template_name, context)


# ══════════════════════════════════════════════════════════════════════
# COACH REGISTRATION & MANAGEMENT
# ══════════════════════════════════════════════════════════════════════

from django.contrib.auth import login as auth_login


class DaftarCoachView(View):
    template_name = 'combat/daftar_coach.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('combat:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        nama_lengkap = request.POST.get('nama_lengkap', '').strip()
        username     = request.POST.get('username', '').strip()
        password1    = request.POST.get('password1', '')
        password2    = request.POST.get('password2', '')
        cabang       = request.POST.get('cabang', '')
        email        = request.POST.get('email', '').strip()
        no_hp        = request.POST.get('no_hp', '').strip()
        foto         = request.FILES.get('foto')

        if password1 != password2:
            messages.error(request, 'Password tidak cocok.')
            return render(request, self.template_name)
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" sudah dipakai.')
            return render(request, self.template_name)
        if len(password1) < 6:
            messages.error(request, 'Password minimal 6 karakter.')
            return render(request, self.template_name)

        nama_parts = nama_lengkap.split(' ', 1)
        user = User.objects.create_user(
            username=username, password=password1,
            first_name=nama_parts[0],
            last_name=nama_parts[1] if len(nama_parts) > 1 else '',
            email=email,
        )
        profil = ProfilPelatih(user=user, cabang=cabang, no_hp=no_hp, email=email, status='approved')
        if foto:
            profil.foto = foto
        profil.save()
        auth_login(request, user)
        return redirect(CABOR_DASHBOARD_URL.get(cabang, 'combat:dashboard'))


class TungguApprovalView(LoginRequiredMixin, View):
    template_name = 'combat/tunggu_approval.html'

    def get(self, request):
        profil = getattr(request.user, 'profil_pelatih', None)
        if request.user.is_superuser or request.user.is_staff:
            return redirect('combat:dashboard')
        if profil and profil.is_approved:
            return redirect('combat:dashboard')
        return render(request, self.template_name, {'profil': profil})


class AdminCoachView(LoginRequiredMixin, View):
    template_name = 'combat/admin_coach.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Akses ditolak.')
            return redirect('combat:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        pending_list  = ProfilPelatih.objects.filter(status='pending').select_related('user').order_by('-dibuat_pada')
        approved_list = ProfilPelatih.objects.filter(status='approved').select_related('user').order_by('user__first_name')
        rejected_list = ProfilPelatih.objects.filter(status='rejected').select_related('user').order_by('-dibuat_pada')
        semua_atlet = Atlet.objects.all().order_by('nama_atlet')
        atlet_bebas = Atlet.objects.filter(pelatih__isnull=True).order_by('nama_atlet')
        return render(request, self.template_name, {
            'pending_list':   pending_list,
            'approved_list':  approved_list,
            'rejected_list':  rejected_list,
            'total_pending':  pending_list.count(),
            'total_approved': approved_list.count(),
            'total_rejected': rejected_list.count(),
            'total_semua':    ProfilPelatih.objects.count(),
            'semua_atlet':    semua_atlet,
            'atlet_bebas':    atlet_bebas,
        })

    def post(self, request):
        action, profil_id = request.POST.get('action'), request.POST.get('profil_id')
        try:
            profil = ProfilPelatih.objects.get(pk=profil_id)
            nama = profil.user.get_full_name() or profil.user.username
            if action == 'approve':
                profil.status = 'approved'
                profil.save()
                messages.success(request, f'{nama} berhasil disetujui.')
                try:
                    from django.core.mail import send_mail
                    email_tujuan = profil.email or profil.user.email
                    if email_tujuan:
                        send_mail(
                            subject='[HPCS] Akun Coach Anda Telah Disetujui',
                            message=f"""Halo {nama},

Selamat! Akun coach Anda di HPCS Combat Sports telah disetujui oleh administrator.

Detail akun:
- Username : {profil.user.username}
- Cabang   : {profil.get_cabang_display()}

Silakan login sekarang di:
http://127.0.0.1:8000/accounts/login/

Salam,
Tim HPCS Combat Sports""",
                            from_email=None,
                            recipient_list=[email_tujuan],
                            fail_silently=True,
                        )
                except Exception:
                    pass
            elif action == 'reject':
                profil.status = 'rejected'
                profil.save()
                messages.error(request, f'{nama} ditolak.')
            elif action == 'revoke':
                profil.status = 'pending'
                profil.save()
                messages.error(request, f'Akses {nama} dicabut.')
        except ProfilPelatih.DoesNotExist:
            messages.error(request, 'Data tidak ditemukan.')
        return redirect('combat:admin_coach')


# ══════════════════════════════════════════════════════════════════════
# ASSIGN ATLET KE COACH
# ══════════════════════════════════════════════════════════════════════

class AssignAtletCoachView(LoginRequiredMixin, View):
    """Admin assign/unassign atlet ke coach tertentu."""

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Akses ditolak.')
            return redirect('combat:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        action    = request.POST.get('action')
        atlet_id  = request.POST.get('atlet_id')
        coach_id  = request.POST.get('coach_id')

        try:
            atlet = Atlet.objects.get(pk=atlet_id)
            if action == 'assign':
                coach = User.objects.get(pk=coach_id)
                atlet.pelatih = coach
                atlet.save()
                messages.success(request, f'{atlet.nama_atlet} berhasil di-assign ke {coach.get_full_name() or coach.username}.')
            elif action == 'unassign':
                nama_coach = atlet.pelatih.get_full_name() if atlet.pelatih else '-'
                atlet.pelatih = None
                atlet.save()
                messages.success(request, f'{atlet.nama_atlet} dilepas dari {nama_coach}.')
        except (Atlet.DoesNotExist, User.DoesNotExist):
            messages.error(request, 'Data tidak ditemukan.')

        return redirect('combat:admin_coach')


# ══════════════════════════════════════════════════════════════════════
# TAMBAH ATLET (oleh Coach)
# ══════════════════════════════════════════════════════════════════════
# CATATAN: sebelumnya class ini terduplikasi 3x berturut-turut di file asli
# (identik persis). Hanya definisi terakhir yang pernah benar-benar dipakai
# Python (definisi sebelumnya jadi dead code tertimpa). Di sini disisakan
# satu saja.

class TambahAtletView(LoginRequiredMixin, View):
    """Coach menambahkan atlet baru yang langsung jadi binaannya."""
    template_name = 'combat/tambah_atlet.html'

    def get_back_url(self, request):
        posted = request.POST.get('back_url')
        if posted:
            return posted
        ref = request.META.get('HTTP_REFERER', '')
        host = request.get_host()
        if ref and host in ref:
            from urllib.parse import urlparse
            return urlparse(ref).path
        return '/combat/'

    def get(self, request):
        return render(request, self.template_name, {'back_url': self.get_back_url(request)})

    def post(self, request):
        try:
            nama        = request.POST.get('nama_atlet', '').strip()
            kategori    = request.POST.get('kategori_umur', '')
            gender      = request.POST.get('gender', '')
            kelas_berat = request.POST.get('kelas_berat', '')
            tinggi      = request.POST.get('tinggi_badan', '') or None
            tgl_lahir   = request.POST.get('tanggal_lahir', '') or None
            cabang      = request.POST.get('cabang', '')
            tahap_ltad  = request.POST.get('tahap_ltad', '')

            if not nama or not kategori or not gender or not kelas_berat:
                messages.error(request, 'Nama, kategori usia, gender, dan berat badan wajib diisi.')
                return render(request, self.template_name)

            atlet = Atlet(
                nama_atlet    = nama,
                kategori_umur = kategori,
                gender        = gender,
                kelas_berat   = float(kelas_berat),
                tinggi_badan  = float(tinggi) if tinggi else None,
                tanggal_lahir = tgl_lahir,
                cabang        = cabang,
                tahap_ltad    = tahap_ltad,
                pelatih       = request.user,
            )
            atlet.save()
            messages.success(request, f'Atlet {nama} berhasil ditambahkan!')
            return redirect('combat:tambah_atlet')

        except Exception as e:
            messages.error(request, f'Gagal menyimpan: {e}')
            return render(request, self.template_name, {'back_url': self.get_back_url(request)})


