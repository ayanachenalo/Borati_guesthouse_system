import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Room, Floor, Booking, Payment, CustomUser,ContactMessage, Feedback, AboutContent
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, login



# 0. User Login View (Google / Chrome Account or Quick Login for Booking)
def user_login_view(request):
    # Namni website kana dhufe yeroo booking qofa akka seenu ykn login godhuuf
    return render(request, 'user_base_templates/user_login.html')

# 1. Fuula Jalqabaa (Home Page & Search / Room Listing) - Guest-tti ilaaluu danda'a
def user_index(request):
    floors = Floor.objects.prefetch_related('rooms').all()
    rooms = Room.objects.filter(status='available')
    
    context = {
        'floors': floors,
        'rooms': rooms,
    }
    return render(request, 'user_base_templates/index.html', context)


# 2. Ibsa Bal'aa Kutaa (Room Detail View) - Guest-tti ilaaluu danda'a
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    context = {'room': room}
    return render(request, 'user_base_templates/room_detail.html', context)



# 3. Checkout & Booking Form (Yeroo booking godhu qofa Google/Chrome account gaafata)
@login_required(login_url='user_login')
def checkout_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if room.status != 'available':
        messages.error(request, "Kutaan kun amma duwwaa miti!")
        return redirect('user_index')

    if request.method == 'POST':
        guest_full_name = request.POST.get('guest_full_name')
        guest_phone = request.POST.get('guest_phone')
        national_id_number = request.POST.get('national_id_number')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        payment_method = request.POST.get('payment_method')
        transaction_ref = request.POST.get('transaction_ref')

        # Gatii kutaa guyyaa (1 night)
        total_price = room.price_per_night

        # 1. Booking Uumuu (Status isaa 'pending' godhi)
        booking = Booking.objects.create(
            user=request.user,
            room=room,
            guest_full_name=guest_full_name,
            guest_phone=guest_phone,
            national_id_number=national_id_number,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            booking_status='pending'  # Admin irraa verification eeggachaa jira
        )

        # 2. Payment record uumuu
        Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            transaction_ref=transaction_ref,
            amount_paid=total_price,
            payment_status='pending'
        )

        # 3. ROOM STATUS JIJJIIRUU: Maamilli booking yeroo godhu kallaattiidhaan 
        # room-ichi akka 'booked' (occupied) ta'u gochuu, akka namni biroo irra deebi'ee book hin goonef
        room.status = 'booked'
        room.save()

        messages.success(request, "Bookingiin keessan milkaa'inaan galmaa'eera! Kaffaltiin keessan mirkaneessa eeggachaa jira.")
        return redirect('booking_success', booking_id=booking.id)

    context = {'room': room}
    return render(request, 'user_base_templates/checkout.html', context)


# 4. Fuula Milkaa'ina Bokingii & Ragee (Receipt & Booking Success)
@login_required(login_url='user_login')
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    context = {'booking': booking}
    return render(request, 'user_base_templates/booking_success.html', context)

#about,contact and feedback views
# Public Views
def about_view(request):
    about = AboutContent.objects.first()
    return render(request, 'user_base_templates/about.html', {'about': about})

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(name=name, email=email, phone=phone, message=message)
        messages.success(request, "Ergaan keessan milkaa'inaan daddarbeera! Galatoomaa.")
        return redirect('contact_page')
        
    return render(request, 'user_base_templates/contact.html')

def feedback_view(request):
    if request.method == 'POST':
        guest_name = request.POST.get('guest_name')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            guest_name=guest_name,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Yaadni keessan nu gaheera. Galatoomaa!")
        return redirect('feedback_page')
        
    feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'user_base_templates/feedback.html', {'feedbacks': feedbacks})

def email_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if email:
            User = get_user_model()
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                }
            )
            
            if created:
                user.set_unusable_password()
                user.save()
                messages.success(request, "Account haaraan email keessaniin uumamee seentaniittu!")
            else:
                messages.success(request, "Milkaa'inaan seentaniittu!")
            
            # --- BAKKA SIRREEFFAME ---
            # Django multiple backend qabaachuu isaa akka beekuuf backend kenneef:
            from django.contrib.auth import load_backend
            backend = 'django.contrib.auth.backends.ModelBackend'  # Default backend kee
            user.backend = backend
            
            login(request, user, backend=backend)
            return redirect('user_index')
        else:
            messages.error(request, "Mee email keessan sirriitti galchaa.")
            
    return render(request, 'user_base_templates/user_login.html')