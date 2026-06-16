from django.shortcuts import (
    render,
    get_object_or_404
)

from .forms import TractorBookingForm

from .models import (
    TractorBooking,
    Machinery
)

from agritech.utils import login_required_session


@login_required_session
def tractor_booking(request):

    machines = Machinery.objects.all()

    if request.method == 'POST':

        form = TractorBookingForm(request.POST)

        if form.is_valid():

            booking = form.save(commit=False)

            farmer_id = request.session.get('farmer_id')

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


@login_required_session
def my_bookings(request):

    farmer_id = request.session.get('farmer_id')

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


def machinery_detail(request, id):

    machine = get_object_or_404(
        Machinery,
        id=id
    )

    return render(
        request,
        'machinery/machinery_detail.html',
        {
            'machine': machine
        }
    )