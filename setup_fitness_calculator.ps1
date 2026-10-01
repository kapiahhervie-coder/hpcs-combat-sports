<#
=====================================================================
 SETUP FITNESS CALCULATOR - HPCS (Django)
 Jalankan dari root folder project (folder yang berisi manage.py)
 Contoh: PS D:\proyek\hpcs> .\setup_fitness_calculator.ps1
=====================================================================
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Setup Fitness Calculator untuk HPCS ===" -ForegroundColor Cyan

# 0. Validasi berada di root project Django
if (-not (Test-Path ".\manage.py")) {
    Write-Host "ERROR: manage.py tidak ditemukan di folder ini." -ForegroundColor Red
    Write-Host "Pindah dulu ke root project Django (folder yang berisi manage.py), lalu jalankan ulang script ini." -ForegroundColor Yellow
    exit 1
}

# 1. Buat app 'fitness' jika belum ada
if (-not (Test-Path ".\fitness")) {
    Write-Host "Membuat app 'fitness'..." -ForegroundColor Green
    python manage.py startapp fitness
} else {
    Write-Host "App 'fitness' sudah ada, lanjut menimpa file konten." -ForegroundColor Yellow
}

# 2. Buat struktur folder
$templateDir = ".\fitness\templates\fitness"
$mgmtDir = ".\fitness\management\commands"
New-Item -ItemType Directory -Force -Path $templateDir | Out-Null
New-Item -ItemType Directory -Force -Path $mgmtDir | Out-Null
New-Item -ItemType Directory -Force -Path ".\fitness\management" | Out-Null

# pastikan __init__.py ada di folder management & commands
New-Item -ItemType File -Force -Path ".\fitness\management\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path ".\fitness\management\commands\__init__.py" | Out-Null

Write-Host "Struktur folder siap." -ForegroundColor Green

# =====================================================================
# 3. fitness/access.py
# =====================================================================
$access = @'
def user_has_access(user):
    ALLOWED_GROUPS = {"cabor_1", "cabor_2", "cabor_3", "cabor_4", "pjok"}
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ALLOWED_GROUPS).exists()
'@
Set-Content -Path ".\fitness\access.py" -Value $access -Encoding UTF8

# =====================================================================
# 4. fitness/calculators.py
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
'@
Set-Content -Path ".\fitness\calculators.py" -Value $calculators -Encoding UTF8

# =====================================================================
# 5. fitness/views.py
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
'@
Set-Content -Path ".\fitness\views.py" -Value $views -Encoding UTF8

# =====================================================================
# 6. fitness/urls.py
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
]
'@
Set-Content -Path ".\fitness\urls.py" -Value $urls -Encoding UTF8

# =====================================================================
# 7. management command: setup_groups.py
# =====================================================================
$setupGroups = @'
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

GROUPS = ["cabor_1", "cabor_2", "cabor_3", "cabor_4", "pjok"]

class Command(BaseCommand):
    help = "Buat groups untuk akses kalkulator fitnes"

    def handle(self, *args, **kwargs):
        for name in GROUPS:
            group, created = Group.objects.get_or_create(name=name)
            status = "dibuat" if created else "sudah ada"
            self.stdout.write(f"Group {name}: {status}")
'@
Set-Content -Path "$mgmtDir\setup_groups.py" -Value $setupGroups -Encoding UTF8

# =====================================================================
# 8. Template: base_calculator.html (dengan styling slider custom)
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

    <h4>Pengatur Waktu</h4>
    <ul>
      <li><a href="{% url 'calc_target_hr' %}">Target Denyut Jantung</a></li>
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

/* Custom range slider */
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

# =====================================================================
# 9. Template: bmi_bodyfat.html
# =====================================================================
$bmiBodyfat = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Komposisi Tubuh (BMI & Persen Lemak)</h2>
<form method="post">
  {% csrf_token %}
  <label>Berat Badan: <span id="bV">60</span> kg</label>
  <input type="range" name="berat" min="30" max="150" value="60" oninput="bV.innerText=this.value">

  <label>Tinggi Badan: <span id="tV">165</span> cm</label>
  <input type="range" name="tinggi" min="120" max="220" value="165" oninput="tV.innerText=this.value">

  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

  <label>Jenis Kelamin</label>
  <select name="gender">
    <option value="L">Laki-laki</option>
    <option value="P">Perempuan</option>
  </select>

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>BMI: <strong>{{ hasil.bmi }}</strong> ({{ hasil.kategori }})</p>
  <p>Estimasi Lemak Tubuh: <strong>{{ hasil.body_fat }}%</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Geser slider sesuai berat, tinggi, dan usia atlet saat ini.</li>
    <li>BMI dihitung dari berat (kg) dibagi kuadrat tinggi (m).</li>
    <li>Estimasi lemak tubuh menggunakan rumus Deurenberg - cocok untuk skrining awal, bukan pengukuran presisi.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\bmi_bodyfat.html" -Value $bmiBodyfat -Encoding UTF8

