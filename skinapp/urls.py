from django.contrib import admin
from django.urls import path
from skinapp import views
from skinapp.views import appointment_confirmation, login_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("appointment/", views.make_appointment, name="appointment"),
    path("appointment/<int:appointment_id>/confirmation/", appointment_confirmation, name="appointment_confirmation"),

    path("contact/", views.contact, name="contact"),
    path("opening/", views.opening, name="opening"),
    path("price/", views.price, name="price"),
    path("service/", views.services, name="service"),
    path("team/", views.team, name="team"),
    path("testimonial/", views.testimonial, name="testimonial"),
    path("registration/", views.register, name="registration"),
    path("login/", login_view, name="login"),
    path("reset/", views.reset, name="reset"),
    path("virtual/", views.virtual, name="virtual"),
    path("specialist/", views.specialist, name="specialist_dashboard"),
    path("", views.landing, name="landing"),







# path("appointment/<int:appointment_id>/confirmation/",
#          views.appointment_confirmation,
#          name="appointment_confirmation"),
    path("appointment/<int:appointment_id>/edit/",
         views.edit_appointment,
         name="edit_appointment"),
    path("appointment/<int:appointment_id>/delete/",
         views.delete_appointment,
         name="delete_appointment"),




    path('consultations/book/', views.book_consultation, name='book_consultation'),
    path('consultations/confirmation/<uuid:booking_id>/', views.consultation_confirmation, name='consultation_confirmation'),



path('specialist/dashboard/', views.dashboard, name='specialist_dashboard'),
    path('specialist/toggle-availability/', views.toggle_specialist_availability, name='toggle_specialist_availability'),
    path('consultation/<str:consultation_id>/details/', views.consultation_details, name='consultation_details'),
    path('consultation/<str:consultation_id>/notes/', views.consultation_notes, name='consultation_notes'),
    path('consultation/<str:consultation_id>/update-notes/', views.update_consultation_notes, name='update_consultation_notes'),
    path('consultation/<str:consultation_id>/start-meeting/', views.start_meeting, name='start_meeting'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/get-new/', views.get_new_notifications, name='get_new_notifications'),
    path('notifications/all/', views.all_notifications, name='all_notifications'),




    path('pay/<int:appointment_id>/', views.pay, name='pay'),
    path('stk/', views.stk, name='stk'),
    path('token/', views.token, name='token'),





]