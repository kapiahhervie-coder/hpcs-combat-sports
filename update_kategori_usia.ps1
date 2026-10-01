<#
=====================================================================
 UPDATE: Tambah Kategori Usia pada Tes Kekuatan Otot
 (Push Up, Sit Up, Plank, Squat, Crunch)
 Jalankan dari root folder project (folder yang berisi manage.py)
=====================================================================
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Update: Kategori Usia untuk Tes Kekuatan Otot ===" -ForegroundColor Cyan

if (-not (Test-Path ".\manage.py")) {
    Write-Host "ERROR: manage.py tidak ditemukan. Pindah ke root project dulu." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path ".\fitness")) {
    Write-Host "ERROR: folder 'fitness' tidak ditemukan." -ForegroundColor Red
    exit 1
}

$templateDir = ".\fitness\templates\fitness"

# =====================================================================
# 1. calculators.py -> TIMPA lengkap (semua fungsi lama + revisi usia)
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


def label_kategori_usia(usia):
    if usia < 18:
        return "Yunior (< 18 th)"
    elif usia <= 39:
        return "Dewasa (18-39 th)"
    else:
        return "Senior (40+ th)"


def _faktor_usia(usia):
    if usia < 18:
        return 0.8
    elif usia <= 39:
        return 1.0
    else:
        return 0.7


def _sesuaikan_ambang(ambang_dasar, usia):
    faktor = _faktor_usia(usia)
    return [max(1, round(a * faktor)) for a in ambang_dasar]


def _klasifikasi_bertingkat(nilai, ambang):
    labels = ["Kurang", "Cukup", "Baik", "Sangat Baik", "Istimewa"]
    for i, batas in enumerate(ambang):
        if nilai < batas:
            return labels[i]
    return labels[-1]


def klasifikasi_pushup(usia, gender, jumlah):
    dasar = [15, 30, 50, 75] if gender == "L" else [10, 20, 35, 50]
    ambang = _sesuaikan_ambang(dasar, usia)
    kategori = _klasifikasi_bertingkat(jumlah, ambang)
    return {"jumlah": jumlah, "kategori": kategori, "kategori_usia": label_kategori_usia(usia)}


def klasifikasi_situp(usia, gender, jumlah):
    dasar = [20, 30, 40, 50] if gender == "L" else [15, 25, 35, 45]
    ambang = _sesuaikan_ambang(dasar, usia)
    kategori = _klasifikasi_bertingkat(jumlah, ambang)
    return {"jumlah": jumlah, "kategori": kategori, "kategori_usia": label_kategori_usia(usia)}


def klasifikasi_plank(usia, detik):
    dasar = [30, 60, 120, 180]
    ambang = _sesuaikan_ambang(dasar, usia)
    kategori = _klasifikasi_bertingkat(detik, ambang)
    return {"detik": detik, "kategori": kategori, "kategori_usia": label_kategori_usia(usia)}


def klasifikasi_squat(usia, gender, jumlah):
    dasar = [20, 30, 40, 50] if gender == "L" else [15, 25, 35, 45]
    ambang = _sesuaikan_ambang(dasar, usia)
    kategori = _klasifikasi_bertingkat(jumlah, ambang)
    return {"jumlah": jumlah, "kategori": kategori, "kategori_usia": label_kategori_usia(usia)}


def klasifikasi_crunch(usia, gender, jumlah):
    dasar = [25, 35, 45, 60] if gender == "L" else [20, 30, 40, 55]
    ambang = _sesuaikan_ambang(dasar, usia)
    kategori = _klasifikasi_bertingkat(jumlah, ambang)
    return {"jumlah": jumlah, "kategori": kategori, "kategori_usia": label_kategori_usia(usia)}
'@
Set-Content -Path ".\fitness\calculators.py" -Value $calculators -Encoding UTF8
Write-Host "calculators.py diperbarui (kategori usia ditambahkan)." -ForegroundColor Green

# =====================================================================
# 2. views.py -> TIMPA lengkap (5 view tes otot diupdate pakai usia)
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
'@
Set-Content -Path ".\fitness\views.py" -Value $views -Encoding UTF8
Write-Host "views.py diperbarui." -ForegroundColor Green

