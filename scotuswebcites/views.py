# -*- coding: utf-8 -*-

import csv
from django.db.models import Count
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone
from citations.models import Citation
from opinions.models import Opinion


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


# A small generator to handle the streaming logic
def csv_generator(queryset, header):
    yield header
    # .iterator() fetches rows in chunks, keeping memory usage low and constant
    for citation in queryset.iterator(chunk_size=1000):
        yield citation.csv_row()


def download_csv(request):
    # 1. Optimize the SQL to pull all related data in ONE join
    # Follow the chain: Citation -> Opinion -> Justice
    queryset = Citation.objects.select_related('opinion', 'opinion__justice').all()

    header = [
        'Scraped Citation', 'Validated Citation', 'Citation Validation Date',
        'Scrape Evaluation', 'Citation Status', 'Memento', 'WebCite',
        'Perma.cc', 'Opinion', 'Justice', 'Category', 'Published',
        'Discovered', 'Opinion PDF Url', 'Reporter', 'Docket', 'Part',
    ]

    # 2. Use StreamingHttpResponse so the VM doesn't have to build the
    # whole file in memory before sending it to the user.
    response = StreamingHttpResponse(
        (csv.writer(Echo()).writerow(row) for row in csv_generator(queryset, header)),
        content_type='text/csv',
    )

    filename = timezone.now().strftime('%Y%m%d')
    response['Content-Disposition'] = f'attachment; filename="scotus-web-citations.{filename}.csv"'

    return response


def overview(request):
    context = {}
    template = 'overview.html'
    return render(request, template, context)


def data(request):
    template = 'data.html'
    js_month = 2678400000

    # 1. Batch status counts (3 fast queries)
    status_counts = dict(Citation.objects.values_list('status').annotate(total=Count('id')))

    # 2. Get distributions using SQL grouping (1 fast query)
    # This groups by date and counts opinions and citations in one go
    stats = Opinion.objects.values('published').annotate(
        ops=Count('id', distinct=True),
        cites=Count('citation', distinct=True)
    ).order_by('published')

    opinion_data = []
    citation_data = []

    for entry in stats:
        # Convert date to JS timestamp (ms)
        js_date = int(entry['published'].strftime('%s')) * 1000
        opinion_data.append([js_date, entry['ops']])
        citation_data.append([js_date, entry['cites']])

    # Boundaries
    if opinion_data:
        earliest = opinion_data[0][0]
        latest = opinion_data[-1][0]
    else:
        earliest = 1262304000000
        latest = 1462086000000  # Your go_live_date example

    context = {
        'available': status_counts.get('a', 0),
        'unavailable': status_counts.get('u', 0),
        'redirected': status_counts.get('r', 0),
        'citation_distribution': citation_data,
        'opinion_distribution': opinion_data,
        'earliest': earliest - js_month,
        'latest': latest + js_month,
        'go_live_date': 1462086000000,
    }

    return render(request, template, context)


# Helper class for StreamingHttpResponse + CSV writer
class Echo:
    def write(self, value):
        return value