from django.shortcuts import render
from opinions.models import Opinion
from django.http import HttpResponseRedirect

def index(request):
    template = 'opinions.html'
    opinions = Opinion.objects.all().order_by('-published')

    for opinion in opinions:
        opinion.get_counts_and_update_date()

    context = {
        'opinions': opinions,
    }

    return render(request, template, context)

def justice_opinions(request, justice_id):
    template = 'opinions.html'
    opinions = Opinion.objects.filter(justice_id=justice_id)

    if not opinions:
        return redirect(request)

    for opinion in opinions:
        opinion.get_counts_and_update_date()

    context = {
        'opinions': opinions,
    }

    return render(request, template, context)

def redirect(request, *args):
    return HttpResponseRedirect('/opinions/')
