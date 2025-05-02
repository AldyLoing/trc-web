from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Pastikan ini digunakan untuk AUTH_USER_MODEL
from datetime import datetime

# ✅ Model CustomUser yang benar
class CustomUser(AbstractUser):
    ADMIN_TRX = 'admin_trc'
    MEMBER = 'member'

    ROLE_CHOICES = [
        (ADMIN_TRX, 'Admin TRC'),
        (MEMBER, 'Member'),
    ]

    nik = models.CharField(max_length=16, unique=True, blank=False, null=False)  
    email = models.EmailField(unique=True)
    nomor_hape = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)  
    is_active = models.BooleanField(default=True)  
    points = models.IntegerField(default=0)  
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True, 
        default='default-avatar.png'
    )

    def deactivate(self):
        """Nonaktifkan pengguna tanpa menghapus"""
        self.is_active = False
        self.save()

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

# ✅ Model Posting
class Posting(models.Model):
    judul = models.CharField(max_length=200)
    konten = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)

    # Gunakan settings.AUTH_USER_MODEL agar sesuai dengan model CustomUser
    penulis = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.judul

# ✅ Model Transaksi Sampah
class WasteTransaction(models.Model):
    CATEGORY_CHOICES = [
        ('plastik', 'Plastik'),
        ('kertas', 'Kertas'),
        ('logam', 'Logam'),
        ('organik', 'Organik'),
        ('minyak_jelantah', 'Minyak Jelantah'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    weight_kg = models.FloatField()
    points = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Menghitung poin berdasarkan berat sampah """
        point_values = {
            'plastik': 10,
            'kertas': 5,
            'logam': 15,
            'organik': 2,
            'minyak_jelantah': 20,
        }
        self.points = int(self.weight_kg * point_values[self.category])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.category} ({self.weight_kg} kg) - {self.points} points"

# ✅ Model Permintaan Penukaran Poin
class PointsRedemption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()  # ✅ Pastikan kolom ini ada
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_redemptions"
    )

    def __str__(self):
        return f"{self.user.username} - {self.points} Poin ({self.status})"
