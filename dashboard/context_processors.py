from orders.models import Order
from services.models import ServiceRequest
from consultation.models import ConsultationRequest
from farmer_support.models import CropProblem


def admin_notifications(request):

    return {

        "pending_orders":
        Order.objects.filter(
            status="Pending"
        ).count(),

        "pending_services":
        ServiceRequest.objects.count(),

        "consultations":
        ConsultationRequest.objects.count(),

        "crop_problems":
        CropProblem.objects.count(),

    }