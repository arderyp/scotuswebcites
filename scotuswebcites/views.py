# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

def download_csv(request):
    from citations.models import Citation
    from django.http import HttpResponse
    from datetime import datetime
    import csv

    fields_header = [
        'Scraped Citation',
        'Validated Citation',
        'Citation Validation Date',
        'Scrape Evaluation',
        'Citation Status',
        'Memento',
        'WebCite',
        'Perma.cc',
        'Opinion',
        'Justice',
        'Category',
        'Published',
        'Discovered',
        'Opinion PDF Url',
        'Reporter',
        'Docket',
        'Part',
    ]

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scotus-web-citations.%s.csv' % datetime.now().strftime('%Y%m%d')

    writer = csv.writer(response, delimiter=',')
    writer.writerow(fields_header)

    for citation in Citation.objects.all():
        writer.writerow(citation.csv_row())

    return response


def overview(request):
    context = {}
    template = 'overview.html'
    return render(request, template, context)

def data(request):
    from time import time
    from opinions.models import Opinion
    from citations.models import Citation
    from django.http import HttpRequest

    template = 'data.html'
    js_month = 2678400000
    context = {
        'base': HttpRequest.build_absolute_uri(request).strip('data/'),
        'go_live_date': 1462086000000,
        'available': Citation.objects.filter(status='a').count(),
        'unavailable': Citation.objects.filter(status='u').count(),
        'redirected': Citation.objects.filter(status='r').count(),
    }

    # Calculate opinion and citation distributions
    distributions = {}
    for opinion in Opinion.objects.all():
        citations = len(opinion.citation_set.all())
        unix_date = int(opinion.published.strftime('%s'))
        js_date = unix_date * 1000
        if js_date in distributions:
            distributions[js_date]['opinions'] += 1
            distributions[js_date]['citations'] += citations
        else:
            distributions[js_date] = {'opinions': 1, 'citations': citations}

    opinion_data = [[date, data['opinions']] for date, data in distributions.iteritems()]
    citation_data = [[date, data['citations']] for date, data in distributions.iteritems()]

    # Sort data chronologically
    opinion_data = sorted(opinion_data, key=lambda x: x[0])
    citation_data = sorted(citation_data, key=lambda x: x[0])

    if opinion_data:
        earliest = opinion_data[0][0] - js_month
        latest = opinion_data[-1][0] + js_month
    else:
        # No scraping has been done yet, set dates manually, charts will be blank
        earliest = 1262304000
        latest = time()

    context['citation_distribution'] = citation_data
    context['opinion_distribution'] = opinion_data
    context['earliest'] = earliest - js_month
    context['latest'] = latest + js_month

    return render(request, template, context)