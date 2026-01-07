from .forms import VerifyCitationForm
from archive.Perma import Perma
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.utils import timezone
from citations.models import Citation
from scotuswebcites import settings


def index(request):
    template = 'citations.html'
    context = {
        'citations': _get_citations_with_opinions(),
        'statuses': dict(Citation.STATUSES),
    }
    return render(request, template, context)


def justice_opinions_citations(request, justice_id):
    template = 'citations.html'
    if justice_id in [status for code, status in Citation.STATUSES]:
        # Check if filtering by link status instead of justice_id
        return get_citations_by_status(request, justice_id)
    else:
        citations = _get_citations_with_opinions().filter(opinion_id__justice_id=justice_id)
        if not citations:
            return redirect(request)
        context = {
            'citations': citations,
            'statuses': dict(Citation.STATUSES),
        }
        return render(request, template, context)


def opinion_citations(request, opinion_id):
    template = 'citations.html'
    citations = _get_citations_with_opinions().filter(opinion_id=opinion_id)
    if not citations:
        return redirect(request)
    context = {
        'citations':citations,
        'statuses': dict(Citation.STATUSES),
    }
    return render(request, template, context)


@login_required()
def verify(request, citation_id):
    template = 'verify.html'

    if request.method == 'POST':
        try:
            citation = Citation.objects.get(id=request.POST['citation_id'])
            scrape_evaluation = request.POST['scrape_evaluation']
            validated = request.POST['validated']

            form = VerifyCitationForm({
                'validated': validated,
                'scrape_evaluation': scrape_evaluation,
            })

            if form.is_valid():
                citation.validated = validated
                citation.verify_date = timezone.now()
                citation.scrape_evaluation = scrape_evaluation
                citation.get_statuses()

                # Archive the citation if archiving enabled
                if citation.status != 'u':
                    if settings.PERMA['enabled']:
                        archiver = Perma()
                        archiver.archive_citation(citation)
                        citation.perma = archiver.get_archive_url()

                citation.save()

                # Successful update
                messages.add_message(request, messages.SUCCESS, 'Successfully verified citation!')
                return HttpResponseRedirect('/citations/#%s' % citation.id)

            messages.add_message(request, messages.ERROR, 'Your form submission was invalid')

        except Exception as exception:
            messages.add_message(request, messages.ERROR, str(exception))

            # if settings.DEBUG:
            #     import traceback
            #     raise Exception(traceback.format_exc())

    else:
        try:
            citation = Citation.objects.get(id=citation_id)
        except Exception:
            return redirect(request)

        # Make sure not already validated
        if citation.verify_date:
            messages.add_message(request, messages.WARNING, 'This citation has already been verified')
            return HttpResponseRedirect('/citations/#%s' % citation.id)

        form = VerifyCitationForm(initial={'validated': citation.scraped})

    context = {
        'citation': citation,
        'form': form,
    }

    return render(request, template, context)


def get_citations_by_status(request, status):
    template = 'citations.html'
    context = {
        'citations':_get_citations_with_opinions().filter(status=status[0]).order_by('-opinion__id'),
        'statuses': dict(Citation.STATUSES),
    }
    return render(request, template, context)


def _get_citations_with_opinions():
    return Citation.objects.select_related('opinion').all().order_by('-opinion__id')


def redirect(request, *args):
    return HttpResponseRedirect('/citations/')
