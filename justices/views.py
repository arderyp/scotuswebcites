import operator
from django.db.models import Count, ExpressionWrapper, FloatField
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect
from django.shortcuts import render
from justices.models import Justice


def index(request):
    template = 'justices.html'
    justices = (Justice.objects
                .annotate(
                    opinion_count=Count('opinion', distinct=True),
                    citation_count=Count('opinion__citation', distinct=True)
                )
                .annotate(
                    citation_average_count=ExpressionWrapper(Cast('citation_count', FloatField()) / Cast('opinion_count', FloatField()),
                    output_field=FloatField()
                ))
                .order_by('-citation_average_count'))

    context = {
        'justices': justices,
    }

    return render(request, template, context)


def redirect(request, *args):
    return HttpResponseRedirect('/justices/')    
