from django.http import HttpResponse


def index(request):
    return HttpResponse("Herzlich Wilkommen im PeP et al. Event System")
