from django.contrib import messages
from django.shortcuts import redirect


def login_required_session(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.session.get('farmer_id'):

            messages.warning(
                request,
                "Please login or register first to use this feature."
            )

            return redirect('login')

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper