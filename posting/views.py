import csv
import datetime
from datetime import datetime as dt  # ✅ Rename agar tidak bentrok
import json
from django.http import HttpResponse, JsonResponse
from audioop import reverse
from django.shortcuts import render, get_object_or_404, reverse, redirect
from posting.models import Posting, CustomUser
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, FormView
from django.db.models import Q, Sum
from django.db.models.functions import ExtractMonth
from django.views import View
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages  # Import messages
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.utils.translation import activate

from .models import WasteTransaction, PointsRedemption, CustomUser
from .forms import FormPendaftaran, UpdateProfileForm, UserForm, WasteTransactionForm
# Create your views here.


def index(request):
    postings = Posting.objects.all().order_by('-id')
    paginator = Paginator(postings, 9)
    page = request.GET.get('page')
    postings = paginator.get_page(page)
    slider_data = [
        {
            "image": "img/slider-1.jpeg",
            "title": "Bersama Membangun Masa Depan Hijau",
            "description": "Kami berkomitmen untuk mendukung pengelolaan sampah yang lebih baik demi lingkungan yang lebih sehat."
        },
        {
            "image": "img/slider-2.jpeg",
            "title": "Edukasi dan Inovasi dalam Daur Ulang",
            "description": "Mengajarkan kepada masyarakat bagaimana cara mendaur ulang dengan efektif dan inovatif."
        },
        {
            "image": "img/slider-3.jpeg",
            "title": "Mendukung Ekonomi Sirkular",
            "description": "Mengubah sampah menjadi peluang ekonomi yang berkelanjutan bagi komunitas sekitar."
        },
    ]

    context = {
        'slider_data': slider_data,  # Kirim data slider ke template
        'postings': postings
    }

    return render(request, 'posting/index.html', context)

class SearchPosting(View):
    def get(self, request):
        query = self.request.GET.get('q')
        
        query_list = Posting.objects.filter(
            Q(judul__icontains=query) |
            Q(konten__icontains=query)
            
        )
        
        context = {
            'query_list': query_list,
        }
        
        return render(request, 'posting/search.html', context)


class SignUp(generic.CreateView):
    form_class = FormPendaftaran
    success_url = reverse_lazy('login')  # Redirect ke login setelah signup
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)

   
class DetailPosting(generic.DetailView):
    model = Posting
    template_name = 'posting/detail.html'
    
class AddPost(LoginRequiredMixin,generic.CreateView):
    model = Posting
    fields = ['judul', 'penulis', 'date', 'image', 'konten']
    template_name = 'posting/addpost.html'
    
    def get_success_url(self):
        return reverse('detail', kwargs={'pk':self.object.pk})
    
class UpdatePost(LoginRequiredMixin, UpdateView):
    model = Posting
    fields = ['judul', 'image', 'konten']
    template_name = 'posting/addpost.html'
    
    def get_success_url(self):
        return reverse('detail', kwargs={'pk':self.object.pk})
    
class DeletePost(LoginRequiredMixin,generic.DeleteView):
    model = Posting
    template_name = 'posting/deletepost.html'
    success_url = reverse_lazy('index')
    
class PendaftaranView(FormView):
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('Blog:index')
    
    def get_form_class(self, form_class=None):
        form_class = FormPendaftaran
        return form_class(**self.get_form_class())
    
    def post(self, *args, **kwargs):
        form = self.get_form(self.request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        return render(self.request, self.template_name, {"from": form})
    
@login_required
def check_balance(request):
    return render(request, 'profile/check_balance.html')

@login_required
def transaction_history(request):
    return render(request, 'profile/transaction_history.html')

@login_required
def points_redemption(request):
    return render(request, 'transactions/redeem_points.html')

@login_required
def update_profile(request):
    if request.method == "POST":
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil berhasil diperbarui!")
            return redirect("update_profile")  # Kembali ke halaman profil setelah update
        else:
            messages.error(request, "Terjadi kesalahan. Periksa kembali input Anda.")
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, "profile/update_profile.html", {"form": form})


def is_admin_trc(user):
    return user.is_authenticated and user.role == "admin_trc"

