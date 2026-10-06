from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .access import user_has_access
from . import calculators as calc


def _check_access(user):
    if not user_has_access(user):
            raise PermissionDenied("Fitur Kalkulator Fitness khusus akun Pro. Upgrade akun Anda untuk mengakses fitur ini.")


@login_required
def calc_bmi_bodyfat(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        berat = float(request.POST.get("berat"))
        tinggi = float(request.POST.get("tinggi"))
        usia = int(request.POST.get("usia"))
        gender = request.POST.get("gender", "L")
        hasil = calc.hitung_bmi_bodyfat(berat, tinggi, usia, gender)
    return render(request, "fitness/bmi_bodyfat.html", {"hasil": hasil})


@login_required
def calc_one_rep_max(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        berat = float(request.POST.get("berat_angkat"))
        rep = int(request.POST.get("repetisi"))
        hasil = calc.hitung_1rm(berat, rep)
    return render(request, "fitness/one_rep_max.html", {"hasil": hasil})


@login_required
def calc_tdee(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        berat = float(request.POST.get("berat"))
        tinggi = float(request.POST.get("tinggi"))
        usia = int(request.POST.get("usia"))
        gender = request.POST.get("gender", "L")
        aktivitas = float(request.POST.get("aktivitas"))
        hasil = calc.hitung_tdee(berat, tinggi, usia, gender, aktivitas)
    return render(request, "fitness/tdee.html", {"hasil": hasil})


@login_required
def calc_target_hr(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        usia = int(request.POST.get("usia"))
        hr_istirahat = request.POST.get("hr_istirahat")
        hr_istirahat = int(hr_istirahat) if hr_istirahat else None
        hasil = calc.hitung_target_hr(usia, hr_istirahat)
    return render(request, "fitness/target_heart_rate.html", {"hasil": hasil})


@login_required
def calc_vo2_12min(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        jarak = float(request.POST.get("jarak"))
        hasil = calc.hitung_vo2_12min(jarak)
    return render(request, "fitness/vo2_12min.html", {"hasil": hasil})


@login_required
def calc_risk(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        jumlah_faktor = int(request.POST.get("jumlah_faktor", 0))
        ada_gejala = request.POST.get("ada_gejala") == "on"
        hasil = calc.klasifikasi_risiko(jumlah_faktor, ada_gejala)
    return render(request, "fitness/risk_classification.html", {"hasil": hasil})


@login_required
def calc_denyut_nadi(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        usia = int(request.POST.get("usia"))
        denyut_istirahat = int(request.POST.get("denyut_istirahat"))
        denyut_latihan = request.POST.get("denyut_latihan")
        denyut_latihan = int(denyut_latihan) if denyut_latihan else None

        evaluasi_istirahat = calc.evaluasi_denyut_istirahat(denyut_istirahat)
        evaluasi_latihan = None
        if denyut_latihan:
            evaluasi_latihan = calc.evaluasi_denyut_latihan(usia, denyut_latihan, denyut_istirahat)

        hasil = {
            "istirahat": evaluasi_istirahat,
            "latihan": evaluasi_latihan,
        }
    return render(request, "fitness/denyut_nadi.html", {"hasil": hasil})


@login_required
def calc_pushup(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        usia = int(request.POST.get("usia"))
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_pushup(usia, gender, jumlah)
    return render(request, "fitness/pushup.html", {"hasil": hasil})


@login_required
def calc_situp(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        usia = int(request.POST.get("usia"))
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_situp(usia, gender, jumlah)
    return render(request, "fitness/situp.html", {"hasil": hasil})


@login_required
def calc_plank(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        usia = int(request.POST.get("usia"))
        detik = int(request.POST.get("detik"))
        hasil = calc.klasifikasi_plank(usia, detik)
    return render(request, "fitness/plank.html", {"hasil": hasil})


@login_required
def calc_squat(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        usia = int(request.POST.get("usia"))
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_squat(usia, gender, jumlah)
    return render(request, "fitness/squat.html", {"hasil": hasil})


@login_required
def calc_crunch(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        usia = int(request.POST.get("usia"))
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_crunch(usia, gender, jumlah)
    return render(request, "fitness/crunch.html", {"hasil": hasil})
