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


def session_role_required(*allowed_roles):

    def decorator(view_func):

        def wrapper(request, *args, **kwargs):

            user_role = request.session.get('user_role')

            if user_role not in allowed_roles:

                messages.warning(
                    request,
                    'Access denied.'
                )

                return redirect('home')

            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator


doctor_required = session_role_required('doctor')
consultant_required = session_role_required('consultant')
farmer_required = session_role_required('farmer')