@login_required
@user_passes_test(is_admin_trc)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
@user_passes_test(is_admin_trc)
def manage_users(request):
    return render(request, 'admin/manage_users.html')

@login_required
@user_passes_test(is_admin_trc)
def manage_waste_transactions(request):
    return render(request, 'transactions/manage_transactions.html')

@login_required
@user_passes_test(is_admin_trc)
def reports_analytics(request):
    return render(request, 'reports/reports_dashboard.html')

@login_required
@user_passes_test(is_admin_trc)
def point_redemption_management(request):
    return render(request, 'admin/point_redemption_management.html')

@login_required
@user_passes_test(is_admin_trc)
def admin_profile_management(request):
    return render(request, 'admin/admin_profile_management.html')


# Hanya admin yang bisa mengakses
def is_admin(user):
    return user.is_authenticated and user.role == CustomUser.ADMIN_TRX

# List Users + Search
@login_required
@user_passes_test(is_admin)
def manage_users(request):
    query = request.GET.get('q')
    users = CustomUser.objects.filter(is_superuser=False)  # Jangan tampilkan superadmin di daftar admin

    if query:
        users = users.filter(username__icontains=query) | users.filter(nik__icontains=query) | users.filter(email__icontains=query)

    return render(request, 'users/manage_users.html', {'users': users})

# Add User
@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = False  # Pastikan tidak bisa menambahkan superadmin
            user.save()
            messages.success(request, "Pengguna berhasil ditambahkan.")
            return redirect("manage_users")
        else:
            messages.error(request, "Terjadi kesalahan. Periksa kembali input Anda.")
    else:
        form = UserForm()

    return render(request, "users/add_user.html", {"form": form})

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)  # ✅ Tambahkan request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "User successfully updated!")
            return redirect("manage_users")
        else:
            messages.error(request, "Terjadi kesalahan. Periksa kembali input Anda.")
    else:
        form = UserForm(instance=user)

    return render(request, "users/edit_user.html", {"form": form, "user": user})

# Delete User
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_superuser:  # Cegah admin menghapus superadmin
        messages.error(request, "Anda tidak memiliki izin untuk menghapus superadmin.")
        return redirect("manage_users")

    user.delete()
    messages.success(request, "Pengguna berhasil dihapus.")
    return redirect("manage_users")

# Deactivate User
@login_required
@user_passes_test(is_admin)
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_superuser:  # Cegah admin menonaktifkan superadmin
        messages.error(request, "Anda tidak memiliki izin untuk menonaktifkan superadmin.")
        return redirect("manage_users")

    user.deactivate()
    messages.success(request, "Pengguna berhasil dinonaktifkan.")
    return redirect("manage_users")

@login_required
@user_passes_test(is_admin)
def manage_transactions(request):
    transactions = WasteTransaction.objects.all()

    # Debugging: Cetak data yang dikirim dari form
    print("GET Data:", request.GET)

    query = request.GET.get("q")
    filter_date = request.GET.get("date")
    filter_category = request.GET.get("category")

    if query:
        transactions = transactions.filter(user__username__icontains=query)

    if filter_date:
        transactions = transactions.filter(date__date=filter_date)

    if filter_category:
        transactions = transactions.filter(category=filter_category)

    print("Filtered Transactions:", transactions)  # Cek hasil filter

    return render(request, "transactions/manage_transactions.html", {"transactions": transactions})


@login_required
@user_passes_test(is_admin)
def export_transactions_csv(request):
    """ Mengekspor transaksi dalam format CSV """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="transactions_{datetime.date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Username", "Kategori Sampah", "Berat (kg)", "Poin", "Tanggal"])

    transactions = WasteTransaction.objects.all()
    for t in transactions:
        writer.writerow([t.user.username, t.category, t.weight_kg, t.points, t.date])

    return response

