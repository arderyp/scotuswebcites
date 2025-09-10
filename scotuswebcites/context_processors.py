from scotuswebcites import settings

def global_variables(request):
    return {
        'SITE_IMPROVE_SCRIPT_URL': settings.SITE_IMPROVE_SCRIPT_URL,
        'VERSION': '4.1.4'
    }
