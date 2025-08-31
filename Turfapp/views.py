from django.shortcuts import render,redirect,get_object_or_404
from datetime import datetime,date,timedelta
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse
from itertools import chain
from django.utils.timezone import now

def Landing(request):
    return render(request,"landing.html")


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login,logout
from django.contrib import messages
from .models import CustomUser,Turf_details,Booking,Rating,Cancelled_booking,SportType


def Register(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        phone = request.POST['phone']
        role = request.POST['role']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']
        image = request.FILES.get('image')
    

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "User already exists")
            return redirect('register')

        user = CustomUser.objects.create_user(
            
            
            email=email,
            password=password,
            phone=phone,
            role=role,
            first_name=first_name,
            last_name=last_name,
            profile_pic = image,
            
        )
        user.save()

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_blocked:
                messages.error(request,"User is bloked by admin")
                return render(request,"login.html")
            if user.role == "player":
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('home')
            elif user.role == "admin":
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('admin_dashboard')
            else :
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('turf_reg')

    return render(request, 'register.html')

from django.contrib.auth import authenticate, login

def Login(request):
    if request.method == 'POST':
        update_boooking_status()
         
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_blocked:
                messages.error(request,"User is bloked by admin")
                return render(request,"login.html")
            if user.role == "player":
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('home')
            elif user.role == "admin":
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('admin_dashboard')

            else:
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('owner_dashboard')
            
            
        else:
            messages.error(request, "Invalid email or password")
            return redirect('login')

    return render(request, 'login.html')

from django.contrib.auth.decorators import login_required

@login_required
def Home(request):
    return render(request, 'home.html')
from django.db.models import Q
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def Turfs(request):
    turfs = Turf_details.objects.filter(status='enabled',is_approved=True)

    search_query = request.GET.get('q', '').strip()
    selected_sport = request.GET.get('sport', '').strip()
    selected_sort = request.GET.get('sort', '').strip()
    selected_district = request.GET.get('district', '').strip()
    
    
    # 🔍 Search by location or name
    if selected_district:
        turfs = turfs.filter(district=selected_district)

    if search_query:
        turfs = turfs.filter(
            Q(location__icontains=search_query) | Q(name__icontains=search_query)
        )

    # 🏀 Filter by sport type
    if selected_sport:
        turfs = turfs.filter(sport_types__id=selected_sport)

    # ↕️ Sorting
    if selected_sort == "price":
        turfs = turfs.order_by("price")
    elif selected_sort == "rating":
        turfs = turfs.order_by("ratings")   # ✅ correct field

    sports = SportType.objects.all()

    return render(request, "turf.html", {
        'turfs': turfs,
        'sports': sports,
        'selected_sport': selected_sport,
        'selected_sort': selected_sort,
        'selected_district': selected_district,
        'search_query': search_query,
        
    })

@login_required
def Turf_Reg(request):
    if request.method == "POST":
        name = request.POST.get("name")
        location = request.POST.get("location")
        price = request.POST.get("price")
        opening_time = request.POST.get("opening_time")
        closing_time = request.POST.get("closing_time")
        sport_types = request.POST.getlist('sport_types')
        length = request.POST.get("length")
        width = request.POST.get("width")
        image = request.FILES.get('image')
        flood_light = request.POST.get('has_floodlight') == 'on'
        drinking_water = request.POST.get('has_drinking_water') == 'on'
        extra = request.POST.get('extra_features')
        capacity = request.POST.get('player_capacity')
        district = request.POST.get('district')
        
        

        if Turf_details.objects.filter(name=name).exists():
            return render(request,"turf_reg.html")
        owner = request.user
        
        turf=Turf_details.objects.create(name=name,location=location,owner=owner,price=price,opening_time=opening_time,closing_time=closing_time,length=length,width=width,image=image,has_floodlight=flood_light,has_drinking_water=drinking_water,player_capacity=capacity,extra_features=extra,district=district)
        for sport_name in sport_types:
            sport_obj, created = SportType.objects.get_or_create(name=sport_name)
            turf.sport_types.add(sport_obj)

        messages.success(request, "Turf registered successfully!")
        return redirect('owner_dashboard')
    return render(request,"turf_reg.html")
    
def Logout(request):
    logout(request)
    return redirect('landing')
    
@login_required
def Profile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        user = request.user

        if first_name:  
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone:
            user.phone = phone
        request.user.save()
        messages.success(request, "User information updated successfully!")
        return render(request,"profile.html")
    messages.success(request, "operartion unsuccessfull")
    return render(request,"profile.html")

from datetime import datetime, timedelta, date
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Turf_details, Booking

