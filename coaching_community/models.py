"""
coaching_community/models.py
Pilar 5 HPCS -- Komunitas & Media Sosial Pelatih (Coach Network).

CoachPost     : postingan forum problem-solving pelatih.
PostSolution  : balasan/solusi dari pelatih lain atas 1 CoachPost.

CATATAN PRIVASI (PENTING dibaca sebelum bikin views/templates-nya):
CoachPost boleh nyimpen referensi ke Atlet (`atlet_terkait`) buat
keperluan INTERNAL penulis (mis. dia mau buka lagi postingannya sendiri
nanti dan tau ini soal atlet siapa). TAPI identitas atlet ini TIDAK
BOLEH ditampilkan ke pelatih lain di UI manapun -- yang boleh
ditampilkan ke publik cuma `radar_data_snapshot` (angka L1-L4 doang,
sudah dianonimkan). Ini niru pola "Cabor.cabor_obj" -- data sensitif
gak di-expose langsung, cuma nempel di belakang layar.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from combat.models import Atlet, Cabor


KATEGORI_POST_CHOICES = [
    ('kendala',     'Kendala Latihan'),
    ('proyek',      'Proyek / Riset'),
    ('diskusi',     'Diskusi Umum'),
    ('minta_saran', 'Minta Saran Intervensi'),
]

STATUS_POST_CHOICES = [
    ('TERBUKA',  'Terbuka'),
    ('TERJAWAB', 'Sudah Terjawab'),
    ('DITUTUP',  'Ditutup'),
]


class CoachPost(models.Model):
    """1 postingan forum problem-solving pelatih."""
    penulis             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coach_posts')
    judul               = models.CharField(max_length=200)
    isi                 = models.TextField(help_text="Ceritakan kendala/proyek/pertanyaan kamu")
    kategori            = models.CharField(max_length=20, choices=KATEGORI_POST_CHOICES, default='diskusi')
    cabor               = models.ForeignKey(
        Cabor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='coach_posts',
        help_text="Opsional, tag cabor yang relevan sama postingan ini"
    )

    # -- Data tagging anonim (lihat catatan privasi di atas file) -------
    atlet_terkait       = models.ForeignKey(
        Atlet, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='coach_posts_terkait',
        help_text="Referensi INTERNAL penulis saja -- JANGAN pernah ditampilkan ke pelatih lain di UI"
    )
    radar_data_snapshot = models.JSONField(
        null=True, blank=True,
        help_text="Snapshot skor L1-L4 (sudah dianonimkan), mis. {'l1': 7.2, 'l2': 6.5, 'l3': 5.8, 'l4': 6.0}"
    )

    status              = models.CharField(max_length=10, choices=STATUS_POST_CHOICES, default='TERBUKA')
    dibuat_pada         = models.DateTimeField(auto_now_add=True)
    diupdate_pada       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Post Komunitas Pelatih'
        verbose_name_plural = 'Post Komunitas Pelatih'
        ordering            = ['-dibuat_pada']

    def __str__(self):
        return f"{self.judul} — {self.penulis.username}"

    @property
    def jumlah_solusi(self):
        return self.solusi.count()


class PostSolution(models.Model):
    """1 balasan/solusi dari pelatih lain atas 1 CoachPost."""
    post           = models.ForeignKey(CoachPost, on_delete=models.CASCADE, related_name='solusi')
    penulis        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_solutions')
    isi            = models.TextField()
    diterima       = models.BooleanField(default=False, help_text="Ditandai sebagai solusi terbaik oleh penulis post")
    poin_diberikan = models.PositiveIntegerField(default=0, help_text="Poin reputasi yang didapat penulis solusi ini kalau diterima")
    dibuat_pada    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Solusi/Balasan Post'
        verbose_name_plural = 'Solusi/Balasan Post'
        ordering            = ['-diterima', 'dibuat_pada']

    def __str__(self):
        tanda = "[DITERIMA] " if self.diterima else ""
        return f"{tanda}{self.penulis.username} -> {self.post.judul}"

    def save(self, *args, **kwargs):
        # Auto isi poin standar 10 kalau baru ditandai diterima & belum ada poinnya
        if self.diterima and self.poin_diberikan == 0:
            self.poin_diberikan = 10
        super().save(*args, **kwargs)


def hitung_poin_reputasi(user):
    """
    Total poin kontribusi 1 pelatih, dihitung on-the-fly dari semua
    PostSolution miliknya yang sudah ditandai diterima -- sengaja TIDAK
    disimpan sebagai field tersendiri (counter cache) di Tahap 1 ini,
    biar gak ada risiko data ke-desync dari sumber aslinya.
    """
    total = PostSolution.objects.filter(penulis=user, diterima=True).aggregate(total=Sum('poin_diberikan'))
    return total['total'] or 0