# =====================================================================
# 10. Template: one_rep_max.html
# =====================================================================
$oneRepMax = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Kalkulator 1 Rep Max (1RM)</h2>
<p>Prediksi beban maksimal angkatan tunggal dari beban yang sanggup diangkat berulang kali.</p>

<form method="post">
  {% csrf_token %}
  <label>Beban yang diangkat: <span id="bVal">40</span> kg</label>
  <input type="range" name="berat_angkat" min="5" max="200" value="40" oninput="bVal.innerText=this.value">

  <label>Jumlah pengulangan: <span id="rVal">8</span>x</label>
  <input type="range" name="repetisi" min="1" max="15" value="8" oninput="rVal.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <strong>Estimasi 1RM: {{ hasil }} kg</strong>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Masukkan beban (kg) yang mampu diangkat dalam satu set.</li>
    <li>Masukkan jumlah pengulangan maksimal dengan beban tersebut (idealnya 2-10 repetisi agar estimasi akurat).</li>
    <li>Hasil merupakan estimasi menggunakan rumus Epley, bukan pengukuran langsung.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\one_rep_max.html" -Value $oneRepMax -Encoding UTF8

# =====================================================================
# 11. Template: tdee.html
# =====================================================================
$tdee = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Kebutuhan Kalori Harian (TDEE)</h2>
<form method="post">
  {% csrf_token %}
  <label>Berat Badan: <span id="bV">60</span> kg</label>
  <input type="range" name="berat" min="30" max="150" value="60" oninput="bV.innerText=this.value">

  <label>Tinggi Badan: <span id="tV">165</span> cm</label>
  <input type="range" name="tinggi" min="120" max="220" value="165" oninput="tV.innerText=this.value">

  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

  <label>Jenis Kelamin</label>
  <select name="gender">
    <option value="L">Laki-laki</option>
    <option value="P">Perempuan</option>
  </select>

  <label>Level Aktivitas: <span id="aV">Sedang</span></label>
  <input type="range" name="aktivitas" min="1.2" max="1.9" step="0.1" value="1.55" oninput="updAkt(this.value)">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <strong>TDEE: {{ hasil }} kkal/hari</strong>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Isi data dasar atlet, lalu sesuaikan level aktivitas dengan frekuensi latihan mingguan.</li>
    <li>BMR dihitung dengan rumus Mifflin-St Jeor, lalu dikalikan faktor aktivitas untuk mendapat TDEE.</li>
    <li>Gunakan hasil ini sebagai acuan kebutuhan energi harian, sesuaikan lagi jika tujuannya menambah/menurunkan berat badan.</li>
  </ol>
</div>

<script>
function updAkt(v){
  var l = "Sedang";
  if (v <= 1.3) { l = "Ringan"; }
  else if (v <= 1.55) { l = "Sedang"; }
  else if (v <= 1.7) { l = "Berat"; }
  else { l = "Sangat Berat (atlet)"; }
  document.getElementById("aV").innerText = l;
}
</script>
{% endblock %}
'@
Set-Content -Path "$templateDir\tdee.html" -Value $tdee -Encoding UTF8

# =====================================================================
# 12. Template: target_heart_rate.html
# =====================================================================
$targetHr = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Target Denyut Jantung (Zona Latihan)</h2>
<form method="post">
  {% csrf_token %}
  <label>Usia: <span id="uV">20</span> tahun</label>
  <input type="range" name="usia" min="10" max="80" value="20" oninput="uV.innerText=this.value">

  <label>Denyut Jantung Istirahat (opsional): <span id="rV">70</span> bpm</label>
  <input type="range" name="hr_istirahat" min="40" max="100" value="70" oninput="rV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Denyut Jantung Maksimal: <strong>{{ hasil.hr_max }} bpm</strong></p>
  <p>Zona Latihan (60-80%): <strong>{{ hasil.zona_bawah }} - {{ hasil.zona_atas }} bpm</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Masukkan usia atlet - HR maksimal diestimasi dengan rumus 220 minus usia.</li>
    <li>Jika tersedia data denyut jantung istirahat (diukur pagi hari sebelum bangun), zona dihitung dengan metode Karvonen yang lebih akurat.</li>
    <li>Zona 60-80% cocok untuk latihan aerobik umum; sesuaikan untuk latihan intensitas tinggi atau pemulihan.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\target_heart_rate.html" -Value $targetHr -Encoding UTF8

