from django.contrib import admin
# from .models import Client, Appointment  # Import the Client model
#
# admin.site.register(Client)
# admin.site.register(Appointment)

from django.contrib import admin
from .models import (
    Specialist, Patient, Service, SkinPhoto, Consultation,
    Appointment, ConsultationNote, Prescription, Payment,
    AvailabilitySchedule, SpecialistTimeOff, ChatMessage, Review
)


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'specialization', 'years_of_experience', 'is_available')
    list_filter = ('specialization', 'is_available', 'years_of_experience')
    search_fields = ('user__first_name', 'user__last_name', 'specialization', 'qualification')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone_number', 'date_of_birth')
    search_fields = ('user__first_name', 'user__last_name', 'phone_number')
    list_filter = ('date_of_birth',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name', 'description')


@admin.register(SkinPhoto)
class SkinPhotoAdmin(admin.ModelAdmin):
    list_display = ('patient', 'uploaded_at', 'description')
    list_filter = ('uploaded_at',)
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'description')
    date_hierarchy = 'uploaded_at'


class ConsultationNoteInline(admin.TabularInline):
    model = ConsultationNote
    extra = 1


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 1


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp',)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'patient', 'specialist', 'service', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'service')
    search_fields = (
        'patient__user__first_name', 'patient__user__last_name',
        'specialist__user__first_name', 'specialist__user__last_name',
        'booking_id', 'concern_description'
    )
    date_hierarchy = 'date'
    inlines = [ConsultationNoteInline, PrescriptionInline, ChatMessageInline]
    filter_horizontal = ('photos',)
    readonly_fields = ('booking_id', 'created_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'service', 'appointment_date', 'appointment_time')
    list_filter = ('service', 'appointment_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'service')
    date_hierarchy = 'appointment_date'


@admin.register(ConsultationNote)
class ConsultationNoteAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('consultation__patient__user__first_name', 'consultation__patient__user__last_name', 'content')
    date_hierarchy = 'created_at'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medication_name', 'consultation', 'dosage', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'consultation__patient__user__first_name', 'consultation__patient__user__last_name',
        'medication_name', 'instructions'
    )
    date_hierarchy = 'created_at'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = (
        'consultation__patient__user__first_name', 'consultation__patient__user__last_name',
        'transaction_id'
    )
    readonly_fields = ('transaction_id',)


@admin.register(AvailabilitySchedule)
class AvailabilityScheduleAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'get_day_display', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available')
    search_fields = ('specialist__user__first_name', 'specialist__user__last_name')

    def get_day_display(self, obj):
        return dict(obj.DAY_CHOICES)[obj.day_of_week]

    get_day_display.short_description = 'Day'


@admin.register(SpecialistTimeOff)
class SpecialistTimeOffAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'start_date', 'end_date', 'reason')
    list_filter = ('start_date', 'end_date')
    search_fields = ('specialist__user__first_name', 'specialist__user__last_name', 'reason')
    date_hierarchy = 'start_date'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'consultation', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('sender__first_name', 'sender__last_name', 'message')
    date_hierarchy = 'timestamp'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = (
        'consultation__patient__user__first_name', 'consultation__patient__user__last_name',
        'comment'
    )
    date_hierarchy = 'created_at'