POINTS_RATE = {
    'plastik': 10,  # 10 poin per kg
    'kertas': 5,
    'logam': 15,
    'organik': 3,
    'minyak_jelantah': 8,
}
@login_required
@user_passes_test(is_admin)
def add_transaction(request):
    if request.method == "POST":
        form = WasteTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)

            # Hitung poin berdasarkan kategori sampah
            rate = POINTS_RATE.get(transaction.category, 0)
            transaction.points = int(transaction.weight_kg * rate)
            transaction.save()

            # Tambahkan poin ke saldo user
            user = transaction.user
            user.points += transaction.points
            user.save()

            messages.success(request, "Transaksi berhasil ditambahkan!")
            return redirect("manage_transactions")  # ✅ Redirect ke daftar transaksi

    else:
        form = WasteTransactionForm()

    return render(request, "transactions/add_transaction.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(WasteTransaction, id=transaction_id)

    if request.method == "POST":
        form = WasteTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaksi berhasil diperbarui.")
            return redirect("manage_transactions")
    else:
        form = WasteTransactionForm(instance=transaction)

    return render(request, "transactions/edit_transaction.html", {"form": form, "transaction": transaction})

@login_required
@user_passes_test(is_admin)
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(WasteTransaction, id=transaction_id)
    transaction.delete()
    messages.success(request, "Transaksi berhasil dihapus.")
    return redirect("manage_transactions")

@login_required
@user_passes_test(is_admin)
def reports_dashboard(request):
    months = list(range(1, 13))  # ✅ Kirim daftar bulan 1-12 ke template
    
    # Filter berdasarkan tahun & bulan
    year = request.GET.get('year')
    month = request.GET.get('month')

    transactions = WasteTransaction.objects.all()

    if year:
        transactions = transactions.filter(date__year=year)
    if month:
        transactions = transactions.filter(date__month=month)

    # Hitung total berat sampah & poin
    total_weight = transactions.aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
    total_points = transactions.aggregate(Sum('points'))['points__sum'] or 0

    # Hitung total berat sampah per kategori
    category_data = list(
        transactions.values('category')
        .annotate(total_weight=Sum('weight_kg'))
    )

    # ✅ Debugging: Print ke terminal untuk melihat apakah data ada
    print("Category Data:", category_data)

    return render(request, 'reports/reports_dashboard.html', {
        'months': months,
        'total_weight': total_weight,
        'total_points': total_points,
        'transactions': transactions,
        'category_data': json.dumps(category_data),  # ✅ Kirim JSON untuk grafik
    })

@login_required
@user_passes_test(is_admin)
def export_reports_csv(request):
    """ Mengekspor laporan transaksi dalam format CSV """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="waste_reports_{datetime.date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Username", "Kategori Sampah", "Berat (kg)", "Poin", "Tanggal"])

    transactions = WasteTransaction.objects.all()
    for t in transactions:
        writer.writerow([t.user.username, t.category, t.weight_kg, t.points, t.date])

    return response


@login_required
def transaction_history(request):
    transactions = WasteTransaction.objects.filter(user=request.user).order_by('-date')

    # ✅ Hitung total poin dari transaksi sampah
    earned_points = transactions.aggregate(total_poin=Sum('points'))['total_poin'] or 0

    # ✅ Hitung total poin yang sudah ditukar dari PointsRedemption
    redeemed_points = PointsRedemption.objects.filter(user=request.user, status="approved").aggregate(total_redeemed=Sum('points'))['total_redeemed'] or 0

    # ✅ Kurangi poin yang sudah ditukar
    total_points = earned_points - redeemed_points

    # ✅ Ambil data penukaran poin
    redemptions = PointsRedemption.objects.filter(user=request.user).order_by("-requested_at")

    # Filter berdasarkan kategori & tanggal
    category_filter = request.GET.get('category', '')
    date_filter = request.GET.get('date', '')

    if category_filter:
        transactions = transactions.filter(category=category_filter)

    if date_filter:
        transactions = transactions.filter(date__date=date_filter)

    return render(request, 'transactions/transaction_history.html', {
        'transactions': transactions,
        'total_points': total_points,
        'redemptions': redemptions,  # ✅ Kirim data penukaran poin ke template
        'category_filter': category_filter,
        'date_filter': date_filter
    })


