from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from opinions.models import Opinion

def index(request):
    template = 'opinions.html'
    context = {
        'opinions': _get_opinions_with_citations(),
    }
    return render(request, template, context)


def justice_opinions(request, justice_id):
    template = 'opinions.html'
    opinions = _get_opinions_with_citations().filter(justice_id=justice_id)
    if not opinions:
        return redirect(request)
    context = {
        'opinions': opinions,
    }
    return render(request, template, context)


def redirect(request, *args):
    return HttpResponseRedirect('/opinions/')


def _get_opinions_with_citations():
    return (Opinion.objects.select_related('justice')
                .annotate(citation_count=Count('citation'))
                .order_by('-published', 'name', '-discovered', 'justice__name'))
