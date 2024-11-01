from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages

from scotuswebcites import settings
from citations.models import Citation
from archive.Perma import Perma
from .forms import VerifyCitationForm


def index(request):
    template = 'citations.html'

    ## On October 28 2024, SCOTUS touched hundreds of old opinions, triggering thousdands of "new" citation
    ## ingests.  I no longer have time to maintain this strictly. It's hihgly unlikely they were changing
    ## citation data. As such, the best bet for now is to simply hide these citations, because I can't verify
    ## them all.  If this happens again, we should add a new "ignore" field to opinions, and batch ignore
    ## citations for flagged opinions. Yes, this is brute force and inelligant, but I simply don't have the time.

    ## Show all citations
    # citations = Citation.objects.all().order_by('-opinion__id')

    ## Show only citations from opinions discovered on problem date
    # citations = Citation.objects.filter(opinion_id__discovered__range=["2024-10-28", "2024-10-29"]).order_by('-opinion__id')

    ## Show all citations EXCEPT those published on problem date when thousand of old files were touched
    citations = Citation.objects.filter(~Q(opinion_id__discovered__range=["2024-10-28", "2024-10-29"])).order_by('-opinion__id')

    context = {
        'citations': citations,
        'statuses': dict(Citation.STATUSES),
    }

    return render(request, template, context)


def justice_opinions_citations(request, justice_id):
    template = 'citations.html'

    # Check if filtering by link status instead of justice_id 
    if justice_id in [status for code, status in Citation.STATUSES]:
        return get_citations_by_status(request, justice_id)

    else:
        citations = Citation.objects.filter(opinion_id__justice_id=justice_id).order_by('-opinion__id')

        if not citations:
            return redirect(request)

        context = {
            'citations': citations,
            'statuses': dict(Citation.STATUSES),
        }

        return render(request, template, context)


def opinion_citations(request, opinion_id):
    template = 'citations.html'
    citations = Citation.objects.filter(opinion_id=opinion_id)

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
            # Successful update
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

                # Create success flash message
                messages.add_message(request, messages.SUCCESS, 'Successfully verified citation!')

                return HttpResponseRedirect('/citations/#%s' % citation.id)

            # Submitted invalidated url
            context = {
                'citation': citation,
                'form': form,
            }

        except Exception:
            if settings.DEBUG:
                import traceback
                raise Exception(traceback.format_exc())

            context = {
                'error': 'No citation with id %s' % request.POST['citation_id'],
            } 

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
    citations = Citation.objects.filter(status=status[0]).order_by('-opinion__id')
    context = {
        'citations':citations,
        'statuses': dict(Citation.STATUSES),
    }

    return render(request, template, context)


def redirect(request, *args):
    return HttpResponseRedirect('/citations/')