@login_required
def export_transactions_csv(request):
    """
    Ekspor transaksi pengguna dalam format CSV.
    """
    # Set nama file CSV berdasarkan username
    filename = f"transaction_history_{request.user.username}.csv"

    # Set header response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Buat writer untuk menulis data CSV
    writer = csv.writer(response)
    
    # Header CSV
    writer.writerow(['Tanggal', 'Nama Pengguna', 'Kategori Sampah', 'Berat (kg)', 'Poin'])

    # Ambil transaksi berdasarkan user yang sedang login
    transactions = WasteTransaction.objects.filter(user=request.user).order_by('-date')

    # Loop data dan tulis ke CSV
    for transaction in transactions:
        writer.writerow([
            transaction.date.strftime("%Y-%m-%d"),  # Format tanggal
            transaction.user.username,
            transaction.get_category_display(),
            transaction.weight_kg,
            transaction.points
        ])

    return response

@login_required
def redeem_points(request):
    """Menampilkan halaman redeem dengan saldo poin yang diperbarui."""
    earned_points = WasteTransaction.objects.filter(user=request.user).aggregate(total_poin=Sum('points'))['total_poin'] or 0
    redeemed_points = PointsRedemption.objects.filter(user=request.user, status="approved").aggregate(total_redeemed=Sum('points'))['total_redeemed'] or 0

    total_points = earned_points - redeemed_points  # Hitung saldo terbaru

    point_options = [
        {"points": i, "amount": i * 1000}
        for i in range(50, total_points + 1, 50) if i <= total_points
    ]

    if request.method == "POST":
        points_to_redeem = int(request.POST.get("points", 0))

        if any(option["points"] == points_to_redeem for option in point_options):
            if total_points >= points_to_redeem:
                PointsRedemption.objects.create(
                    user=request.user,
                    points=points_to_redeem,
                    amount=points_to_redeem * 1000,
                    status="pending"
                )
                messages.success(request, f"Permintaan penukaran {points_to_redeem} poin telah dikirim.")
                return redirect("redeem_points")
            else:
                messages.error(request, "Poin tidak mencukupi untuk penukaran.")
        else:
            messages.error(request, "Jumlah poin yang dipilih tidak valid.")

    return render(request, "transactions/redeem_points.html", {
        "total_points": total_points,
        "point_options": point_options
    })
# ✅ API untuk mendapatkan saldo terbaru setelah redeem
@login_required
def get_updated_balance(request):
    """Mengembalikan saldo poin terbaru setelah transaksi atau redeem."""
    earned_points = WasteTransaction.objects.filter(user=request.user).aggregate(total_poin=Sum('points'))['total_poin'] or 0
    redeemed_points = PointsRedemption.objects.filter(user=request.user, status="approved").aggregate(total_redeemed=Sum('points'))['total_redeemed'] or 0

    total_points = earned_points - redeemed_points  # Hitung saldo terbaru

    return JsonResponse({"user_points": total_points})

    
def is_admin_trc(user):
    """Cek apakah user adalah admin TRC"""
    return user.is_authenticated and user.role == "admin_trc"

@login_required
@user_passes_test(is_admin)
def point_redemption_management(request):
    pending_requests = PointsRedemption.objects.filter(status="pending")
    all_redemptions = PointsRedemption.objects.all().order_by("-requested_at")

    if request.method == "POST":
        redemption_id = request.POST.get("redemption_id")
        action = request.POST.get("action")
        redemption = get_object_or_404(PointsRedemption, id=redemption_id)
        user = redemption.user  # Ambil pengguna yang melakukan redeem

        if action == "approve":
            if user.points >= redemption.points:
                redemption.status = "approved"
                redemption.approved_at = timezone.now()
                redemption.admin = request.user
                redemption.save()
                messages.success(request, f"Penukaran {redemption.points} poin oleh {user.username} telah disetujui.")
            else:
                messages.error(request, "Pengguna tidak memiliki cukup poin untuk disetujui.")

        elif action == "reject":
            # ✅ Jika ditolak, kembalikan poin ke saldo pengguna
            user.points += redemption.points  # Kembalikan poin
            user.save(update_fields=["points"])  # Simpan perubahan saldo
            redemption.status = "rejected"
            redemption.approved_at = timezone.now()
            redemption.admin = request.user
            redemption.save()
            messages.warning(request, f"Penukaran {redemption.points} poin oleh {user.username} telah ditolak dan poin dikembalikan.")

        return redirect("point_redemption_management")

    return render(request, "admin/point_redemption_management.html", {
        "pending_requests": pending_requests,
        "all_redemptions": all_redemptions,
    })