@login_required
def Turf_booking(request, id):
    turf = get_object_or_404(Turf_details, id=id)
    user = request.user
    slots = []
    selected_date = request.GET.get("date", date.today().strftime("%Y-%m-%d"))

    # Generate hourly slots based on turf opening & closing times
    start_time = datetime.combine(date.today(), turf.opening_time)
    end_time = datetime.combine(date.today(), turf.closing_time)
    bookings = Booking.objects.filter(turf=turf, date=selected_date)

    current_time = datetime.now()

    while start_time < end_time:
        slot_start = start_time.time()
        slot_end = (start_time + timedelta(hours=1)).time()

        # Check if booked
        booked = bookings.filter(
            start_time__lt=slot_end, end_time__gt=slot_start
        ).exists()

        # Check if slot is in the past (for today)
        past = (selected_date == date.today().strftime("%Y-%m-%d") and
                datetime.combine(date.today(), slot_start) < current_time)

        slots.append({
            "start": slot_start.strftime("%I:%M %p"),
            "end": slot_end.strftime("%I:%M %p"),
            "status": "booked" if booked else ("past" if past else "available")
        })

        start_time += timedelta(hours=1)

    # Handle booking submission
    if request.method == "POST":
        booking_date = request.POST.get("date")
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")

        start_time_t = datetime.strptime(start_time_str, "%H:%M").time()
        end_time_t = datetime.strptime(end_time_str, "%H:%M").time()

        # Date validation
        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
        if booking_date_obj < date.today():
            messages.error(request, "Cannot book in the past.")
            return redirect(request.path + f"?date={booking_date}")

        # Time validation
        if booking_date_obj == date.today() and datetime.combine(date.today(), start_time_t) < current_time:
            messages.error(request, "Start time is in the past.")
            return redirect(request.path + f"?date={booking_date}")
        if start_time_t.minute != 0 or end_time_t.minute != 0:
            messages.error(request,"the start or end time isn't whole")
            return redirect(request.path + f"?date={booking_date}")
        

        # Duration validation
        duration = (datetime.combine(date.today(), end_time_t) -
                    datetime.combine(date.today(), start_time_t)).total_seconds() / 60
        if duration < 60 or duration % 60 != 0:
            messages.error(request, "Booking must be at least 1 hour and in whole hours.")
            return redirect(request.path + f"?date={booking_date}")

        # Overlap check
        if bookings.filter(start_time__lt=end_time_t, end_time__gt=start_time_t).exists():
            messages.error(request, "Time slot overlaps with an existing booking.")
            return redirect(request.path + f"?date={booking_date}")

        # Create booking
        Booking.objects.create(
            user=user,
            turf=turf,
            start_time=start_time_t,
            end_time=end_time_t,
            date=booking_date_obj
        )
        messages.success(request, "Booking successful!")
        return redirect(request.path + f"?date={booking_date}")

    return render(request,"turf_booking.html", {
        "turf": turf,
        "slots": slots,
        "selected_date": selected_date
    })
        
@login_required
def Owner_dashboard(request):
    today = date.today()
    turfs = Turf_details.objects.filter(owner_id=request.user.id)

    try:
        booking_today = Booking.objects.filter(turf_id__in=turfs, date=today)
        upcoming_booking = Booking.objects.filter(turf_id__in=turfs, date__gt=today)
    
    except Booking.DoesNotExist:
        booking_today = None
    

    revenue = weekly_revenue(request.user)
    bookings = Booking.objects.filter(turf__in=turfs)
    no_booking = bookings.count()
    cancelled = Cancelled_booking.objects.filter(turf__in = turfs)
    no_cancelled = cancelled.count()

        
    return render(request,"owner_dashboard.html",{'booking_today':booking_today,'upcoming_booking':upcoming_booking,"revenue":revenue,'no_booking':no_booking,'no_cancelled':no_cancelled})
@login_required
def Booking_history(request):
    update_boooking_status()
    user_id = request.user.id

    bookings = Booking.objects.filter(user_id=user_id).order_by('date', 'start_time')
    cancelled = Cancelled_booking.objects.filter(user_id=user_id).order_by('cancelled_at')

    merged = list(chain(bookings, cancelled))

    # --- Get filters from GET request ---
    status_filter = request.GET.get('statusFilter', 'all')
    date_filter = request.GET.get('dateFilter', 'recent')

    # --- Apply Status Filter ---
    if status_filter == "upcoming":
        merged = [b for b in merged if hasattr(b, 'date') and b.date >= now().date()]
    elif status_filter == "completed":
        merged = [b for b in merged if isinstance(b, Booking) and b.status == "completed"]
    elif status_filter == "cancelled":
        merged = [c for c in merged if hasattr(c, 'cancelled_at')]
    # "all" → show everything

    # --- Apply Date Sorting ---
    if date_filter == "recent":
        merged = sorted(
            merged,
            key=lambda x: getattr(x, 'date', getattr(x, 'cancelled_at', None)),
            reverse=True
        )
    elif date_filter == "oldest":
        merged = sorted(
            merged,
            key=lambda x: getattr(x, 'date', getattr(x, 'cancelled_at', None))
        )

    return render(request, 'player_booking.html', {"bookings": merged})

