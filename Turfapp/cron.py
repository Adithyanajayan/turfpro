from .models import Booking

def update_booking_status():
    bookings = Booking.objects.all()
    for booking in bookings:
        booking.update_status()
