<#
=====================================================================
 UPDATE: Tambah Tes Kekuatan Otot (Push Up, Sit Up, Plank, Squat, Crunch)
 Jalankan dari root folder project (folder yang berisi manage.py)
=====================================================================
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Update: Tes Kekuatan Otot ===" -ForegroundColor Cyan

if (-not (Test-Path ".\manage.py")) {
    Write-Host "ERROR: manage.py tidak ditemukan. Pindah ke root project dulu." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path ".\fitness")) {
    Write-Host "ERROR: folder 'fitness' tidak ditemukan. Jalankan setup_fitness_calculator.ps1 dulu." -ForegroundColor Red
    exit 1
}

$templateDir = ".\fitness\templates\fitness"

# =====================================================================
# 1. calculators.py -> TIMPA lengkap (semua fungsi lama + 5 fungsi baru)
# =====================================================================
$calculators = @'
def hitung_bmi_bodyfat(berat, tinggi_cm, usia, gender):
    tinggi_m = tinggi_cm / 100
    bmi = round(berat / (tinggi_m ** 2), 2)
    if gender == "L":
        body_fat = round((1.20 * bmi) + (0.23 * usia) - 16.2, 1)
    else:
        body_fat = round((1.20 * bmi) + (0.23 * usia) - 5.4, 1)

    if bmi < 18.5:
        kategori = "Kurus"
    elif bmi < 25:
        kategori = "Normal"
    elif bmi < 30:
        kategori = "Gemuk"
    else:
        kategori = "Obesitas"

    return {"bmi": bmi, "body_fat": body_fat, "kategori": kategori}


def hitung_1rm(berat_angkat, repetisi):
    if repetisi == 1:
        return round(berat_angkat, 1)
    return round(berat_angkat * (1 + repetisi / 30), 1)


def hitung_target_hr(usia, hr_istirahat=None, persen_bawah=60, persen_atas=80):
    hr_max = 220 - usia
    if hr_istirahat:
        cadangan = hr_max - hr_istirahat
        bawah = round((cadangan * persen_bawah / 100) + hr_istirahat)
        atas = round((cadangan * persen_atas / 100) + hr_istirahat)
    else:
        bawah = round(hr_max * persen_bawah / 100)
        atas = round(hr_max * persen_atas / 100)
    return {"hr_max": hr_max, "zona_bawah": bawah, "zona_atas": atas}


def hitung_tdee(berat, tinggi, usia, gender, faktor_aktivitas):
    if gender == "L":
        bmr = (10 * berat) + (6.25 * tinggi) - (5 * usia) + 5
    else:
        bmr = (10 * berat) + (6.25 * tinggi) - (5 * usia) - 161
    return round(bmr * faktor_aktivitas, 1)


def hitung_vo2_12min(jarak_meter):
    vo2max = round((jarak_meter - 504.9) / 44.73, 1)
    if vo2max >= 51:
        rating = "Sangat Baik"
    elif vo2max >= 42:
        rating = "Baik"
    elif vo2max >= 34:
        rating = "Cukup"
    else:
        rating = "Kurang"
    return {"vo2max": vo2max, "rating": rating}


def klasifikasi_risiko(jumlah_faktor_risiko, ada_gejala):
    if ada_gejala:
        return {
            "level": "Tinggi",
            "saran": "Rujuk pemeriksaan medis sebelum mengikuti latihan intensitas tinggi."
        }
    elif jumlah_faktor_risiko >= 2:
        return {
            "level": "Sedang",
            "saran": "Disarankan konsultasi medis sebelum program latihan intensitas tinggi."
        }
    else:
        return {
            "level": "Rendah",
            "saran": "Aman untuk memulai program latihan bertahap."
        }


