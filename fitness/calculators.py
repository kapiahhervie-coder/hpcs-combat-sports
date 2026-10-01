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
