from django.shortcuts import render, redirect
from .forms import TractorBookingForm
from .models import TractorBooking, Machinery
from agritech.utils import login_required_session


def tractor_booking(request):

    machines = Machinery.objects.all()

    if request.method == 'POST':

        form = TractorBookingForm(request.POST)

        if form.is_valid():

            booking = form.save(
                commit=False
            )

            farmer_id = request.session.get(
                'farmer_id'
            )

            if farmer_id:

                booking.farmer_id = farmer_id

            booking.save()

            return render(
                request,
                'machinery/tractor_booking.html',
                {
                    'form': TractorBookingForm(),
                    'machines': machines,
                    'success': True
                }
            )

    else:

        form = TractorBookingForm()

    return render(
        request,
        'machinery/tractor_booking.html',
        {
            'form': form,
            'machines': machines
        }
    )


def my_bookings(request):

    farmer_id = request.session.get(
        'farmer_id'
    )

    if not farmer_id:

        return redirect('login')

    bookings = TractorBooking.objects.filter(
        farmer_id=farmer_id
    ).order_by('-id')

    return render(
        request,
        'machinery/my_bookings.html',
        {
            'bookings': bookings
        }
    )
@login_required_session
def tractor_booking(request):

    ...