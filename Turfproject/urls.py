"""
URL configuration for Turfproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from Turfapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",views.Landing,name="landing"),
    path("register/",views.Register,name="register"),
    path("login/",views.Login,name="login"),
    path("home/",views.Home,name="home"),
    path("turfs/",views.Turfs,name="turfs"),
    path("turfregistration/",views.Turf_Reg,name="turfreg"),
    path("logout/",views.Logout,name='logout'),
    path("profile/",views.Profile,name='profile'),
    path("turf_booking/<int:id>",views.Turf_booking,name='turf_booking'),
    path("owner_dashboard/",views.Owner_dashboard,name='owner_dashboard'),
    path("player_booking/",views.Booking_history,name='player_booking'),
    path("owner_turfs/",views.Owner_turf,name='owner_turfs'),
    path("confirm_booking/<int:booking_id>",views.confirm_booking,name='confirm_booking'),
    path("delete_account/",views.delete_account,name='delete_account'),
    path("delete_turf/<int:turf_id>",views.delete_turf,name='delete_turf'),
    path("turf_management/<int:turf_id>",views.manage_turf,name='manage_turf'),
    path("toggle_status/<int:turf_id>",views.toggle_status,name='toggle_status'),
    path("cancel_booking/<int:booking_id>",views.Cancel_booking,name='cancel_booking'),
    path("admin_dashboard/",views.admin_dashboard,name='admin_dashboard'),
    path("approved/<int:turf_id>",views.approved,name='approved'),
    path("disapproved/<int:turf_id>",views.disapproved,name='disapproved'),
    path("admin_turfmanagement/",views.admin_turfmanagement,name='admin_turfmanagement'),
    path("admin_usermanagement/",views.admin_usermanagement,name='admin_usermanagement'),
    path("user_details/<int:user_id>/", views.user_details, name="user_details"),
    path("block_user/<int:user_id>/", views.block_user, name="block_user"),
    path("unblock_user/<int:user_id>/", views.unblock_user, name="unblock_user"),
    path("download_receipt/<int:booking_id>/", views.download_receipt, name="download_receipt"),
    path('turf/<int:turf_id>/rate/<int:value>/', views.rate_turf, name='rate_turf'),


    
    

    

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
