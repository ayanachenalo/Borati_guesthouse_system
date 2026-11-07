import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Building Admin'),
        ('user', 'Guest / User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    provider_name = models.CharField(max_length=50, blank=True, null=True)
    provider_user_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    # Ragaalee bu'uuraa User
    full_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True, help_text="FAN Number / National ID")
    profile_pic_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    
#class gabate gurguddoo
# 1. Gabatee Gamoo (Building Model)
class Building(models.Model):
    building_name = models.CharField(max_length=150, default="Boraati Guest House")
    total_floors = models.IntegerField(help_text="Lakkoofsa gullantaa fkn: Ground, Ground+1...")
    location = models.CharField(max_length=255, default="Bule Hora")

    def __str__(self):
        return self.building_name


# 2. Gabatee Sadarkaa Gamoo (Floor Model / Categories)
class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    floor_name = models.CharField(max_length=50, help_text="fkn: Ground Floor, Ground + 1, Ground + 2")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.building.building_name} - {self.floor_name}"


# 3. Gabatee Kutaawwan Siree (Room Model / Subcategories)
class Room(models.Model):
    ROOM_TYPES = (
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('vip', 'VIP / Master Suite'),
    )

    ROOM_STATUS = (
        ('available', 'Available'),
        ('booked', 'Booked (Qabatame)'),
        ('maintenance', 'Maintenance '),
    )

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20, unique=True, help_text="fkn: Room 101, Room 102")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='single')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, help_text="Gatii guyyaa tokkoo")
    
    # Suuraa fi ibsa
    main_image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    description = models.TextField(help_text="Ibsa bal'aa fkn: Wi-Fi, Bishaan ho'aa, TV...")
    
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Linkii suuraa (fkn: https://example.com/room.jpg)")

    # Method / Property: Yoo linkiin jiraate linkii sana, yoo faayiliin uumamaa jiraate URL faayilichaa agarsiisuuf
    @property
    def get_image_display(self):
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        return '/static/images/default_room.jpg'
    
    # Haala kutaa (Status)
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='available')

    def __str__(self):
        return f"{self.room_number} ({self.room_type}) - {self.status}"
    
  # 2. Booking Model (Ragaa Nagahee fi National ID Qabatu)
class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending '),
        ('confirmed', 'Confirmed '),
        ('checked_in', 'Checked-in '),
        ('checked_out', 'Checked-out '),
        ('cancelled', 'Cancelled '),
    )

    # Receipt Code Addaa Ta'e (fkn: BRT-8F92A)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='bookings')
    
    # Odeeffannoo Dabalataa Imaltuu (Receipt irratti kan maxxanfamu)
    guest_full_name = models.CharField(max_length=150, help_text="Maqaa Guutuu Imaltuu")
    guest_phone = models.CharField(max_length=20, help_text="Lakkoofsa Bilbilaa")
    national_id_number = models.CharField(max_length=50, help_text="FAN Number / Fayidaa ID")
    
    # Guyyoota Qabannaa
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    
    # Receipt-ni sun yeroo meeqaffaaf akka itti fayyadaman to'achuuf
    is_receipt_used = models.BooleanField(default=False, help_text="Admin keessummaa seensiseeraa?")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Receipt Number Ofumaa (Automatically) uumuu
        if not self.receipt_number:
            self.receipt_number = f"BRT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt: {self.receipt_number} - {self.guest_full_name}"

# 5. Gabatee Kaffaltii fi Herregaa (Payment Model)
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('telebirr', 'Telebirr'),
        ('cbe_birr', 'CBE Birr'),
        ('cash', 'Cash (Kaashii)'),
    )

    PAYMENT_STATUS = (
        ('pending', 'Pending )'),
        ('verified', 'Verified '),
        ('rejected', 'Rejected'),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='telebirr')
    transaction_ref = models.CharField(max_length=100, unique=True, help_text="Lakkoofsa Ragaa Kaffaltii (Txn ID)")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Admin kaffalticha mirkaneesse
    verified_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_payments',
        help_text="Admin kaffaltii kana mirkaneesse"
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking #{self.booking.id} - {self.payment_status}"


# 6. Gabatee Baasii Gamoo (Expense Model)
class Expense(models.Model):
    title = models.CharField(max_length=200, help_text="fkn: Bill Electric, Mindaa Hojjetaa, Suphaa")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    expense_date = models.DateField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='expenses')

    def __str__(self):
        return f"{self.title} - {self.amount} ETB"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.phone})"

# 2. Guest Feedback & Reviews Table
class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField(max_length=100)
    rating = models.IntegerField(default=5, help_text="1 to 5 stars")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Admin approve godhchuu qaba")

    def __str__(self):
        return f"Feedback by {self.guest_name} - {self.rating} Stars"

# 3. About Us / Site Info Content Table (Optional dynamic content)
class AboutContent(models.Model):
    title = models.CharField(max_length=200, default="Waa'ee Boraati Guest House")
    description = models.TextField(help_text="Tajaajilaa fi seenaa gabaabaa guest house")
    mission = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, default="+251...")
    location = models.CharField(max_length=200, default="Bule Hora, Guji, Ethiopia")

    def __str__(self):
        return self.title