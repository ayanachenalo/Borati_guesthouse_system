from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Building, Room, Floor, Booking, Payment, Expense,ContactMessage,AboutContent, Feedback, CustomUser
from functools import wraps
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

# Custom Decorator: Admin qofa akka seensisuuf
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # User-ichi log in godhee jiraachuu fi is_staff ykn is_superuser ta'uu isaa mirkaneessa
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Eeyyama admin hin qabdu!")
        return redirect('admin_login') # Gara fuula login-tti deebisa
    return wrapper

# Admin Login View
def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f"Baga nagaan dhuftan, {user.username}!")
                return redirect('admin_room_management')
            else:
                messages.error(request, "Akka admin-tti seenuuf eeyyama hin qabdu.")
        else:
            messages.error(request, "Maqaa fayyadamaa ykn password dogoggorteetta.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'admin_base_templates/loginadmin.html', {'form': form})


def admin_logout_view(request):
    logout(request)
    messages.success(request, "Milkaa'inaan system keessaa baateetta.")
    return redirect('admin_login')

@login_required
@admin_required
def admin_dashboard(request):
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    booked_rooms = Room.objects.filter(status='booked').count()
    
    pending_payments = Payment.objects.filter(payment_status='pending').count()
    total_revenue = Payment.objects.filter(payment_status='verified').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_revenue - total_expenses

    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'booked_rooms': booked_rooms,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
    }
    return render(request, 'admin_base_templates/dashboard.html', context)


@login_required
@admin_required
def room_management(request):
    floors = Floor.objects.prefetch_related('rooms').all()
    context = {'floors': floors}
    return render(request, 'admin_base_templates/room_management.html', context)

@login_required
@admin_required
def add_room(request):
    if request.method == 'POST':
        floor_id = request.POST.get('floor')
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        price = request.POST.get('price_per_night')
        description = request.POST.get('description')
        
        # Fakkii asitti qabamuu isaa mirkaneessi
        main_image = request.FILES.get('main_image')

        floor = get_object_or_404(Floor, id=floor_id)
        
        Room.objects.create(
            floor=floor,
            room_number=room_number,
            room_type=room_type,
            price_per_night=price,
            description=description,
            main_image=main_image
        )
        messages.success(request, f"Kutaan {room_number} milkaa'inaan galmaa'eera!")
        return redirect('admin_room_management')
    
    floors = Floor.objects.all()
    return render(request, 'admin_base_templates/room_form.html', {'floors': floors})

@login_required
@admin_required
def booking_verification(request):
    query = request.GET.get('search_query', '')
    
    # Kutaalee / Booking-oota verification (pending) eegaa jiran qofa filter godhee fida
    bookings = Booking.objects.filter(booking_status='pending')
    
    if query:
        bookings = bookings.filter(
            models.Q(receipt_number__iexact=query) | 
            models.Q(national_id_number__iexact=query) |
            models.Q(guest_phone__icontains=query) |
            models.Q(guest_full_name__icontains=query)
        )

    context = {
        'bookings': bookings,
        'query': query,
    }
    return render(request, 'admin_base_templates/booking_list.html', context)

@login_required
@admin_required
def process_check_in(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.is_receipt_used:
        messages.error(request, "Reesitiin kun kanaan dura itti fayyadameera (Already Verified)!")
    else:
        # 1. Booking Status gara 'confirmed' ykn 'checked_in' tti jijjiiruu
        booking.booking_status = 'confirmed'
        booking.is_receipt_used = True
        booking.save()
        
        # 2. Room Status gara 'booked' (occupied) tti jijjiiruu
        if booking.room:
            room = booking.room
            room.status = 'booked'
            room.save()
        
        messages.success(request, f"Imaltuun {booking.guest_full_name} milkaa'inaan approve ta'eera, kutaan ammaa booked ta'eera!")
        
    return redirect('admin_booking_verification')


@login_required
@admin_required
def financial_report(request):
    total_revenue = Payment.objects.filter(payment_status='verified').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_revenue - total_expenses
    
    recent_revenues = Payment.objects.filter(payment_status='verified').select_related('booking', 'booking__room').order_by('-id')[:10]
    recent_expenses = Expense.objects.all().order_by('-expense_date', '-id')[:10]
    
    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'recent_revenues': recent_revenues,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'admin_base_templates/financial_report.html', context)


@login_required
@admin_required
def verify_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    action = request.POST.get('action') # 'verify' ykn 'reject'
    
    if action == 'verify':
        payment.payment_status = 'verified'
        payment.verified_by = request.user
        payment.save()
        
        # Booking Status Confirmed gochuu
        booking = payment.booking
        booking.booking_status = 'confirmed'
        booking.save()
        messages.success(request, "Kaffaltiin mirkanaa'eera!")
    elif action == 'reject':
        payment.payment_status = 'rejected'
        payment.save()
        messages.warning(request, "Kaffaltiin fashala'eera!")
        
    return redirect('admin_financial_report')

@login_required
@admin_required
def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        date = request.POST.get('expense_date')
        description = request.POST.get('description')
        
        Expense.objects.create(
            title=title,
            amount=amount,
            expense_date=date,
            description=description,
            created_by=request.user
        )
        messages.success(request, "Baasiin milkaa'inaan galmaa'eera!")
        return redirect('admin_financial_report')
        
    return render(request, 'admin_base_templates/expense_form.html')

