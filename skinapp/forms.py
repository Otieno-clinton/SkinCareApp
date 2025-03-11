# # accounts/forms.py
# import datetime
# from django import forms
# from django.contrib.auth.hashers import make_password
# from .models import Client
# from .models import Appointment
# from django.core.exceptions import ValidationError
#
# class RegistrationForm(forms.ModelForm):
#     confirm_password = forms.CharField(widget=forms.PasswordInput())
#
#     class Meta:
#         model = Client
#         fields = ['first_name', 'last_name', 'email', 'phone', 'password']
#         widgets = {
#             'password': forms.PasswordInput(),  # Hide password input
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get('password')
#         confirm_password = cleaned_data.get('confirm_password')
#
#         if password and confirm_password and password != confirm_password:
#             raise forms.ValidationError("Passwords do not match.")
#
#         # Hash the password before saving
#         cleaned_data['password'] = make_password(password)  # Secure password storage
#         return cleaned_data
#
#
# class LoginForm(forms.Form):
#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
#     )
#
# class AppointmentForm(forms.ModelForm):
#     class Meta:
#         model = Appointment
#         fields = ['name', 'email', 'appointment_date', 'appointment_time', 'service']
#         widgets = {
#             'appointment_date': forms.DateInput(attrs={'type': 'date'}),
#             'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
#         }


# accounts/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Consultation, Service, SkinPhoto
from .models import Patient, Appointment, Specialist


class PatientRegistrationForm(UserCreationForm):
    """
    Registration form for patients using Django's built-in UserCreationForm
    """
    phone_number = forms.CharField(max_length=20, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        # Set username initial value to email to encourage using email as username
        if 'email' in self.data:
            self.fields['username'].initial = self.data['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                date_of_birth=self.cleaned_data.get('date_of_birth')
            )
        return user


class SpecialistRegistrationForm(UserCreationForm):
    """
    Registration form for specialists/doctors
    """
    specialization = forms.CharField(max_length=100)
    bio = forms.CharField(widget=forms.Textarea)
    years_of_experience = forms.IntegerField(min_value=0)
    qualification = forms.CharField(max_length=200)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        if 'email' in self.data:
            self.fields['username'].initial = self.data['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            Specialist.objects.create(
                user=user,
                specialization=self.cleaned_data.get('specialization'),
                bio=self.cleaned_data.get('bio'),
                years_of_experience=self.cleaned_data.get('years_of_experience'),
                qualification=self.cleaned_data.get('qualification'),
                profile_image=self.cleaned_data.get('profile_image')
            )
        return user


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form that uses Django's AuthenticationForm as the base
    """
    username = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email"


class AppointmentForm(forms.ModelForm):
    """
    Form for scheduling appointments
    """

    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'service']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        appointment = super().save(commit=False)
        if self.patient:
            appointment.patient = self.patient
        if commit:
            appointment.save()
        return appointment


class PatientProfileForm(forms.ModelForm):
    """
    Form for updating patient profile information
    """
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Patient
        fields = ['phone_number', 'date_of_birth', 'medical_history']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, user=None, commit=True):
        patient = super().save(commit=False)

        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if commit:
                user.save()

        if commit:
            patient.save()
        return patient


class ConsultationBookingForm(forms.ModelForm):
    """Form for booking virtual consultations"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Select your preferred consultation date"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        help_text="Select your preferred consultation time"
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the type of consultation service"
    )
    concern_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        help_text="Please describe your skin concern in detail",
        required=False
    )
    upload_photos = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': True}),
        help_text="Upload photos of your skin condition (optional)",
        required=False
    )

    class Meta:
        model = Consultation
        fields = ['service', 'date', 'time', 'concern_description']

    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        today = timezone.now().date()

        if date < today:
            raise forms.ValidationError("Consultation date cannot be in the past.")

        return date

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        service = cleaned_data.get('service')

        if date and time and service:
            # Check if the selected specialist is available at this time
            # This would be implemented based on how specialists are assigned
            pass

        return cleaned_data


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Patient, Specialist


