from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Specialist(models.Model):
    """Model for dermatology specialists/doctors"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='specialist_profile')
    profile_image = models.ImageField(upload_to='specialists/', null=True, blank=True)
    specialization = models.CharField(max_length=100)
    bio = models.TextField()
    years_of_experience = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=200)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


class Patient(models.Model):
    """Model for patients using the platform"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Service(models.Model):
    """Model for dermatology services offered"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")

    def __str__(self):
        return self.name


class SkinPhoto(models.Model):
    """Model for skin condition photos uploaded by patients"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='skin_photos')
    image = models.ImageField(upload_to='skin_photos/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo by {self.patient} - {self.uploaded_at.strftime('%Y-%m-%d')}"


class Consultation(models.Model):
    """Model for virtual consultation appointments"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='consultations')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    concern_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Related photos for this specific consultation
    photos = models.ManyToManyField(SkinPhoto, blank=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.patient} - {self.service} on {self.date} at {self.time}"


class Appointment(models.Model):
    """Model for simplified appointment booking"""
    SERVICE_CHOICES = [
        ("Skin Consultation", "Skin Consultation"),
        ("Acne Treatment", "Acne Treatment"),
        ("Laser Therapy", "Laser Therapy"),
        ("Anti-Aging Solutions", "Anti-Aging Solutions"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)

    def __str__(self):
        return f"{self.patient} - {self.service} on {self.appointment_date}"


class ConsultationNote(models.Model):
    """Model for notes made by specialists during or after consultations"""
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.consultation} - {self.created_at.strftime('%Y-%m-%d')}"


class Prescription(models.Model):
    """Model for prescriptions given during consultations"""
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication_name} for {self.consultation.patient}"


class Payment(models.Model):
    """Model for consultation payments"""
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('mobile_money', 'Mobile Money'),
        ('paypal', 'PayPal'),
    ]

    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for {self.consultation} - {self.status}"


class AvailabilitySchedule(models.Model):
    """Model for specialist availability schedule"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('specialist', 'day_of_week')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        day = dict(self.DAY_CHOICES)[self.day_of_week]
        return f"{self.specialist} - {day} {self.start_time} to {self.end_time}"


class SpecialistTimeOff(models.Model):
    """Model for tracking specialist time off"""
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='time_off')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.specialist} - Off from {self.start_date} to {self.end_date}"


class ChatMessage(models.Model):
    """Model for chat messages during consultation"""
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"


class Review(models.Model):
    """Model for patient reviews after consultation"""
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.consultation} - {self.rating}/5"


# Add this to your models.py file

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    icon = models.CharField(max_length=50, default='bell')
    type_class = models.CharField(max_length=20, default='primary')
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.user.get_full_name()}"

    @property
    def time_ago(self):
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(self.created_at)

    def get_icon(self):
        """Return the icon for this notification"""
        return self.icon

    def get_type_class(self):
        """Return the type class for UI styling"""
        return self.type_class

    def get_url(self):
        """Return the URL for this notification"""
        return self.url