# =====================================================================
# 13. Template: vo2_12min.html
# =====================================================================
$vo2 = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Tes Lari 12 Menit (Estimasi VO2 Max)</h2>
<form method="post">
  {% csrf_token %}
  <label>Jarak Tempuh: <span id="jV">2000</span> meter</label>
  <input type="range" name="jarak" min="800" max="4000" step="10" value="2000" oninput="jV.innerText=this.value">

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Estimasi VO2 Max: <strong>{{ hasil.vo2max }} ml/kg/menit</strong></p>
  <p>Rating: <strong>{{ hasil.rating }}</strong></p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Atlet berlari secepat mungkin selama 12 menit di lintasan datar, lalu catat jarak yang ditempuh (meter).</li>
    <li>Masukkan jarak tersebut ke slider untuk mendapat estimasi VO2 max (rumus Cooper).</li>
    <li>Rating bersifat umum - bandingkan dengan norma cabor masing-masing untuk interpretasi lebih spesifik.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\vo2_12min.html" -Value $vo2 -Encoding UTF8

# =====================================================================
# 14. Template: risk_classification.html
# =====================================================================
$risk = @'
{% extends "fitness/base_calculator.html" %}
{% block calc_content %}
<h2>Klasifikasi Risiko Kesehatan (Pra-Latihan)</h2>
<form method="post">
  {% csrf_token %}
  <label>Jumlah Faktor Risiko yang Diketahui (riwayat penyakit jantung, tekanan darah tinggi, kolesterol tinggi, merokok, dsb): <span id="fV">0</span></label>
  <input type="range" name="jumlah_faktor" min="0" max="6" value="0" oninput="fV.innerText=this.value">

  <label style="display:flex; align-items:center; gap:.5rem; margin-top:1rem;">
    <input type="checkbox" name="ada_gejala" style="width:auto;">
    Ada gejala saat ini (nyeri dada, sesak napas tidak biasa, pusing, jantung berdebar tidak normal)
  </label>

  <button type="submit">Hitung</button>
</form>

{% if hasil %}
<div class="result-box">
  <p>Tingkat Risiko: <strong>{{ hasil.level }}</strong></p>
  <p>{{ hasil.saran }}</p>
</div>
{% endif %}

<div class="instruksi-box">
  <strong>Petunjuk:</strong>
  <ol>
    <li>Hitung jumlah faktor risiko kesehatan yang diketahui pada atlet (bukan diagnosis, hanya skrining awal).</li>
    <li>Centang jika atlet sedang mengalami gejala tidak biasa.</li>
    <li>Alat ini bukan pengganti pemeriksaan medis - hasil "Sedang" atau "Tinggi" wajib ditindaklanjuti dengan konsultasi ke dokter/tenaga medis olahraga.</li>
  </ol>
</div>
{% endblock %}
'@
Set-Content -Path "$templateDir\risk_classification.html" -Value $risk -Encoding UTF8

Write-Host "`nSemua file berhasil dibuat." -ForegroundColor Green

# =====================================================================
# 15. Pengingat langkah manual yang WAJIB dilakukan setelah ini
# =====================================================================
Write-Host "`n=== LANGKAH SELANJUTNYA (manual, wajib) ===" -ForegroundColor Cyan
Write-Host "1. Tambahkan 'fitness' ke INSTALLED_APPS di settings.py (jika belum)."
Write-Host "2. Include URL app fitness di urls.py project utama, contoh:"
Write-Host "   path('fitness/', include('fitness.urls'))"
Write-Host "3. Jalankan: python manage.py setup_groups"
Write-Host "   -> ini akan membuat groups: cabor_1, cabor_2, cabor_3, cabor_4, pjok"
Write-Host "4. Assign user ke group masing-masing lewat /admin/auth/group/"
Write-Host "5. Pastikan base.html project punya {% block content %}{% endblock %}"
Write-Host "6. Jalankan: python manage.py runserver, lalu buka /fitness/bmi-bodyfat/"
Write-Host "`nSelesai." -ForegroundColor Green
