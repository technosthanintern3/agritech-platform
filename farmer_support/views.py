from django.shortcuts import render, redirect, get_object_or_404
from .forms import CropProblemForm
from .models import CropProblem, CropProblemGuide
from agritech.utils import login_required_session


@login_required_session
def farmer_support(request):

    problem_guides = CropProblemGuide.objects.filter(
        is_active=True
    ).order_by('display_order', 'title')

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
                    'success': True,
                    'problem_guides': problem_guides
                }
            )

    else:

        form = CropProblemForm()

    return render(
        request,
        'farmer_support/support.html',
        {
            'form': form,
            'problem_guides': problem_guides
        }
    )


@login_required_session
def crop_problem_detail(request, slug):

    guide = get_object_or_404(
        CropProblemGuide,
        slug=slug,
        is_active=True
    )

    related_guides = CropProblemGuide.objects.filter(
        is_active=True
    ).exclude(
        id=guide.id
    ).order_by('display_order', 'title')[:3]

    return render(
        request,
        'farmer_support/problem_detail.html',
        {
            'guide': guide,
            'related_guides': related_guides,
        }
    )


@login_required_session
def my_problems(request):

    farmer_id = request.session.get(
        'farmer_id'
    )

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
