from django.contrib.auth.decorators import user_passes_test

management_only = user_passes_test(lambda u: u.is_authenticated and u.has_management_permission)