@login_required
def Owner_turf(request):
    turfs = Turf_details.objects.filter(owner_id=request.user.id)
    number_turf = turfs.count()
    revenue = weekly_revenue(request.user)
    bookings = Booking.objects.filter(turf__in=turfs)
    no_booking = bookings.count()
    
    return render(request,"owner_turfs.html",{'turfs':turfs,'revenue':revenue,'number_turf':number_turf,'no_booking':no_booking})


    
@login_required
def confirm_booking(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)

        booking.status = 'confirmed'  # If you're using this field
        booking.save()
        messages.success(request, "Booking confirmed.")
    
    return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))



@login_required
def delete_account(request):
    user=request.user
    if user.role == 'owner':
        today = date.today()
        turfs = Turf_details.objects.filter(owner=user)
        upcoming_booking = Booking.objects.filter(turf_id__in=turfs, date__gte=today)
        if not upcoming_booking.exists():
            turfs.delete()
            user.delete()
            messages.success(request, "User account and Turfs deleted")
            return redirect("landing")
        
            
            
    else:
        user.delete()
        messages.success(request, "User account deleted successfully!")
        return redirect("landing")
    messages.success(request, "Account cannot be deleted ")
    return render(request,"profile.html")

@login_required  
def manage_turf(request, turf_id):
    turf = get_object_or_404(Turf_details, id=turf_id)

    if request.method == "POST":
        # Update basic info
        turf.name = request.POST.get("name")
        turf.location = request.POST.get("location")
        turf.price = request.POST.get("price")
        turf.player_capacity = request.POST.get("player_capacity")
        turf.length = request.POST.get("length") or None
        turf.width = request.POST.get("width") or None
        turf.opening_time = request.POST.get("opening_time")
        turf.closing_time = request.POST.get("closing_time")
        turf.district = request.POST.get("district")

        # Sports available (multiple checkboxes)
        sports = request.POST.getlist("sport_types")
        turf.sports_available = sports  # If using JSONField or ArrayField

        # Facilities
        turf.has_floodlight = bool(request.POST.get("has_floodlight"))
        turf.has_drinking_water = bool(request.POST.get("has_drinking_water"))

        # Additional features
        turf.extra_features = request.POST.get("extra_features")

        # Image update
        if request.FILES.get("image"):
            turf.image = request.FILES["image"]

        turf.save()
        messages.success(request, "Turf information updated successfully!")
        return redirect("manage_turf", turf_id=turf.id)

    return render(request, "manage_turf.html", {"turf": turf})

@login_required
def toggle_status(request, turf_id):
    turf = get_object_or_404(Turf_details, id=turf_id)
    turf.status = "disabled" if turf.status == "enabled" else "enabled"
    turf.save()
    messages.success(request, f"Turf status changed to {turf.status.capitalize()}")
    return redirect("manage_turf", turf_id=turf.id)

@login_required
def delete_turf(request, turf_id):
    turf = get_object_or_404(Turf_details, id=turf_id)
    today = date.today()
    upcoming_booking = Booking.objects.filter(turf=turf,date__gte=today)
    if not upcoming_booking.exists():
        turf.delete()
        messages.success(request, "Turf deleted successfully.")
        return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))
    messages.error(request, "Cannot delete turf with upcoming bookings.")
    return redirect(request.META.get('HTTP_REFERER', 'manage_turf'))
    
@login_required
def Cancel_booking(request,booking_id):
    booking = get_object_or_404(Booking,id=booking_id)
    Cancelled_booking.objects.create(user=booking.user,turf=booking.turf,start_time=booking.start_time,date=booking.date,end_time=booking.end_time,cancelled_at=datetime.now())  
    booking.delete()
    return redirect('player_booking')  
def weekly_revenue(user):
    turfs = Turf_details.objects.filter(owner_id=user.id)
    seven_days_ago = timezone.now() - timedelta(days=7)
    bookings = Booking.objects.filter(turf__in =turfs,status='confirmed',date__gte=seven_days_ago.date())
    revenue=0
    revenue = sum(booking.total_price for booking in bookings)
    return revenue

def approved(request,turf_id):
    if request.method == 'POST':
        turf = Turf_details.objects.get(id = turf_id)
        turf.is_approved = 'True'
        turf.save()
        messages.success(request,"turf approved successfully")
    return redirect(request.META.get('HTTP_REFERER', 'admin_turfmanagement'))

def disapproved(request,turf_id):
    if request.method == 'POST':
        turf = Turf_details.objects.get(id = turf_id)
        turf.delete()
        messages.success(request,"turf disapproved successfully")
    return redirect(request.META.get('HTTP_REFERER', 'admin_turfmanagement'))
