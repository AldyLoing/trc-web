from django.conf import settings
from posting.views import DetailPosting, index, update_profile, manage_users, add_user, edit_user, delete_user, deactivate_user, manage_transactions, add_transaction, edit_transaction, delete_transaction, export_transactions_csv, reports_dashboard, export_reports_csv, transaction_history, export_transactions_csv, redeem_points, redemption_history, check_balance, point_redemption_management, admin_dashboard, get_updated_balance
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posting import views 
from django.contrib.auth import views as auth_views 





urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('posting.urls')),
    path("profile/update/", update_profile, name="update_profile"),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('reports-analytics/', views.reports_analytics, name='reports_analytics'),
    path('point-redemption-management/', views.point_redemption_management, name='point_redemption_management'),
    path("users/", manage_users, name="manage_users"),
    path("users/add/", add_user, name="add_user"),
    path("users/edit/<int:user_id>/", edit_user, name="edit_user"),
    path("users/delete/<int:user_id>/", delete_user, name="delete_user"),
    path("users/deactivate/<int:user_id>/", deactivate_user, name="deactivate_user"),
    path("transactions/", manage_transactions, name="manage_transactions"),
    path("transactions/add/", add_transaction, name="add_transaction"),
    path("transactions/edit/<int:transaction_id>/", edit_transaction, name="edit_transaction"),
    path("transactions/delete/<int:transaction_id>/", delete_transaction, name="delete_transaction"),
    path("transactions/export/", export_transactions_csv, name="export_transactions_csv"),
    path("reports/", reports_dashboard, name="reports_dashboard"),
    path("reports/export/", export_reports_csv, name="export_reports_csv"),
    path('transaction-history/', transaction_history, name='transaction_history'),
    path('export-transactions/', export_transactions_csv, name='export_transactions_csv'),
    path('redeem-points/', redeem_points, name='redeem_points'),
    path('redemption-history/', redemption_history, name='redemption_history'),
    path("check-balance/", check_balance, name="check_balance"),
    path('point-redemption/', point_redemption_management, name='point_redemption_management'),
    path('template\admin\admin_dashboard', admin_dashboard, name='admin_dashboard'),
    path('get-updated-balance/', get_updated_balance, name='get_updated_balance'),  # ✅ API baru

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)