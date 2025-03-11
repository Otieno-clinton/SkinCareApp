import json
from datetime import timedelta
import datetime  # Add this import at the top of your file

import requests
from django.shortcuts import render, redirect
from django.urls import reverse

# from .forms import RegistrationForm
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from requests.auth import HTTPBasicAuth

# from .forms import LoginForm
from .forms import AppointmentForm, RegistrationForm, LoginForm, ConsultationForm
# from .models import Client
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Appointment, Patient, ConsultationNote



from skinapp.credentials import MpesaAccessToken, LipanaMpesaPpassword #for mpesa integration




def home(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def appointment(request):
    return render(request, "appointment.html")

def contact(request):
    return render(request, "contact.html")

def opening(request):
    return render(request, "opening.html")

def price(request):
    return render(request, "price.html")

def services(request):
    return render(request, "service.html")

def team(request):
    return render(request, "team.html")

def testimonial(request):
    return render(request, "testimonial.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import RegistrationForm


def register(request):
    if request.method == 'POST':
        # Make sure to include request.FILES for handling image uploads
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the user and associated profile (Patient or Specialist)
                user = form.save()

                # Log the user in
                login(request, user)

                # Add success message
                account_type = form.cleaned_data.get('account_type')
                messages.success(request, f"Your {account_type} account has been created successfully!")

                return redirect('login')  # Or any appropriate redirect
            except Exception as e:
                import traceback
                print("Error saving user:", str(e))
                traceback.print_exc()  # This will print the full error traceback in the console
                messages.error(request, "An error occurred while creating your account. Please try again.")
        else:
            # If form is invalid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()

    return render(request, 'registration.html', {'form': form})




def reset(request):
    return render(request, "resetpassword.html")

def landing(request):
    return render(request, "landing.html")


def make_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()  # Save appointment and get its ID
            return redirect(reverse('appointment_confirmation', args=[appointment.id]))  # Pass the appointment ID
        else:
            return render(request, "appointment.html", {"form": form})
    else:
        form = AppointmentForm()
    return render(request, "appointment.html", {"form": form})


def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, "appointment_confirmation.html", {"appointment": appointment})


def edit_appointment(request, appointment_id):
    """
    Allow users to edit their appointment details
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Prevent editing past appointments
    if appointment.appointment_date < timezone.now().date():
        messages.error(request, "Cannot edit past appointments")
        return redirect("appointment_confirmation", appointment_id=appointment_id)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully!")
            return redirect("appointment_confirmation", appointment_id=appointment_id)
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "edit.html", {
        "form": form,
        "appointment": appointment
    })


def delete_appointment(request, appointment_id):
    """
    Allow users to cancel their appointments
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Prevent deleting past appointments
    if appointment.appointment_date < timezone.now().date():
        messages.error(request, "Cannot cancel past appointments")
        return redirect("appointment_confirmation", appointment_id=appointment_id)

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment cancelled successfully!")
        return redirect("home")

    return render(request, "appointment.html", {
        "appointment": appointment
    })



def virtual(request):
    return render(request, "virtual.html")

def specialist(request):
    return render(request, "specialist_dashboard.html")


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Consultation, SkinPhoto, Specialist
from .forms import ConsultationBookingForm


@login_required
def book_consultation(request, specialist_id=None):
    """
    View for handling virtual consultation booking by a patient.
    Optionally pre-fills specialist if specialist_id is passed.
    """
    try:
        # Get patient profile of logged-in user
        patient = request.user.patient_profile
    except AttributeError:
        messages.error(request, "You need a patient profile to book a consultation.")
        return redirect('create_patient_profile')  # Redirect if no patient profile

    if request.method == 'POST':
        form = ConsultationForm(request.POST, patient=patient, specialist_id=specialist_id)  # Pass specialist_id for consistency
        if form.is_valid():
            # Save consultation
            consultation = form.save(commit=False)
            consultation.patient = patient  # Auto-assign patient

            if not consultation.specialist:
                messages.error(request, "Please select a specialist for your consultation.")
                return render(request, 'virtual.html', {'form': form})

            consultation.save()  # Now save fully

            # Handle selected skin photos (ManyToMany)
            skin_photos = form.cleaned_data.get('skin_photos')
            if skin_photos:
                consultation.photos.set(skin_photos)

            # Success message
            messages.success(
                request,
                f"Your consultation has been scheduled for {consultation.date} at {consultation.time}."
            )
            return redirect('consultation_confirmation', booking_id=consultation.booking_id)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        # On GET, initialize form with patient and optional specialist
        form = ConsultationForm(patient=patient, specialist_id=specialist_id)

    return render(request, 'virtual.html', {
        'form': form,
        'page_title': 'Book a Virtual Consultation'
    })



@login_required
def consultation_confirmation(request, booking_id):
    """View for displaying consultation confirmation"""
    try:
        consultation = Consultation.objects.get(booking_id=booking_id, patient=request.user.patient_profile)
    except Consultation.DoesNotExist:
        messages.error(request, "Consultation booking not found.")
        return redirect('dashboard')

    return render(request, 'virtual.html', {
        'consultation': consultation,
        'page_title': 'Consultation Confirmation'
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            # Log the user in
            login(request, user)

            # Handle "remember me" option
            if not form.cleaned_data.get('remember'):
                request.session.set_expiry(0)

            # Determine user type and redirect accordingly
            try:
                # Check if user is a specialist
                specialist = Specialist.objects.get(user=user)
                messages.success(request, f"Welcome back, Dr. {user.first_name} {user.last_name}!")
                return redirect('specialist_dashboard')
            except Specialist.DoesNotExist:
                try:
                    # Check if user is a patient
                    patient = Patient.objects.get(user=user)
                    messages.success(request, f"Welcome back, {user.first_name} {user.last_name}!")
                    return redirect('home')
                except Patient.DoesNotExist:
                    # User has neither profile, could be admin or new user
                    messages.warning(request, "Your account is not fully set up. Please contact support.")
                    return redirect('registration')
        else:
            # Add a message about login failure
            messages.error(request, "Login failed. Please check your credentials.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def dashboard(request):
    # Get the logged-in specialist
    try:
        specialist = Specialist.objects.get(user=request.user)
    except Specialist.DoesNotExist:
        # Handle the case where the user isn't a specialist
        return render(request, 'error.html', {'message': 'Unauthorized access.'})

    # Get today's date
    today = timezone.now().date()

    # Get today's appointments (consultations)
    todays_consultations = Consultation.objects.filter(
        specialist=specialist,
        date=today
    ).select_related('patient', 'patient__user', 'service')

    # Count today's appointments
    todays_appointments_count = todays_consultations.count()

    # Count completed appointments today
    completed_today = todays_consultations.filter(status='completed').count()

    # Get appointments for the current week
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    upcoming_week = Consultation.objects.filter(
        specialist=specialist,
        date__range=[today, week_end],
        status='scheduled'
    ).count()

    # Get instant meeting requests (consultations that are urgent)
    # For this example, we're assuming consultations with an "urgent" flag or certain services
    # might require immediate attention
    urgent_consultations = Consultation.objects.filter(
        specialist=specialist,
        date=today,
        status='scheduled',
        concern_description__icontains='urgent'  # This is an example - adjust based on your needs
    ).select_related('patient', 'patient__user', 'service')[:5]

    # Count urgent consultations
    urgent_consultations_count = urgent_consultations.count()

    # Get the specialist's availability status
    is_available = specialist.is_available

    context = {
        'specialist': specialist,
        'todays_date': today,
        'todays_appointments_count': todays_appointments_count,
        'completed_today': completed_today,
        'upcoming_week': upcoming_week,
        'urgent_consultations': urgent_consultations,
        'urgent_consultations_count': urgent_consultations_count,
        'is_available': is_available,
        'todays_consultations': todays_consultations,
    }

    return render(request, 'specialist_dashboard.html', context)


@login_required
def view_patient_details(request, consultation_id):
    try:
        consultation = Consultation.objects.get(
            id=consultation_id,
            specialist__user=request.user
        )
    except Consultation.DoesNotExist:
        return render(request, 'error.html', {'message': 'Consultation not found.'})

    # Get previous consultations for this patient with this specialist
    previous_consultations = Consultation.objects.filter(
        patient=consultation.patient,
        specialist__user=request.user,
        date__lt=consultation.date  # Only consultations before the current one
    ).order_by('-date')

    # Get consultation notes if the consultation is completed
    consultation_notes = None
    if consultation.status == 'completed':
        consultation_notes = ConsultationNote.objects.filter(
            consultation=consultation
        ).first()

    context = {
        'consultation': consultation,
        'patient': consultation.patient,
        'previous_consultations': previous_consultations,
        'consultation_notes': consultation_notes,
    }

    return render(request, 'patient_details.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from .models import Specialist, Consultation, Notification  # Adjust based on your actual models



@login_required
def specialist_dashboard(request):
    # Get specialist information
    specialist = get_object_or_404(Specialist, user=request.user)

    # Get today's consultations
    today_consultations = Consultation.objects.filter(
        specialist=specialist,
        date=datetime.date.today()
    ).order_by('time')

    # Get urgent consultations
    urgent_consultations = Consultation.objects.filter(
        specialist=specialist,
        status='scheduled',  # Using status instead of is_urgent which doesn't seem to exist
        concern_description__icontains='urgent'  # As you did in the dashboard view
    ).order_by('created_at')

    # Get unread notifications - fix the recipient filter
    notifications = Notification.objects.filter(
        recipient=specialist,  # Changed from request.user to specialist
        is_read=False
    ).order_by('-created_at')

    # Rest of your function remains the same
    # ...


@login_required
@require_POST
def mark_notification_read(request):
    notification_id = request.POST.get('notification_id')
    specialist = get_object_or_404(Specialist, user=request.user)
    notification = get_object_or_404(Notification, id=notification_id, recipient=specialist)

    notification.is_read = True
    notification.save()

    return JsonResponse({'status': 'success'})


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification, Specialist


@login_required
def get_new_notifications(request):
    print(f"request.user: {request.user}")

    # Retrieve specialist once (if needed for other logic)
    specialist = get_object_or_404(Specialist, user=request.user)

    # Get timestamp of last check from session
    last_check_str = request.session.get('last_notification_check', None)

    # Convert the string to a timezone-aware datetime object, if it exists
    last_check = None
    if last_check_str:
        try:
            last_check = timezone.make_aware(
                datetime.datetime.fromisoformat(last_check_str),
                timezone.get_current_timezone()
            )
        except ValueError:
            last_check = None  # Invalid format

    # Update the timestamp for next check
    now = timezone.now()
    request.session['last_notification_check'] = now.isoformat()

    # Query for new notifications
    query = Notification.objects.filter(recipient=request.user, is_read=False)
    if last_check:
        query = query.filter(created_at__gt=last_check)

    # Optional: Limit to recent 10-20 notifications
    new_notifications = []
    for notification in query[:20]:  # Adjust limit as needed
        new_notifications.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'icon': notification.get_icon(),
            'type_class': notification.get_type_class(),
            'url': notification.get_url()
        })

    return JsonResponse({
        'status': 'success',
        'new_notifications': new_notifications
    })


@login_required
def all_notifications(request):
    specialist = get_object_or_404(Specialist, user=request.user)
    notifications = Notification.objects.filter(recipient=specialist).order_by('-created_at')

    return render(request, 'specialists/all_notifications.html', {'notifications': notifications})


@login_required
@require_POST
def toggle_specialist_availability(request):
    specialist_id = request.POST.get('specialist_id')
    is_available = request.POST.get('is_available') == 'true'

    specialist = get_object_or_404(Specialist, id=specialist_id, user=request.user)
    specialist.is_available = is_available
    specialist.save()

    return JsonResponse({
        'status': 'success',
        'message': 'Availability status updated successfully',
        'is_available': specialist.is_available
    })


@login_required
def consultation_details(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id, specialist__user=request.user)

    context = {
        'consultation': consultation,
        'patient': consultation.patient,
        'medical_history': consultation.patient.medical_history.all() if hasattr(consultation.patient,
                                                                                 'medical_history') else []
    }

    return render(request, 'specialists/consultation_details_partial.html', context)


@login_required
def consultation_notes(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id, specialist__user=request.user)

    context = {
        'consultation': consultation,
        'notes': consultation.notes or "No notes available for this consultation."
    }

    return render(request, 'specialists/consultation_notes_partial.html', context)


@login_required
@require_POST
def update_consultation_notes(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id, specialist__user=request.user)

    notes = request.POST.get('notes', '')
    consultation.notes = notes
    consultation.save()

    # Render the notes HTML for the response
    context = {
        'consultation': consultation,
        'notes': consultation.notes
    }
    notes_html = render_to_string('specialists/consultation_notes_partial.html', context)

    return JsonResponse({
        'status': 'success',
        'message': 'Notes updated successfully',
        'notes_html': notes_html
    })


@login_required
def start_meeting(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id, specialist__user=request.user)

    # Update consultation status if needed
    if consultation.status == 'pending':
        consultation.status = 'in_progress'
        consultation.save()

    # Redirect to meeting room or video chat implementation
    return redirect('meeting_room', meeting_id=consultation_id)


@login_required
@require_POST
def mark_notification_read(request):
    notification_id = request.POST.get('notification_id')
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    notification.is_read = True
    notification.save()

    return JsonResponse({'status': 'success'})


@login_required
def get_new_notifications(request):
    # Get timestamp of last check from request or session
    last_check = request.session.get('last_notification_check', None)

    # Update the timestamp for next check
    request.session['last_notification_check'] = str(datetime.datetime.now())

    # Query for new notifications
    query = Notification.objects.filter(recipient=request.user, is_read=False)
    if last_check:
        query = query.filter(created_at__gt=last_check)

    new_notifications = []
    for notification in query:
        new_notifications.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'icon': notification.get_icon(),
            'type_class': notification.get_type_class(),
            'url': notification.get_url()
        })

    return JsonResponse({
        'status': 'success',
        'new_notifications': new_notifications
    })


from django.shortcuts import get_object_or_404

@login_required
def all_notifications(request):
    specialist = get_object_or_404(Specialist, user=request.user)  # Ensure user is a Specialist
    notifications = Notification.objects.filter(recipient=specialist.user)

    return render(request, 'specialist/all_notifications.html', {'notifications': notifications})


def token(request):
    consumer_key = '1ktP51i1jECFDDd8UdimELCE2cAZyjO4Uz6ufF5GDbpohIpd'
    consumer_secret = 'qUbtwAnveOESfoJ7M8sj0CbeQww6TmvpzMcoWiQm5iGwlKPGrF65MlZ65dmuZ5f1'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

# def pay(request):
#    return render(request, 'pay.html')

def pay(request, appointment_id):
    # Payment processing logic
    return render(request, 'pay.html', {'appointment_id': appointment_id})

def stk(request):
    if request.method =="POST":
        phone = request.POST.get('phone_number')
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Clinton",
            "TransactionDesc": "Web Development Charges"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse("Success")