def evaluasi_denyut_istirahat(denyut_istirahat):
    if denyut_istirahat < 60:
        kategori = "Sangat Baik (umum pada atlet terlatih)"
    elif denyut_istirahat <= 70:
        kategori = "Baik"
    elif denyut_istirahat <= 80:
        kategori = "Rata-rata"
    elif denyut_istirahat <= 90:
        kategori = "Kurang"
    else:
        kategori = "Tinggi - perlu perhatian"
    return {"nilai": denyut_istirahat, "kategori": kategori}


def evaluasi_denyut_latihan(usia, denyut_latihan, hr_istirahat=None):
    zona = hitung_target_hr(usia, hr_istirahat)
    if denyut_latihan < zona["zona_bawah"]:
        status = "Di bawah zona target (intensitas latihan tergolong ringan)"
    elif denyut_latihan <= zona["zona_atas"]:
        status = "Dalam zona target latihan"
    elif denyut_latihan <= zona["hr_max"]:
        status = "Di atas zona target (intensitas tinggi, mendekati maksimal)"
    else:
        status = "Melebihi estimasi denyut jantung maksimal - turunkan intensitas segera"
    return {"zona": zona, "status": status}


def klasifikasi_pushup(gender, jumlah):
    if gender == "L":
        if jumlah < 15:
            label = "Kurang"
        elif jumlah < 30:
            label = "Cukup"
        elif jumlah < 50:
            label = "Baik"
        elif jumlah < 75:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    else:
        if jumlah < 10:
            label = "Kurang"
        elif jumlah < 20:
            label = "Cukup"
        elif jumlah < 35:
            label = "Baik"
        elif jumlah < 50:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    return {"jumlah": jumlah, "kategori": label}


def klasifikasi_situp(gender, jumlah):
    if gender == "L":
        if jumlah < 20:
            label = "Kurang"
        elif jumlah < 30:
            label = "Cukup"
        elif jumlah < 40:
            label = "Baik"
        elif jumlah < 50:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    else:
        if jumlah < 15:
            label = "Kurang"
        elif jumlah < 25:
            label = "Cukup"
        elif jumlah < 35:
            label = "Baik"
        elif jumlah < 45:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    return {"jumlah": jumlah, "kategori": label}


def klasifikasi_plank(detik):
    if detik < 30:
        label = "Kurang"
    elif detik < 60:
        label = "Cukup"
    elif detik < 120:
        label = "Baik"
    elif detik < 180:
        label = "Sangat Baik"
    else:
        label = "Istimewa"
    return {"detik": detik, "kategori": label}


def klasifikasi_squat(gender, jumlah):
    if gender == "L":
        if jumlah < 20:
            label = "Kurang"
        elif jumlah < 30:
            label = "Cukup"
        elif jumlah < 40:
            label = "Baik"
        elif jumlah < 50:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    else:
        if jumlah < 15:
            label = "Kurang"
        elif jumlah < 25:
            label = "Cukup"
        elif jumlah < 35:
            label = "Baik"
        elif jumlah < 45:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    return {"jumlah": jumlah, "kategori": label}


def klasifikasi_crunch(gender, jumlah):
    if gender == "L":
        if jumlah < 25:
            label = "Kurang"
        elif jumlah < 35:
            label = "Cukup"
        elif jumlah < 45:
            label = "Baik"
        elif jumlah < 60:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    else:
        if jumlah < 20:
            label = "Kurang"
        elif jumlah < 30:
            label = "Cukup"
        elif jumlah < 40:
            label = "Baik"
        elif jumlah < 55:
            label = "Sangat Baik"
        else:
            label = "Istimewa"
    return {"jumlah": jumlah, "kategori": label}
'@
Set-Content -Path ".\fitness\calculators.py" -Value $calculators -Encoding UTF8
Write-Host "calculators.py diperbarui." -ForegroundColor Green

# =====================================================================
# 2. views.py -> TIMPA lengkap (semua view lama + 5 view baru)
# =====================================================================
$views = @'
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .access import user_has_access
from . import calculators as calc


def _check_access(user):
    if not user_has_access(user):
        raise PermissionDenied("Kamu tidak punya akses ke kalkulator ini.")


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
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_pushup(gender, jumlah)
    return render(request, "fitness/pushup.html", {"hasil": hasil})


