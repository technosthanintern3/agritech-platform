from django.shortcuts import render
from .forms import CropProblemForm
from django.shortcuts import redirect
from .models import CropProblem
from agritech.utils import login_required_session


def farmer_support(request):

    if request.method == 'POST':

        form = CropProblemForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            problem = form.save(
                commit=False
            )

            farmer_id = request.session.get(
                'farmer_id'
            )

            if farmer_id:

                problem.farmer_id = farmer_id

            problem.save()

            return render(
                request,
                'farmer_support/support.html',
                {
                    'form': CropProblemForm(),
                    'success': True
                }
            )

    else:

        form = CropProblemForm()

    return render(
        request,
        'farmer_support/support.html',
        {
            'form': form
        }
    )
def my_problems(request):

    farmer_id = request.session.get(
        'farmer_id'
    )

    if not farmer_id:

        return redirect('login')

    problems = CropProblem.objects.filter(
        farmer_id=farmer_id
    ).order_by('-created_at')

    return render(
        request,
        'farmer_support/my_problems.html',
        {
            'problems': problems
        }
    )
@login_required_session
def farmer_support(request):

    ...