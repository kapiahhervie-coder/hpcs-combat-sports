<#
=====================================================================
 UPDATE: Tambah Kalkulator Denyut Nadi (Normal, Istirahat, Latihan)
 Jalankan dari root folder project (folder yang berisi manage.py)
=====================================================================
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Update: Kalkulator Denyut Nadi ===" -ForegroundColor Cyan

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
# 1. calculators.py -> TIMPA lengkap (versi lama + fungsi baru)
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
'@
Set-Content -Path ".\fitness\calculators.py" -Value $calculators -Encoding UTF8
Write-Host "calculators.py diperbarui." -ForegroundColor Green

# =====================================================================
# 2. views.py -> TIMPA lengkap (versi lama + view baru)
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
'@
Set-Content -Path ".\fitness\views.py" -Value $views -Encoding UTF8
Write-Host "views.py diperbarui." -ForegroundColor Green

# =====================================================================
# 3. urls.py -> TIMPA lengkap (versi lama + url baru)
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
]
'@
Set-Content -Path ".\fitness\urls.py" -Value $urls -Encoding UTF8
Write-Host "urls.py diperbarui." -ForegroundColor Green

# =====================================================================
# 4. base_calculator.html -> TIMPA lengkap (tambah link sidebar baru)
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
.calc-sidebar { width: 220px; flex-shrink: 0; border-right: 1px solid #ddd; padding-right: 1rem; position: sticky; top: 1rem; }
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
  .calc-sidebar { width: 100%; border-right: none; border-bottom: 1px solid #ddd; padding-bottom: 1rem; position: static; }
}
</style>
{% endblock %}
'@
Set-Content -Path "$templateDir\base_calculator.html" -Value $baseCalc -Encoding UTF8
Write-Host "base_calculator.html diperbarui (link sidebar baru ditambahkan)." -ForegroundColor Green

# =====================================================================
# 5. Template baru: denyut_nadi.html
# =====================================================================
$denyutNadi = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Denyut Nadi (Normal, Istirahat & Latihan)</h2>
<p>Referensi umum: denyut nadi istirahat normal orang dewasa berkisar 60-100 kali/menit. Atlet terlatih sering memiliki denyut istirahat lebih rendah (bisa di bawah 60).</p>

<form method="post">
  {% csrf_token %}
  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

  <label>Denyut Nadi Istirahat (diukur pagi hari sebelum bangun/beraktivitas): <span id="iV">70</span> bpm</label>
  <input type="range" name="denyut_istirahat" min="40" max="120" value="70" oninput="iV.innerText=this.value">

  <label>Denyut Nadi Saat Latihan (opsional, diukur di tengah sesi latihan): <span id="lV">140</span> bpm</label>
  <input type="range" name="denyut_latihan" min="60" max="220" value="140" oninput="lV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Denyut Nadi Istirahat: <strong>{{ hasil.istirahat.nilai }} bpm</strong> - {{ hasil.istirahat.kategori }}</p>
  {% if hasil.latihan %}
  <p>Denyut Jantung Maksimal (estimasi): <strong>{{ hasil.latihan.zona.hr_max }} bpm</strong></p>
  <p>Zona Latihan Target: <strong>{{ hasil.latihan.zona.zona_bawah }} - {{ hasil.latihan.zona.zona_atas }} bpm</strong></p>
  <p>Status Denyut Saat Latihan: <strong>{{ hasil.latihan.status }}</strong></p>
  {% endif %}
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li><strong>Denyut nadi istirahat:</strong> ukur denyut nadi atlet saat baru bangun tidur, sebelum beraktivitas, selama 1 menit penuh (atau 15 detik dikali 4).</li>
    <li><strong>Denyut nadi latihan:</strong> ukur di tengah sesi latihan (misal segera setelah interval berat) untuk mengecek apakah intensitas latihan sudah sesuai target.</li>
    <li>Rentang normal istirahat dewasa: 60-100 bpm. Di bawah 60 pada atlet terlatih umumnya normal; di atas 100 secara konsisten sebaiknya dikonsultasikan ke tenaga medis.</li>
    <li>Zona latihan dihitung dengan metode Karvonen menggunakan denyut istirahat yang diisi di atas.</li>
  </ol>
</div>

<script>
document.getElementById("iV")?.addEventListener("input", function(){});
</script>
{% endblock %}
'@
Set-Content -Path "$templateDir\denyut_nadi.html" -Value $denyutNadi -Encoding UTF8
Write-Host "Template denyut_nadi.html dibuat." -ForegroundColor Green

Write-Host "`n=== SELESAI ===" -ForegroundColor Cyan
Write-Host "Tidak ada perubahan settings.py / urls.py utama / base.html yang diperlukan lagi."
Write-Host "Cukup restart server:"
Write-Host "  python manage.py runserver"
Write-Host "Lalu buka: http://127.0.0.1:8000/fitness/denyut-nadi/"