@login_required
def calc_situp(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_situp(gender, jumlah)
    return render(request, "fitness/situp.html", {"hasil": hasil})


@login_required
def calc_plank(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        detik = int(request.POST.get("detik"))
        hasil = calc.klasifikasi_plank(detik)
    return render(request, "fitness/plank.html", {"hasil": hasil})


@login_required
def calc_squat(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_squat(gender, jumlah)
    return render(request, "fitness/squat.html", {"hasil": hasil})


@login_required
def calc_crunch(request):
    _check_access(request.user)
    hasil = None
    if request.method == "POST":
        gender = request.POST.get("gender", "L")
        jumlah = int(request.POST.get("jumlah"))
        hasil = calc.klasifikasi_crunch(gender, jumlah)
    return render(request, "fitness/crunch.html", {"hasil": hasil})
'@
Set-Content -Path ".\fitness\views.py" -Value $views -Encoding UTF8
Write-Host "views.py diperbarui." -ForegroundColor Green

# =====================================================================
# 3. urls.py -> TIMPA lengkap (semua url lama + 5 url baru)
# =====================================================================
$urls = @'
from django.urls import path
from . import views

urlpatterns = [
    path("bmi-bodyfat/", views.calc_bmi_bodyfat, name="calc_bmi_bodyfat"),
    path("1rm/", views.calc_one_rep_max, name="calc_one_rep_max"),
    path("tdee/", views.calc_tdee, name="calc_tdee"),
    path("target-hr/", views.calc_target_hr, name="calc_target_hr"),
    path("vo2-12min/", views.calc_vo2_12min, name="calc_vo2_12min"),
    path("risk/", views.calc_risk, name="calc_risk"),
    path("denyut-nadi/", views.calc_denyut_nadi, name="calc_denyut_nadi"),
    path("pushup/", views.calc_pushup, name="calc_pushup"),
    path("situp/", views.calc_situp, name="calc_situp"),
    path("plank/", views.calc_plank, name="calc_plank"),
    path("squat/", views.calc_squat, name="calc_squat"),
    path("crunch/", views.calc_crunch, name="calc_crunch"),
]
'@
Set-Content -Path ".\fitness\urls.py" -Value $urls -Encoding UTF8
Write-Host "urls.py diperbarui." -ForegroundColor Green

# =====================================================================
# 4. base_calculator.html -> TIMPA lengkap (tambah section baru)
# =====================================================================
$baseCalc = @'
{% extends "base.html" %}
{% block content %}
<div class="calc-layout">
  <aside class="calc-sidebar">
    <h4>Tes Kebugaran</h4>
    <ul>
      <li><a href="{% url 'calc_bmi_bodyfat' %}">Komposisi Tubuh</a></li>
      <li><a href="{% url 'calc_vo2_12min' %}">Lari 12 Menit</a></li>
    </ul>

    <h4>Tes Kekuatan Otot</h4>
    <ul>
      <li><a href="{% url 'calc_pushup' %}">Push Up</a></li>
      <li><a href="{% url 'calc_situp' %}">Sit Up</a></li>
      <li><a href="{% url 'calc_crunch' %}">Crunch</a></li>
      <li><a href="{% url 'calc_plank' %}">Plank</a></li>
      <li><a href="{% url 'calc_squat' %}">Squat</a></li>
    </ul>

    <h4>Latihan Beban</h4>
    <ul>
      <li><a href="{% url 'calc_one_rep_max' %}">1 Rep Max</a></li>
    </ul>

    <h4>Diet & Nutrisi</h4>
    <ul>
      <li><a href="{% url 'calc_tdee' %}">Kebutuhan Kalori Harian</a></li>
    </ul>

    <h4>Denyut Jantung</h4>
    <ul>
      <li><a href="{% url 'calc_target_hr' %}">Target Denyut Jantung</a></li>
      <li><a href="{% url 'calc_denyut_nadi' %}">Denyut Nadi (Istirahat & Latihan)</a></li>
    </ul>

    <h4>Kalkulator Lainnya</h4>
    <ul>
      <li><a href="{% url 'calc_risk' %}">Klasifikasi Risiko Kesehatan</a></li>
    </ul>
  </aside>

  <main class="calc-content">
    {% block calc_content %}{% endblock %}
  </main>
</div>

<style>
.calc-layout { display: flex; gap: 2rem; align-items: flex-start; }
.calc-sidebar { width: 220px; flex-shrink: 0; border-right: 1px solid #ddd; padding-right: 1rem; position: sticky; top: 1rem; max-height: 90vh; overflow-y: auto; }
.calc-sidebar h4 { margin-top: 1.2rem; color: #555; font-size: .8rem; text-transform: uppercase; letter-spacing: .03em; }
.calc-sidebar ul { list-style: none; padding: 0; margin: .3rem 0 0 0; }
.calc-sidebar a { color: #2563eb; text-decoration: none; display: block; padding: .3rem 0; font-size: .93rem; }
.calc-sidebar a:hover { text-decoration: underline; }
.calc-content { flex: 1; max-width: 620px; }
.calc-content h2 { margin-bottom: .3rem; }
.calc-content label { display: block; margin-top: 1rem; font-weight: 600; font-size: .9rem; color: #333; }
.calc-content select { width: 100%; padding: .4rem; margin-top: .3rem; border-radius: 6px; border: 1px solid #ccc; }
.calc-content button[type="submit"] { margin-top: 1.5rem; padding: .6rem 1.4rem; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
.calc-content button[type="submit"]:hover { background: #1d4ed8; }

input[type=range] {
  -webkit-appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 4px;
  background: #dbeafe;
  margin-top: .5rem;
  outline: none;
}
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 3px solid #fff;
  box-shadow: 0 0 0 1px #2563eb;
}
input[type=range]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 3px solid #fff;
  box-shadow: 0 0 0 1px #2563eb;
}

.instruksi-box { background: #f8f9fa; border-left: 4px solid #2563eb; padding: 1rem 1.2rem; margin-top: 1.8rem; font-size: .92rem; border-radius: 4px; }
.instruksi-box ol { margin: .5rem 0 0 1.2rem; padding: 0; }
.instruksi-box li { margin-bottom: .4rem; }
.result-box { margin-top: 1.5rem; padding: 1rem 1.2rem; background: #eef7ee; border: 1px solid #cdebd0; border-radius: 8px; }
.result-box p { margin: .3rem 0; }

@media (max-width: 768px) {
  .calc-layout { flex-direction: column; }
  .calc-sidebar { width: 100%; border-right: none; border-bottom: 1px solid #ddd; padding-bottom: 1rem; position: static; max-height: none; }
}
</style>
{% endblock %}
'@
Set-Content -Path "$templateDir\base_calculator.html" -Value $baseCalc -Encoding UTF8
Write-Host "base_calculator.html diperbarui." -ForegroundColor Green

# =====================================================================
# 5. Template: pushup.html
# =====================================================================
$pushup = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Push Up</h2>
<form method="post">
  {% csrf_token %}
  <label>Jenis Kelamin</label>
  <select name="gender">
    <option value="L">Laki-laki</option>
    <option value="P">Perempuan</option>
  </select>

  <label>Jumlah Push Up (maksimal dalam 1 menit): <span id="jV">20</span> kali</label>
  <input type="range" name="jumlah" min="0" max="100" value="20" oninput="jV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Atlet melakukan push up dengan teknik benar (dada menyentuh/mendekati lantai, lengan lurus penuh di posisi atas) sebanyak mungkin dalam 1 menit.</li>
    <li>Catat jumlah repetisi yang valid (repetisi dengan teknik buruk tidak dihitung).</li>
    <li>Norma klasifikasi bersifat umum untuk usia dewasa - sesuaikan dengan standar cabor masing-masing bila tersedia.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\pushup.html" -Value $pushup -Encoding UTF8

# =====================================================================
# 6. Template: situp.html
# =====================================================================
$situp = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Sit Up</h2>
<form method="post">
  {% csrf_token %}
  <label>Jenis Kelamin</label>
  <select name="gender">
    <option value="L">Laki-laki</option>
    <option value="P">Perempuan</option>
  </select>

  <label>Jumlah Sit Up (dalam 1 menit): <span id="jV">25</span> kali</label>
  <input type="range" name="jumlah" min="0" max="100" value="25" oninput="jV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Posisi awal: berbaring telentang, lutut ditekuk, tangan di belakang kepala atau menyilang di dada.</li>
    <li>Hitung jumlah sit up sempurna (bahu terangkat penuh, punggung kembali menyentuh lantai) dalam 1 menit.</li>
    <li>Norma klasifikasi bersifat umum untuk usia dewasa.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\situp.html" -Value $situp -Encoding UTF8

# =====================================================================
# 7. Template: plank.html
# =====================================================================
$plank = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Plank</h2>
<form method="post">
  {% csrf_token %}
  <label>Lama Tahan Plank: <span id="dV">45</span> detik</label>
  <input type="range" name="detik" min="0" max="300" step="5" value="45" oninput="dV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Waktu: <strong>{{ hasil.detik }} detik</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Posisi plank: bertumpu pada lengan bawah dan ujung kaki, tubuh membentuk garis lurus dari kepala hingga tumit.</li>
    <li>Catat waktu maksimal atlet mampu mempertahankan posisi dengan teknik benar (pinggul tidak turun/naik).</li>
    <li>Norma berlaku umum untuk kedua jenis kelamin.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\plank.html" -Value $plank -Encoding UTF8

# =====================================================================
# 8. Template: squat.html
# =====================================================================
$squat = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Squat</h2>
<form method="post">
  {% csrf_token %}
  <label>Jenis Kelamin</label>
  <select name="gender">
    <option value="L">Laki-laki</option>
    <option value="P">Perempuan</option>
  </select>

  <label>Jumlah Bodyweight Squat (dalam 1 menit): <span id="jV">25</span> kali</label>
  <input type="range" name="jumlah" min="0" max="100" value="25" oninput="jV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Squat dilakukan tanpa beban tambahan, paha sejajar lantai (90 derajat) sebagai standar kedalaman.</li>
    <li>Hitung repetisi valid dalam 1 menit.</li>
    <li>Norma klasifikasi bersifat umum untuk usia dewasa.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\squat.html" -Value $squat -Encoding UTF8

# =====================================================================
# 9. Template: crunch.html
# =====================================================================
$crunch = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Crunch</h2>
<form method="post">
  {% csrf_token %}
  <label>Jenis Kelamin</label>
  <select name="gender">
    <option value="L">Laki-laki</option>
    <option value="P">Perempuan</option>
  </select>

  <label>Jumlah Crunch (dalam 1 menit): <span id="jV">30</span> kali</label>
  <input type="range" name="jumlah" min="0" max="120" value="30" oninput="jV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Posisi awal sama seperti sit up, namun gerakan crunch hanya mengangkat bahu dan punggung atas (rentang gerak lebih pendek dari sit up).</li>
    <li>Hitung jumlah repetisi valid dalam 1 menit.</li>
    <li>Norma klasifikasi bersifat umum untuk usia dewasa.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\crunch.html" -Value $crunch -Encoding UTF8

Write-Host "5 template tes kekuatan otot dibuat (pushup, situp, plank, squat, crunch)." -ForegroundColor Green

Write-Host "`n=== SELESAI ===" -ForegroundColor Cyan
Write-Host "Tidak ada perubahan settings.py / urls.py utama / base.html yang diperlukan lagi."
Write-Host "Restart server:"
Write-Host "  python manage.py runserver"
Write-Host "Lalu buka salah satu, misal: http://127.0.0.1:8000/fitness/pushup/"
