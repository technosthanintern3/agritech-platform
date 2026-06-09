from django.shortcuts import render, redirect
from .forms import ServiceRequestForm
from .models import ServiceRequest
from agritech.utils import login_required_session


@login_required_session
def services(request):

    if request.method == 'POST':

        form = ServiceRequestForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            service = form.save(
                commit=False
            )

            farmer_id = request.session.get(
                'farmer_id'
            )

            if farmer_id:
                service.farmer_id = farmer_id

            service.save()

            return render(
                request,
                'services/services.html',
                {
                    'form': ServiceRequestForm(),
                    'success': True
                }
            )

    else:

        form = ServiceRequestForm()

    return render(
        request,
        'services/services.html',
        {
            'form': form
        }
    )


@login_required_session
def my_requests(request):

    farmer_id = request.session.get(
        'farmer_id'
    )

    requests = ServiceRequest.objects.filter(
        farmer_id=farmer_id
    ).order_by('-created_at')

    return render(
        request,
        'services/my_requests.html',
        {
            'requests': requests
        }
    )


def service_info(request, service_name):

    services_data = {

        'crop-advisory': {
            'title': 'Crop Advisory',
            'description': '''
            Get expert guidance on crop selection,
            cultivation practices, pest management,
            fertilizer usage and disease prevention
            to maximize crop productivity.
            ''',
            'benefits': [
                'Improved crop yield',
                'Better crop planning',
                'Reduced pest and disease losses',
                'Expert farming guidance'
            ],
            'why_choose': '''
            Our agricultural experts provide personalized
            recommendations based on your crop type,
            soil condition, climate and farming practices
            to help you achieve better harvests.
            '''
        },

        'soil-testing': {
            'title': 'Soil Testing',
            'description': '''
            Analyze soil nutrients, pH levels and fertility
            status to determine the best cultivation and
            fertilizer strategy for your farm.
            ''',
            'benefits': [
                'Know soil nutrient levels',
                'Reduce fertilizer costs',
                'Improve soil fertility',
                'Increase crop productivity'
            ],
            'why_choose': '''
            Accurate soil testing helps farmers understand
            nutrient deficiencies and optimize fertilizer
            application for healthier crops and higher yields.
            '''
        },

        'disease-identification': {
            'title': 'Disease Identification',
            'description': '''
            Identify crop diseases at an early stage and
            receive recommendations for effective treatment
            and prevention strategies.
            ''',
            'benefits': [
                'Early disease detection',
                'Reduce crop damage',
                'Proper treatment recommendations',
                'Protect farm productivity'
            ],
            'why_choose': '''
            Early diagnosis of plant diseases can prevent
            major crop losses and save both time and money
            through timely corrective actions.
            '''
        },

        'plant-doctor': {
            'title': 'Plant Doctor',
            'description': '''
            Consult experienced agricultural specialists
            regarding crop health issues, nutrient
            deficiencies and plant growth problems.
            ''',
            'benefits': [
                'Direct expert consultation',
                'Solutions for crop health issues',
                'Nutrient deficiency diagnosis',
                'Improved crop quality'
            ],
            'why_choose': '''
            Our plant health specialists provide practical
            and reliable recommendations to ensure healthy
            crop growth throughout the season.
            '''
        },

        'farmer-consultation': {
            'title': 'Farmer Consultation',
            'description': '''
            One-to-one consultation with agriculture experts
            for crop planning, modern farming techniques,
            irrigation management and productivity improvement.
            ''',
            'benefits': [
                'Personalized farming advice',
                'Modern farming techniques',
                'Better decision making',
                'Higher farm profitability'
            ],
            'why_choose': '''
            Receive tailored guidance from agricultural
            professionals who understand local farming
            challenges and opportunities.
            '''
        },

        'weather-information': {
            'title': 'Weather Information',
            'description': '''
            Access timely weather forecasts and climate
            information to plan farming activities more
            efficiently and reduce weather-related risks.
            ''',
            'benefits': [
                'Plan irrigation effectively',
                'Avoid weather-related losses',
                'Better harvesting decisions',
                'Improved farm management'
            ],
            'why_choose': '''
            Accurate weather information helps farmers
            make informed decisions regarding sowing,
            irrigation, spraying and harvesting.
            '''
        },

        'market-price': {
            'title': 'Market Price Information',
            'description': '''
            Stay updated with the latest crop market prices,
            demand trends and trading opportunities to
            maximize agricultural profits.
            ''',
            'benefits': [
                'Sell crops at better prices',
                'Track market demand',
                'Maximize profits',
                'Make informed selling decisions'
            ],
            'why_choose': '''
            Real-time market information enables farmers
            to choose the right time and place to sell
            their produce for maximum returns.
            '''
        }

    }

    service = services_data.get(service_name)

    return render(
        request,
        'services/service_info.html',
        {
            'service': service
        }
    )