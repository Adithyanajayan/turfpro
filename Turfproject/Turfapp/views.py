from django.shortcuts import render,redirect
from datetime import datetime,date

def Landing(request):
    return render(request,"landing.html")


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login,logout
from django.contrib import messages
from .models import CustomUser,Turf_details,Booking,Bill,Schedule,SportType


def Register(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        phone = request.POST['phone']
        role = request.POST['role']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']
    

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect('register')

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            phone=phone,
            role=role,
            first_name=first_name,
            last_name=last_name
            
        )
        user.save()

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.role == "player":
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('home')
            else:
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('turfreg')

    return render(request, 'register.html')

from django.contrib.auth import authenticate, login

def Login(request):
    if request.method == 'POST':
         
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.role == "player":
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('home')
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

@login_required
def Turfs(request):
    turfs = Turf_details.objects.all()
    
    return render(request,"turf.html",{'turfs':turfs})

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
        
        

        if Turf_details.objects.filter(name=name).exists():
            return render(request,"turf_reg.html")
        owner = request.user
        
        turf=Turf_details.objects.create(name=name,location=location,owner=owner,price=price,opening_time=opening_time,closing_time=closing_time,length=length,width=width,image=image,has_floodlight=flood_light,has_drinking_water=drinking_water,player_capacity=capacity,extra_features=extra)
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
        return render(request,"profile.html")
    return render(request,"profile.html")


@login_required
def Turf_booking(request,id):
    turf=Turf_details.objects.get(id=id)
    user_id = request.user
    if request.method == "POST":
        turf_id = request.POST.get("turf")
        booking_date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        bookings = Booking.objects.filter(turf=turf_id,date=booking_date)
        start_time_t = datetime.strptime(start_time, "%H:%M")
        end_time_t = datetime.strptime(end_time, "%H:%M")
        
        now = datetime.now()
        current_time = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
        
        today = date.today()
        booking_date_time = datetime.strptime(booking_date, "%Y-%m-%d").date()
        if booking_date_time < today:
            messages.error(request, "Cannot book in the past.")
            return render(request,"turf_booking.html")
        if booking_date_time == today:
            if start_time_t < current_time:
                messages.error(request, "Start time is in the past.")
                return render(request,"turf_booking.html")
                

        duration = (end_time_t-start_time_t).total_seconds()/60
        if duration < 60 or duration%60 != 0:
            messages.error(request, "Booking duration must be at least 1 hour and in whole hours.")
            return render(request,"turf_booking.html",{"turf": turf})
        
        for booking in bookings:
            if start_time_t.time()<turf.opening_time or end_time_t.time()>turf.closing_time:
                messages.error(request, "Booking is outside turf operating hours.")
                return render(request,"turf_booking.html",{"turf": turf})
            
            if start_time_t.time() < booking.end_time and end_time_t.time() > booking.start_time:
                 messages.error(request, "Time slot overlaps with an existing booking.")
                 return render(request,"turf_booking.html",{"turf": turf})
        Booking.objects.create(user=user_id,turf=turf,start_time=start_time,date=booking_date,end_time=end_time,)
        messages.success(request, "Booking successful!")
        return redirect('home')
                
    return render(request,"turf_booking.html",{'turf':turf})

        
@login_required
def Owner_dashboard(request):
    today = date.today()
    turfs = Turf_details.objects.filter(owner_id=request.user.id)
    try:
        booking_today = Booking.objects.filter(turf_id__in=turfs, date=today)
        upcoming_booking = Booking.objects.filter(turf_id__in=turfs, date__gt=today)
    
    except Booking.DoesNotExist:
        booking_today = None
        
    return render(request,"owner_dashboard.html",{'booking_today':booking_today,'upcoming_booking':upcoming_booking})
@login_required
def Booking_history(request):
    user_id = request.user.id
    bookings = Booking.objects.filter(user_id=user_id)
    return render(request,'player_booking.html',{'bookings':bookings})

@login_required
def Owner_turf(request):
    turfs = Turf_details.objects.filter(owner_id=request.user.id)
    return render(request,"owner_turfs.html",{'turfs':turfs})


    
    