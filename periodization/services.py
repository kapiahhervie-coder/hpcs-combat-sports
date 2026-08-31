"""
periodization/services.py
Pilar 3 HPCS -- Auto-Periodization Engine.

Fungsi utama: generate_periodisasi_otomatis(macro_program) -- otomatis
bikin MesoCycle (GPP/SPP/Pre-Comp/Comp) dari 1 MacroProgram, berdasarkan
rasio periodisasi klasik dan kurva volume/intensitas standar.

Ini logika murni (gak ada model baru), aman diubah kapan saja.
"""
from datetime import timedelta
from .models import MesoCycle


# Rasio klasik pembagian durasi total ke 4 fase (total harus 100)
RASIO_FASE = {
    'GPP':      0.40,
    'SPP':      0.30,
    'PRE_COMP': 0.20,
    'COMP':     0.10,
}

# Kurva volume/intensitas & porsi fokus L1-L4 per fase (skala 1-10 / persen)
# Prinsip: makin dekat kompetisi, volume turun & intensitas naik, fokus
# geser dari koreksi/strength (L1/L2) ke power/speed (L3/L4).
PROFIL_FASE = {
    'GPP': {
        'volume_target': 8, 'intensitas_target': 3,
        'fokus_l1_persen': 40, 'fokus_l2_persen': 40, 'fokus_l3_persen': 15, 'fokus_l4_persen': 5,
    },
    'SPP': {
        'volume_target': 6, 'intensitas_target': 5,
        'fokus_l1_persen': 20, 'fokus_l2_persen': 35, 'fokus_l3_persen': 30, 'fokus_l4_persen': 15,
    },
    'PRE_COMP': {
        'volume_target': 4, 'intensitas_target': 8,
        'fokus_l1_persen': 10, 'fokus_l2_persen': 20, 'fokus_l3_persen': 30, 'fokus_l4_persen': 40,
    },
    'COMP': {
        'volume_target': 2, 'intensitas_target': 10,
        'fokus_l1_persen': 5, 'fokus_l2_persen': 10, 'fokus_l3_persen': 25, 'fokus_l4_persen': 60,
    },
}

MINGGU_MINIMUM = 4  # di bawah ini, periodisasi 4 fase gak masuk akal


def hitung_pembagian_minggu(total_minggu):
    """
    Bagi total_minggu ke 4 fase sesuai RASIO_FASE, pembulatan ke bawah,
    sisa pembulatan (kalau ada) ditambahkan ke fase COMP -- biar total
    akhirnya PERSIS sama dengan total_minggu (gak lebih gak kurang).

    Return dict: {'GPP': int, 'SPP': int, 'PRE_COMP': int, 'COMP': int}
    """
    pembagian = {}
    for fase, rasio in RASIO_FASE.items():
        pembagian[fase] = int(total_minggu * rasio)

    sisa = total_minggu - sum(pembagian.values())
    pembagian['COMP'] += sisa  # sisa pembulatan diserap fase terakhir

    return pembagian


def generate_periodisasi_otomatis(macro_program, hapus_lama=False):
    """
    Generate MesoCycle otomatis (GPP -> SPP -> Pre-Comp -> Comp) buat 1
    MacroProgram, berdasarkan tanggal_mulai & tanggal_target-nya.

    Parameter:
        macro_program : instance MacroProgram
        hapus_lama    : kalau True, semua MesoCycle lama milik program
                        ini dihapus dulu sebelum generate ulang. Default
                        False -- biar gak sengaja menghapus data yang
                        udah diedit manual sama pelatih.

    Return dict:
        berhasil : bool
        pesan    : str
        meso_cycles : list of MesoCycle yang berhasil dibuat (kosong kalau gagal)
    """
    total_minggu = macro_program.durasi_minggu

    if total_minggu < MINGGU_MINIMUM:
        return {
            'berhasil': False,
            'pesan': f"Durasi program cuma {total_minggu} minggu -- minimal {MINGGU_MINIMUM} minggu buat periodisasi 4 fase yang masuk akal. Set tanggal_target lebih jauh, atau isi MesoCycle manual.",
            'meso_cycles': [],
        }

    if hapus_lama:
        macro_program.meso_cycles.all().delete()
    elif macro_program.meso_cycles.exists():
        return {
            'berhasil': False,
            'pesan': "Program ini sudah punya MesoCycle. Set hapus_lama=True kalau mau generate ulang dari nol.",
            'meso_cycles': [],
        }

    pembagian_minggu = hitung_pembagian_minggu(total_minggu)

    meso_cycles_dibuat = []
    tanggal_kursor = macro_program.tanggal_mulai
    urutan = 1

    # Urutan fase harus tetap GPP -> SPP -> PRE_COMP -> COMP
    for fase in ['GPP', 'SPP', 'PRE_COMP', 'COMP']:
        durasi_minggu_fase = pembagian_minggu[fase]
        if durasi_minggu_fase <= 0:
            continue

        tanggal_mulai_fase = tanggal_kursor
        tanggal_selesai_fase = tanggal_mulai_fase + timedelta(weeks=durasi_minggu_fase) - timedelta(days=1)

        profil = PROFIL_FASE[fase]
        meso = MesoCycle.objects.create(
            macro_program=macro_program,
            nama_fase=fase,
            urutan=urutan,
            tanggal_mulai=tanggal_mulai_fase,
            tanggal_selesai=tanggal_selesai_fase,
            volume_target=profil['volume_target'],
            intensitas_target=profil['intensitas_target'],
            fokus_l1_persen=profil['fokus_l1_persen'],
            fokus_l2_persen=profil['fokus_l2_persen'],
            fokus_l3_persen=profil['fokus_l3_persen'],
            fokus_l4_persen=profil['fokus_l4_persen'],
        )
        meso_cycles_dibuat.append(meso)

        tanggal_kursor = tanggal_selesai_fase + timedelta(days=1)
        urutan += 1

    return {
        'berhasil': True,
        'pesan': f"Berhasil generate {len(meso_cycles_dibuat)} fase MesoCycle dari total {total_minggu} minggu.",
        'meso_cycles': meso_cycles_dibuat,
    }