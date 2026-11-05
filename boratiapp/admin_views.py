from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Building, Room, Floor, Booking, Payment, Expense, CustomUser

# Custom Decorator: Admin qofa akka seensisuuf
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Akkasumas eeyyama admin hin qabdu!")
        return redirect('user_index')
    return wrapper


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
    bookings = []
    
    if query:
        # Receipt Code, National ID, ykn Phone-iin search gochuu
        bookings = Booking.objects.filter(
            models.Q(receipt_number__iexact=query) | 
            models.Q(national_id_number__iexact=query) |
            models.Q(guest_phone__icontains=query)
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
        messages.error(request, "Reesitiin kun kanaan dura itti fayyadameera (Already Checked-in)!")
    else:
        booking.booking_status = 'checked_in'
        booking.is_receipt_used = True
        booking.save()
        
        # Room Status 'booked' tti jijjiiruu
        room = booking.room
        room.status = 'booked'
        room.save()
        
        messages.success(request, f"Imaltuun {booking.guest_full_name} milkaa'inaan keessummeeffameera!")
        
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