@login_required
@admin_required
def add_floor(request):
    if request.method == 'POST':
        building_name = request.POST.get('building_name').strip()
        floor_name = request.POST.get('name').strip()
        description = request.POST.get('description', '')
        
        if building_name and floor_name:
            # Gamoon sun yoo jiraate fida, yoo hin jirre haaraa uuma
            building, created = Building.objects.get_or_create(
                building_name=building_name,
                defaults={'total_floors': 5, 'location': 'Bule Hora'}
            )
            
            # Floor haaraa gamoo kana jalatti uumuu
            Floor.objects.create(
                building=building,
                floor_name=floor_name,
                description=description
            )
            messages.success(request, f"Floor '{floor_name}' gamoo '{building.building_name}' jalatti milkaa'inaan galmaa'eera!")
            return redirect('admin_room_management')
        else:
            messages.error(request, "Maaloo maqaa Gamoo fi Floor guutaa!")
            
    return render(request, 'admin_base_templates/floor_form.html')


def available_rooms_view(request):
    selected_floor = request.GET.get('floor')
    floors = Floor.objects.all()
    
    # Terminal/Console irratti maal akka fuudhu ilaaluuf (Debugging)
    print("Selected Floor ID from URL:", selected_floor)

    rooms = Room.objects.select_related('floor').all()

    if selected_floor:
        try:
            floor_id_int = int(selected_floor)
            rooms = rooms.filter(floor_id=floor_id_int)
        except ValueError:
            rooms = Room.objects.none() # Yoo ID-n dogoggora ta'e kutaa hin fidu

    context = {
        'floors': floors,
        'rooms': rooms,
        'selected_floor': selected_floor
    }
    return render(request, 'public_templates/rooms_list.html', context)

def signup_view(request):
    if request.method == 'POST':
        # Code sign up (user registration) asitti barraa'a
        pass
    return render(request, 'public_templates/signup.html') 


# --- ADMIN ROOM MANAGEMENT VIEWS ---

@staff_member_required
def admin_rooms_view(request):
    rooms = Room.objects.select_related('floor').all()
    return render(request, 'admin_base_templates/admin_rooms.html', {'rooms': rooms})

@staff_member_required
def admin_edit_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    floors = Floor.objects.all()

    if request.method == 'POST':
        room.name = request.POST.get('name')
        room.room_type = request.POST.get('room_type')
        floor_id = request.POST.get('floor')
        if floor_id:
            room.floor = get_object_or_404(Floor, id=floor_id)
        room.price_per_night = request.POST.get('price_per_night')
        room.status = request.POST.get('status')

        if 'image' in request.FILES:
            room.image = request.FILES['image']

        room.save()
        messages.success(request, f"Kutaan '{room.name}' milkaa'inaan haaromeera!")
        return redirect('admin_rooms')

    return render(request, 'admin_base_templates/admin_edit_room.html', {'room': room, 'floors': floors})

@staff_member_required
def admin_toggle_room_status_view(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)
        new_status = request.POST.get('status')
        if new_status in ['available', 'booked', 'maintenance']:
            room.status = new_status
            room.save()
            messages.success(request, f"Status kutaa '{room.name}' gara '{new_status}'tti jijjiirameera.")
    return redirect('admin_rooms')

@staff_member_required
def admin_delete_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        # room.name bakka jedhu room.room_number ykn str(room) godhi
        room_identifier = getattr(room, 'room_number', str(room))
        room.delete()
        messages.success(request, f"Room {room_identifier} has been deleted successfully!")
        return redirect('admin_rooms')
    
    #return render(request, 'admin_base_templates/admin_confirm_delete.html', {'room': room})


# Admin Management Views for Messages & Feedback
@staff_member_required
def admin_messages_view(request):
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    feedbacks_list = Feedback.objects.all().order_by('-created_at')
    return render(request, 'admin_base_templates/admin_inquiries.html', {
        'messages_list': messages_list,
        'feedbacks_list': feedbacks_list
    })

@staff_member_required
def admin_toggle_feedback(request, fb_id):
    fb = get_object_or_404(Feedback, id=fb_id)
    fb.is_approved = not fb.is_approved
    fb.save()
    return redirect('admin_messages')

from .models import AboutContent

@staff_member_required
def admin_edit_about_view(request):
    # AboutContent object tokko qofa qabanna (Singleton akkasitti hojjeta)
    about, created = AboutContent.objects.get_or_create(
        defaults={
            'title': 'About Us',
            'description': 'Boraati Guest House – Where cleanliness, tranquility, and reliable service come together.',
            'mission': 'To provide exceptional hospitality, comfortable rooms, and reliable service to all guests.',
            'phone': '+251...',
            'location': 'Bule Hora, Guji, Ethiopia'
        }
    )

    if request.method == 'POST':
        about.title = request.POST.get('title')
        about.description = request.POST.get('description')
        about.mission = request.POST.get('mission')
        about.phone = request.POST.get('phone')
        about.location = request.POST.get('location')
        about.save()
        
        messages.success(request, "Odeeffannoon 'About Us' milkaa'inaan haaromfameera!")
        return redirect('admin_edit_about')

    return render(request, 'admin_base_templates/admin_edit_about.html', {'about': about})

@staff_member_required
def admin_add_room_by_link_view(request):
    floors = Floor.objects.all()
    
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        price_per_night = request.POST.get('price_per_night')
        floor_id = request.POST.get('floor')
        image_url = request.POST.get('image_url')
        description = request.POST.get('description', '')

        floor = get_object_or_404(Floor, id=floor_id) if floor_id else None

        # Kutaa haaraa galchuu (Status kallaattiin Available ta'a)
        Room.objects.create(
            room_number=room_number,
            room_type=room_type,
            price_per_night=price_per_night,
            floor=floor,
            image_url=image_url,
            description=description,
            status='available'  # Battalumatti Available akka ta'uuf
        )
        messages.success(request, f"Kutaan {room_number} linkii suuraa waliin milkaa'inaan galmeeffameera!")
        return redirect('admin_rooms')

    return render(request, 'admin_base_templates/admin_add_room_by_link.html', {'floors': floors})