# =====================================================================
# 3. Template: pushup.html (tambah slider usia)
# =====================================================================
$pushup = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Push Up</h2>
<form method="post">
  {% csrf_token %}
  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

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
  <p>Kategori Usia: <strong>{{ hasil.kategori_usia }}</strong></p>
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Atlet melakukan push up dengan teknik benar (dada menyentuh/mendekati lantai, lengan lurus penuh di posisi atas) sebanyak mungkin dalam 1 menit.</li>
    <li>Catat jumlah repetisi yang valid (repetisi dengan teknik buruk tidak dihitung).</li>
    <li>Norma disesuaikan otomatis berdasarkan kategori usia: Yunior (&lt;18 th), Dewasa (18-39 th), Senior (40+ th).</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\pushup.html" -Value $pushup -Encoding UTF8

# =====================================================================
# 4. Template: situp.html
# =====================================================================
$situp = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Sit Up</h2>
<form method="post">
  {% csrf_token %}
  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

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
  <p>Kategori Usia: <strong>{{ hasil.kategori_usia }}</strong></p>
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Posisi awal: berbaring telentang, lutut ditekuk, tangan di belakang kepala atau menyilang di dada.</li>
    <li>Hitung jumlah sit up sempurna (bahu terangkat penuh, punggung kembali menyentuh lantai) dalam 1 menit.</li>
    <li>Norma disesuaikan otomatis berdasarkan kategori usia: Yunior (&lt;18 th), Dewasa (18-39 th), Senior (40+ th).</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\situp.html" -Value $situp -Encoding UTF8

# =====================================================================
# 5. Template: plank.html
# =====================================================================
$plank = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Plank</h2>
<form method="post">
  {% csrf_token %}
  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

  <label>Lama Tahan Plank: <span id="dV">45</span> detik</label>
  <input type="range" name="detik" min="0" max="300" step="5" value="45" oninput="dV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Kategori Usia: <strong>{{ hasil.kategori_usia }}</strong></p>
  <p>Waktu: <strong>{{ hasil.detik }} detik</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Posisi plank: bertumpu pada lengan bawah dan ujung kaki, tubuh membentuk garis lurus dari kepala hingga tumit.</li>
    <li>Catat waktu maksimal atlet mampu mempertahankan posisi dengan teknik benar (pinggul tidak turun/naik).</li>
    <li>Norma disesuaikan otomatis berdasarkan kategori usia: Yunior (&lt;18 th), Dewasa (18-39 th), Senior (40+ th).</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\plank.html" -Value $plank -Encoding UTF8

# =====================================================================
# 6. Template: squat.html
# =====================================================================
$squat = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Squat</h2>
<form method="post">
  {% csrf_token %}
  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

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
  <p>Kategori Usia: <strong>{{ hasil.kategori_usia }}</strong></p>
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Squat dilakukan tanpa beban tambahan, paha sejajar lantai (90 derajat) sebagai standar kedalaman.</li>
    <li>Hitung repetisi valid dalam 1 menit.</li>
    <li>Norma disesuaikan otomatis berdasarkan kategori usia: Yunior (&lt;18 th), Dewasa (18-39 th), Senior (40+ th).</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\squat.html" -Value $squat -Encoding UTF8

# =====================================================================
# 7. Template: crunch.html
# =====================================================================
$crunch = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Crunch</h2>
<form method="post">
  {% csrf_token %}
  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

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
  <p>Kategori Usia: <strong>{{ hasil.kategori_usia }}</strong></p>
  <p>Jumlah: <strong>{{ hasil.jumlah }} kali</strong></p>
  <p>Kategori: <strong>{{ hasil.kategori }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Posisi awal sama seperti sit up, namun gerakan crunch hanya mengangkat bahu dan punggung atas (rentang gerak lebih pendek dari sit up).</li>
    <li>Hitung jumlah repetisi valid dalam 1 menit.</li>
    <li>Norma disesuaikan otomatis berdasarkan kategori usia: Yunior (&lt;18 th), Dewasa (18-39 th), Senior (40+ th).</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\crunch.html" -Value $crunch -Encoding UTF8

Write-Host "5 template diperbarui dengan slider usia." -ForegroundColor Green

Write-Host "`n=== SELESAI ===" -ForegroundColor Cyan
Write-Host "Tidak perlu ubah urls.py atau base_calculator.html - link sidebar sudah ada dari update sebelumnya."
Write-Host "Restart server:"
Write-Host "  python manage.py runserver"
Write-Host "Lalu buka: http://127.0.0.1:8000/fitness/pushup/"
