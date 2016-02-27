# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

def logout(request):
    response = auth_logout(request)
    return HttpResponseRedirect('/')

def download_csv(request):
    from citations.models import Citation
    from scotus import settings
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
        'PDF Url',
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
    from opinions.models import Opinion
    from citations.models import Citation
    from django.db.models import Count
    from datetime import timedelta
    from django.http import HttpRequest

    template = 'overview.html'
    js_month = 2678400000
    context = {
        'base': HttpRequest.build_absolute_uri(request),
        'nyt_publication': 1379995200000,
        'available': Citation.objects.filter(status='a').count(),
        'unavailable': Citation.objects.filter(status='u').count(),
        'redirected': Citation.objects.filter(status='r').count(),
        'cite_nyt': 'http://www.nytimes.com/2013/09/24/us/politics/in-supreme-court-opinions-clicks-that-lead-nowhere.html?_r=0',
        'cite_wiki': 'https://en.wikipedia.org/wiki/Link_rot',
        'cite_harvard': 'https://blogs.law.harvard.edu/futureoftheinternet/2013/09/22/perma/',
        'cite_aba': 'http://www.abajournal.com/magazine/article/link_rot_is_degrading_legal_research_and_case_cites/',
        'cite_perma': 'http://perma.cc',
        'cite_heritrix': 'https://en.wikipedia.org/wiki/Heritrix',
        'cite_scotus': 'http://www.supremecourt.gov/opinions/opinions.aspx',
        'cite_github': 'https://github.com/pardery/scotus',
    }

    # Get citation distribution data
    context['citation_distribution'] = []
    for opinion in Opinion.objects.values('published').annotate(citation_count=Count('citation')):
        unix_date = int(opinion['published'].strftime('%s'))
        js_date = unix_date * 1000
        context['citation_distribution'].append([js_date, opinion['citation_count']])

    sorted_data = sorted(context['citation_distribution'], key=lambda x: x[0])
    context['earliest'] = sorted_data[0][0] - js_month
    context['latest'] = sorted_data[-1][0] + js_month

    return render(request, template, context)