# ✅ API untuk mengambil saldo terbaru setelah redeem ditolak/diproses
@login_required
def get_updated_balance(request):
    return JsonResponse({"user_points": request.user.points})


@login_required
def redemption_history(request):
    # ✅ Hanya hitung poin yang benar-benar ditukar (approved atau completed)
    total_redeemed_points = PointsRedemption.objects.filter(
        user=request.user, 
        status__in=["approved", "completed"]
    ).aggregate(Sum('points'))['points__sum'] or 0

    redemptions = PointsRedemption.objects.filter(user=request.user).order_by('-requested_at')

    return render(request, 'transactions/redemption_history.html', {
        'total_redeemed_points': total_redeemed_points,  # ✅ Perbaikan perhitungan
        'redemptions': redemptions
    })
    
@login_required
@login_required
def check_balance(request):
    # Menghitung total poin dari transaksi sampah
    earned_points = WasteTransaction.objects.filter(user=request.user).aggregate(total_poin=Sum('points'))['total_poin'] or 0

    # Menghitung total poin yang telah ditukarkan
    redeemed_points = PointsRedemption.objects.filter(user=request.user, status="approved").aggregate(total_redeemed=Sum('points'))['total_redeemed'] or 0

    # Mengurangi poin yang telah ditukarkan dari saldo
    total_points = earned_points - redeemed_points

    # Ambil riwayat transaksi terbaru
    transactions = WasteTransaction.objects.filter(user=request.user).order_by('-date')

    return render(request, 'profile/check_balance.html', {
        'total_points': total_points,
        'transactions': transactions,
    })
    
@login_required
@user_passes_test(is_admin_trc)
def admin_dashboard(request):
    # Statistik utama
    total_users = CustomUser.objects.count()
    total_waste = WasteTransaction.objects.aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
    total_points = WasteTransaction.objects.aggregate(Sum('points'))['points__sum'] or 0
    pending_tasks = PointsRedemption.objects.filter(status="pending").count()

    # ✅ Hitung Total Redeemed Points dari semua pengguna
    total_redeemed_points = PointsRedemption.objects.filter(
        status__in=["approved", "completed"]
    ).aggregate(Sum('points'))['points__sum'] or 0  # Pastikan tidak None

    # ✅ Data per Kategori
    waste_per_category = (
        WasteTransaction.objects
        .values('category')
        .annotate(total_weight=Sum('weight_kg'), total_points=Sum('points'))
        .order_by('category')
    )

    # ✅ Data per Bulan untuk Grafik
    waste_per_month = (
        WasteTransaction.objects
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total_waste=Sum('weight_kg'))
        .order_by('month')
    )

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    months = []
    waste_data = []

    for item in waste_per_month:
        months.append(month_names[item['month'] - 1])
        waste_data.append(item['total_waste'])

    # ✅ Data untuk Grafik per Kategori
    categories = []
    category_weights = []

    for item in waste_per_category:
        categories.append(item['category'])
        category_weights.append(item['total_weight'])

    return render(request, 'admin/admin_dashboard.html', {
        'total_users': total_users,
        'total_waste': total_waste,
        'total_points': total_points,
        'total_redeemed_points': total_redeemed_points,  # ✅ Tambahkan ke template
        'pending_tasks': pending_tasks,
        'waste_per_category': waste_per_category,  # ✅ Data kategori
        'months_json': json.dumps(months),  # ✅ Data bulan
        'waste_data_json': json.dumps(waste_data),  # ✅ Data sampah bulanan
        'categories_json': json.dumps(categories),  # ✅ Data kategori untuk grafik
        'category_weights_json': json.dumps(category_weights),  # ✅ Data berat sampah per kategori
    })