class RegistrationForm(UserCreationForm):
    """
    Form for user registration with fields for both patient and specialist roles
    """
    # Override the password fields to use our custom form styling
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter a strong password'}),
        help_text=_("Must be at least 8 characters with letters and numbers"),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter your password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    # Account type selection
    ACCOUNT_CHOICES = [
        ('patient', 'Patient'),
        ('specialist', 'Specialist'),
    ]
    account_type = forms.ChoiceField(
        choices=ACCOUNT_CHOICES,
        required=True,
        widget=forms.RadioSelect,
        initial='patient',
    )

    # Common fields for both account types
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )

    # Terms agreement
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        error_messages={'required': 'You must agree to the terms and conditions'},
    )

    # Patient-specific fields
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    medical_history = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any important medical history or skin conditions you\'d like us to know about'
        })
    )

    # Specialist-specific fields
    specialization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., Dermatologist, Cosmetic Surgeon'
        })
    )
    years_of_experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    qualification = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g., MD, Board Certified Dermatologist'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Brief description of your professional background and expertise'
        })
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'custom-file-input'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        """
        Validate that the email is not already in use
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different email or log in.")
        return email

    def clean(self):
        """
        Additional validation to ensure required fields are provided based on account type
        """
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')

        # Validate specialist-specific fields
        if account_type == 'specialist':
            specialization = cleaned_data.get('specialization')
            years_of_experience = cleaned_data.get('years_of_experience')
            qualification = cleaned_data.get('qualification')
            bio = cleaned_data.get('bio')

            if not specialization:
                self.add_error('specialization', 'This field is required for specialist accounts')

            if years_of_experience is None:
                self.add_error('years_of_experience', 'This field is required for specialist accounts')

            if not qualification:
                self.add_error('qualification', 'This field is required for specialist accounts')

            if not bio:
                self.add_error('bio', 'This field is required for specialist accounts')

        return cleaned_data

    def save(self, commit=True):
        """
        Save the user and create the associated profile (Patient or Specialist)
        """
        # First save the User model
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

            # Create the appropriate profile based on account type
            account_type = self.cleaned_data['account_type']

            if account_type == 'patient':
                Patient.objects.create(
                    user=user,
                    phone_number=self.cleaned_data.get('phone_number', ''),
                    date_of_birth=self.cleaned_data.get('date_of_birth'),
                    medical_history=self.cleaned_data.get('medical_history', '')
                )
            else:  # specialist
                Specialist.objects.create(
                    user=user,
                    profile_image=self.cleaned_data.get('profile_image'),
                    specialization=self.cleaned_data.get('specialization', ''),
                    bio=self.cleaned_data.get('bio', ''),
                    years_of_experience=self.cleaned_data.get('years_of_experience', 0),
                    qualification=self.cleaned_data.get('qualification', ''),
                    is_available=True
                )

        return user


class LoginForm(forms.Form):
    """
    Form for handling user login authentication
    """
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control border-left-0',
                'placeholder': 'Enter your email',
                'id': 'email'
            }
        ),
        error_messages={
            'required': 'Please enter your email address',
            'invalid': 'Please enter a valid email address'
        }
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control border-left-0',
                'placeholder': 'Enter your password',
                'id': 'password'
            }
        ),
        error_messages={
            'required': 'Please enter your password'
        }
    )

    remember = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'custom-control-input',
                'id': 'remember'
            }
        )
    )

    def clean(self):
        """
        Custom validation to authenticate the user
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Django's default User model uses username for authentication,
            # but we're using email in our form
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)

                if not user:
                    raise ValidationError("Invalid email or password. Please try again.")

                if not user.is_active:
                    raise ValidationError("This account has been deactivated. Please contact support.")

                # Store the authenticated user in the form
                self.user = user

            except User.DoesNotExist:
                # Using the same error message for security reasons
                # (don't want to reveal which emails exist in the system)
                raise ValidationError("Invalid email or password. Please try again.")

        return cleaned_data

    def get_user(self):
        """
        Returns the authenticated user after successful validation
        """
        return getattr(self, 'user', None)


class PasswordResetRequestForm(forms.Form):
    """
    Form for requesting a password reset
    """
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }
        ),
        error_messages={
            'required': 'Please enter your email address',
            'invalid': 'Please enter a valid email address'
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if email exists in the system
        if email and not User.objects.filter(email=email).exists():
            # Don't reveal if email exists for security reasons,
            # but log this for administrative tracking
            # Add this message for developers but not for users
            # Note: Uncomment the next line if you want to notify users
            # raise ValidationError("No account found with this email address.")
            pass

        return email


class ConsultationForm(forms.ModelForm):
    """
    Form for booking virtual consultations with specialists
    """

    # Additional fields not directly in the model but useful
    skin_photos = forms.ModelMultipleChoiceField(
        queryset=SkinPhoto.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select relevant skin photos to share with the specialist"
    )

    # Better widgets for date and time
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select your preferred consultation date"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Select your preferred consultation time"
    )

    class Meta:
        model = Consultation
        fields = [
            'patient', 'specialist', 'service', 'date', 'time',
            'concern_description', 'skin_photos'
        ]
        widgets = {
            'concern_description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please describe your skin concern in detail'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Get patient and specialist_id from kwargs
        self.patient = kwargs.pop('patient', None)
        specialist_id = kwargs.pop('specialist_id', None)
        super(ConsultationForm, self).__init__(*args, **kwargs)

        # Filter specialists to show only available
        self.fields['specialist'].queryset = Specialist.objects.filter(is_available=True)

        # If patient is provided, auto-fill and hide patient field
        if self.patient:
            self.fields['patient'].initial = self.patient
            self.fields['patient'].widget = forms.HiddenInput()
            # Filter skin photos to those belonging to the patient
            self.fields['skin_photos'].queryset = SkinPhoto.objects.filter(patient=self.patient)

        # Pre-select specialist if specialist_id is passed
        if specialist_id:
            self.fields['specialist'].initial = specialist_id

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        specialist = cleaned_data.get('specialist')

        # Validate date is not in the past
        if date and date < timezone.now().date():
            raise ValidationError("Consultation date cannot be in the past.")

        # Validate specialist's availability
        if date and time and specialist:
            day_of_week = date.weekday()

            # Check availability
            availability = specialist.availability.filter(
                day_of_week=day_of_week,
                start_time__lte=time,
                end_time__gte=time,
                is_available=True
            )

            if not availability.exists():
                raise ValidationError(
                    f"Dr. {specialist.user.first_name} {specialist.user.last_name} is not available at the selected time."
                )

            # Check time off
            time_off = specialist.time_off.filter(
                start_date__lte=date,
                end_date__gte=date
            )
            if time_off.exists():
                raise ValidationError(
                    f"Dr. {specialist.user.first_name} {specialist.user.last_name} is on leave on the selected date."
                )

            # Check for conflicts
            conflicts = Consultation.objects.filter(
                specialist=specialist,
                date=date,
                time=time,
                status__in=['scheduled', 'in_progress']
            )
            if conflicts.exists():
                raise ValidationError(
                    "The specialist already has a consultation scheduled at this time. Please select a different time."
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super(ConsultationForm, self).save(commit=False)
        if commit:
            instance.save()
            # Save skin photos
            skin_photos = self.cleaned_data.get('skin_photos')
            if skin_photos:
                instance.photos.set(skin_photos)
        return instance
