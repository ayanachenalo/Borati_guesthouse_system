from django.shortcuts import render
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Room, Floor, Booking, Payment, CustomUser

# 1. Fuula Jalqabaa (Home Page & Search / Room Listing)
def user_index(request):
    floors = Floor.objects.prefetch_related('rooms').all()
    rooms = Room.objects.filter(status='available')
    
    context = {
        'floors': floors,
        'rooms': rooms,
    }
    return render(request, 'user_base_templates/index.html', context)


# 2. Ibsa Bal'aa Kutaa (Room Detail View)
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    context = {'room': room}
    return render(request, 'user_base_templates/room_detail.html', context)


# 3. Checkout & Booking Form (Ragaa Imaltuu fi National ID Galchuuf)
@login_required
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

        # Herrega Qabannaa (Gatii guyyaa)
        # Salphaaf guyyaa 1 ta'uu isaaf gatii kutaa qofa fudhanna (yookaan calculation dabalataa hojjechuu dandeessa)
        total_price = room.price_per_night

        # Booking Uumuu (Receipt Number ofumaan `models.py` keessatti uumama)
        booking = Booking.objects.create(
            user=request.user,
            room=room,
            guest_full_name=guest_full_name,
            guest_phone=guest_phone,
            national_id_number=national_id_number,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            booking_status='pending'
        )

        # Payment record uumuu
        Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            transaction_ref=transaction_ref,
            amount_paid=total_price,
            payment_status='pending'
        )

        # Kutaa Status gara 'booked' ykn pending tti qabuu (Ykn kaffaltiin erga mirkanaa'ee booda)
        messages.success(request, "Bokingiin keessan milkaa'inaan galmaa'eera! Kaffaltiin keessan mirkaneessa eeggachaa jira.")
        return redirect('booking_success', booking_id=booking.id)

    context = {'room': room}
    return render(request, 'user_base_templates/checkout.html', context)


# 4. Fuula Milkaa'ina Bokingii &agahee (Receipt & Booking Success)
@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    context = {'booking': booking}
    return render(request, 'user_base_templates/booking_success.html', context)