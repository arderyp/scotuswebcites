import operator
from django.shortcuts import render
from justices.models import Justice
from django.http import HttpResponseRedirect

def index(request):
    template = 'justices.html'
    justices = Justice.objects.all()

    # Initialize count figres
    for justice in justices:
        justice.set_counts()

    # Sort by average count
    justices = sorted(
        justices,
        key=operator.attrgetter('citation_average_count'),
        reverse=True
    )
 
    context = {
        'justices': justices,
    }

    return render(request, template, context)

def redirect(request, *args):
    return HttpResponseRedirect('/justices/')    
