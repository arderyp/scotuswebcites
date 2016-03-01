from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from citations.models import Citation
from django.http import HttpResponseRedirect
from django.utils import timezone
from .forms import VerifyCitationForm


def index(request):
    template = 'citations.html'

    context = {
        'citations': Citation.objects.all().order_by('-opinion__id'),
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

                # Don't waste time checking validated citation if matched scraped
                if validated != citation.scraped or scrape_evaluation != citation.scrape_evaluation: 
                    citation.get_statuses()

                # If citation is non-404, check if ondemand captures are enabled
                if citation.status != 'u':
                    citation.get_ondemand_captures()

                citation.verify_date = timezone.now()
                citation.scrape_evaluation = scrape_evaluation
                citation.save()

                return HttpResponseRedirect('/citations/#%s' % citation.id)

            # Submitted invalidated url
            context = {
                'citation': citation,
                'form': form,
            }

        except Exception:
            # Somehow attempted to validate citation not in DB
            context = {
                'error': 'No citation with id %s' % request.POST['citation_id'],
            } 

    else:
        try:
            citation = Citation.objects.get(id=citation_id)
            form = VerifyCitationForm(
                initial = {
                    'validated': citation.scraped,
                }
            )
            context = {
                'citation': citation,
                'form': form,
            } 
        except Exception:
            return redirect(request)

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
