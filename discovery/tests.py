# -*- coding: utf-8 -*-

from django.test import TestCase
from scotuswebcites import settings
from discovery.Pdf import Pdf
from discovery.Pdf import Url


class PdfTestCase(TestCase):
    def test_urls_as_expected(self):
        """Expected urls are scraped"""
        test_dir = settings.BASE_DIR + '/discovery/test_pdfs/'
        checks = {
            'United_States_v._Alvarez.pdf': [
                u'http://www.cmohs.org/recipient-archive.php',
                u'http://articles.philly.com/2004-02-11/news/25374213_1_medals-military-imposters-distinguished-flying-cross',
                u'http://www.chicagotribune.com/news/local/chi-valor-oct25,0,4301227.story?page=1',
                u'http://articles.chicagotribune.com/1994-10-21/news/9410210318_1_congressional-medal-highest-fritz',
                u'http://www.nytimes.com/2002/04/29/business/at-fox-news-the-colonel-who-wasn-t.html?pagewanted=all&src=pm',
                u'http://www.nydailynews.com/news/crime/war-crime-fbi-targets-fake-heroes-article-1.249168',
                u'http://www.justice.gov/usao/waw/press/2007/sep/operationstolenvalor.html',
                u'http://triblive.com/usworld/nation/1034434-85/court-military-law-false-medals-supreme-valor-act-federal-free',
                u'http://www.history.army.mil/html/moh/mohstats.html',
            ],
            'Hemi_Group_LLC_v_City_of_New_York.pdf': [
                u'http://www.justice.gov/usao/eousa/foia_reading_room/usam/title6/4mtax.htm',
            ],
            'Michigan_v_Bay_Mills_Indian_Community.pdf': [
                u'http://govinfo.library.unt.edu/ngisc/reports/6.pdf',
                u'http://www.census.gov/newsroom/releases/archives/income_wealth/cb13-165.html',
                u'http://www.nigc.gov/LinkClick.aspx?fileticket=Fhd5shyZ1fM%3D',
                u'http://www.sanmanuel-nsn.gov/fourfires.php.html',
            ],
            'NLRB_v_Noel_Canning.pdf': [
                u'http://www.nlrb.gov/who-we-are/board/members-nlrb-1935',
                u'http://georgewbush­whitehouse.archives.gov/news/releases/2001/08/20010831-14.html',
                u'http://www.dmnews.com/prc-chairman-gleiman-retires/article/70877',
                u'http://www.dnfsb.gov/about/board-members/joseph-j-dinunno',
                u'http://www.ssab.gov/AbouttheBoard/Members.aspx',
                u'http://mynlrb.nlrb.gov/link/document.aspx/09031d45800d5d75',
                u'http://www.unhcr.org/news/NEWS/3fda0f584.html',
                u'http://2001-2009.state.gov/outofdate/bios/d/7988.htm',
                u'http://www.nlrb.gov/who-we-are/general-counsel/general-counsels-1935',
                u'http://history.state.gov/departmenthistory/people/glazer-charles-l',
                u'http://papers.ssrn.com/sol3/papers.cfm?abstract_id=2374563',
                u'http://founders.archives.gov/documents/Washington/99-01-02-00702',
                u'http://wardepartmentpapers.org/document.php?id=31766.10',			# See note below
                u'http://memory.loc.gov/ammem/collections/madison_papers',
                u'http://www.justice.gov/olc/opiniondocs/section7054.pdf',
            ],
        }

        # This is actually a bad citation, the '.10' is a period + footnote tag.
        # But, we can't safely assume that all url stirngs ending in '.#' are bad

        for document, citations in checks.iteritems():
            pdf = Pdf()
            pdf.local_file = test_dir + document
            pdf.scrape_urls()
            if self.assertEqual(pdf.urls, citations):
                print


class UrlTestCase(TestCase):
    def test_request(self):
        """Expected request returns"""
        checks = {'http://www.google.com': 200,
                  'www.google.com': 200,
                  'http://kjhkjhkjhkjhkjhkjhkjhkjhkjhkjh.com': False,
        }

        for url, response in checks.iteritems():
            if response:
                request = Url.get(url)
                self.assertEqual(request.status_code, response)
            else:
                self.assertEqual(Url.get(url, False), response)