@login_required
def admin_dashboard(request):
    turfs = Turf_details.objects.annotate(booking_count=Count('bookings')).order_by('-booking_count')
    users = CustomUser.objects.filter(role__in=['player', 'owner'])
    return render(request,"admin_dashboard.html",{'turfs':turfs,'users':users})

@login_required
def admin_turfmanagement(request):
    pending_turfs = Turf_details.objects.filter(is_approved=False)
    approved_turfs = Turf_details.objects.filter(is_approved=True)
    return render(request,"admin_turfmanagement.html",{'pending_turfs':pending_turfs,'approved_turfs':approved_turfs})

 

@login_required
def admin_usermanagement(request):
    users = CustomUser.objects.all()
    
    return render(request,"admin_usermanagement.html",{'users':users})


@login_required
def user_details(request,user_id):
    user = get_object_or_404(CustomUser,id=user_id)
    return render(request,"user_details.html",{'user':user})

@login_required
def block_user(request,user_id):
    user = CustomUser.objects.get(id = user_id)
    user.is_blocked = True
    user.save()
   
    return redirect(request.META.get('HTTP_REFERER', 'admin_usermanagement'))


  
@login_required
def unblock_user(request,user_id):
    user = CustomUser.objects.get(id = user_id)
    user.is_blocked = False
    user.save()
    
    return redirect(request.META.get('HTTP_REFERER', 'admin_usermanagement'))


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from .models import Booking

def download_receipt(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    # HTTP response setup
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="receipt_{booking.id}.pdf"'
    
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor("#2E86C1"),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor("#2C3E50"),
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['BodyText'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.HexColor("#2C3E50"),
        alignment=TA_LEFT
    )
    
    highlight_style = ParagraphStyle(
        'CustomHighlight',
        parent=styles['BodyText'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor("#27AE60"),
        alignment=TA_LEFT
    )
    
    footer_style = ParagraphStyle(
        'CustomFooter',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor("#7F8C8D"),
        alignment=TA_CENTER
    )
    
    # Title
    title = Paragraph("TURF BOOKING RECEIPT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Booking Information Table
    booking_data = [
        ["Booking ID:", str(booking.id)],
        ["Customer:", f"{booking.user.first_name} {booking.user.last_name}"],
        ["Turf:", booking.turf.name],
        ["Date:", str(booking.date)],
        ["Time Slot:", f"{booking.start_time} - {booking.end_time}"],
    ]
    
    booking_table = Table(booking_data, colWidths=[1.5*inch, 3*inch])
    booking_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#EAEDED")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#2C3E50")),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor("#D0D3D4")),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor("#D0D3D4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D0D3D4")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(booking_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Payment Information
    payment_heading = Paragraph("Payment Details", heading_style)
    elements.append(payment_heading)
    
    payment_data = [
        ["Description", "Amount (INR)"],
        ["Turf Booking Fee", f"INR {booking.total_price}"],
        ["Tax", "INR 0"],  # You can modify this based on your tax calculation
        ["Total Amount", f"INR {booking.total_price}"]
    ]
    
    payment_table = Table(payment_data, colWidths=[3.5*inch, 1.5*inch])
    payment_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9F9")),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.HexColor("#2C3E50")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor("#2E86C1")),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#2E86C1")),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#2E86C1")),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#D0D3D4")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(payment_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Thank you message
    thank_you = Paragraph("Thank you for choosing our turf facility! We hope you enjoy your game.", highlight_style)
    elements.append(thank_you)
    elements.append(Spacer(1, 0.2*inch))
    
    # Additional information
    info_text = Paragraph("Please bring this receipt with you for verification at the time of your booking.", normal_style)
    elements.append(info_text)
    elements.append(Spacer(1, 0.4*inch))
    
    # Footer
    footer1 = Paragraph("For any queries or support, please contact:", footer_style)
    footer2 = Paragraph("support@turfsystem.com | +91 98765 43210", footer_style)
    footer3 = Paragraph("Business Hours: 6:00 AM - 10:00 PM (All days)", footer_style)
    
    elements.append(footer1)
    elements.append(footer2)
    elements.append(footer3)
    
    # Generate PDF
    doc.build(elements)
    
    return response


def rate_turf(request, turf_id, value):
    turf = get_object_or_404(Turf_details, id=turf_id)
    if request.user.is_authenticated:
        Rating.objects.update_or_create(
            turf=turf,
            user=request.user,
            defaults={'value': int(value)}
        )
    # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    #     return JsonResponse({'avg_rating': turf.average_rating})
    return redirect('player_booking')

from django.shortcuts import redirect, resolve_url

def cancel(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect(resolve_url('home'))

def update_boooking_status():
    bookings = Booking.objects.all()
    for booking in bookings:
        booking.update_status()