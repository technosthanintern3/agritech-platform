from django.shortcuts import render, redirect
from .forms import ConsultationForm
from .models import ConsultationRequest
from agritech.utils import login_required_session


@login_required_session
def consultation(request):

    if request.method == 'POST':

        form = ConsultationForm(request.POST)

        if form.is_valid():

            consultation = form.save(commit=False)

            farmer_id = request.session.get('farmer_id')

            if farmer_id:
                consultation.farmer_id = farmer_id

            consultation.save()

            return render(
                request,
                'consultation/consultation.html',
                {
                    'form': ConsultationForm(),
                    'success': True
                }
            )

        else:
            print(form.errors)

    else:
        form = ConsultationForm()

    return render(
        request,
        'consultation/consultation.html',
        {
            'form': form
        }
    )


@login_required_session
def my_consultations(request):

    farmer_id = request.session.get('farmer_id')

    consultations = ConsultationRequest.objects.filter(
        farmer_id=farmer_id
    ).order_by('-created_at')

    return render(
        request,
        'consultation/my_consultations.html',
        {
            'consultations': consultations
        }
    )