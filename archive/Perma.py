import json
from requests import post, put

from scotuswebcites import settings
from archive.models import PermaFolder
from opinions.models import Opinion


class Perma(object):
    """Class for interfacing with perma.cc API

    Given a valid citations.models.Citation object, this class
    will allow you to archive the citation and move it to a
    perma.cc folder that shares the same name as the opinion
    from which the citation came. If such a folder does not
    exist, it will be created.
    """

    KEY = settings.PERMA['api_key']
    PARENT_FOLDER = settings.PERMA['shared_folder_id']
    URL_BASE = 'https://perma.cc'
    API_BASE = 'https://api.perma.cc/v1'

    def __init__(self):
        self.response = False
        self.citation = False
        self.archive_id = False
        self.folder_id = False

    def archive_citation(self, citation):
        """Create perma.cc archive and move it to citation's opinion folder"""

        endpoint = '%s/archives/?api_key=%s' % (self.API_BASE, self.KEY)
        self.citation = citation
        self._set_opinion_folder_id()
        response = post(
            endpoint,
            data=json.dumps(self._get_post_data_archive()),
            headers=self._get_headers_dict(),
        )
        response_dict = json.loads(response.text)

        if 'guid' in response_dict:
            self.archive_id = response_dict['guid']
        else:
            # The perma.cc archive could not be created.  This could be due to an API limit.
            error = str(response_dict)
            raise Exception('The perma.cc archive could not be created.  Please review the '
                            'following error and contact perma.cc if it appears to be related to an '
                            'API limit.  Otherwise, open a ticket on the scotuswebcites github repo '
                            'and paste this full error in the ticket:\n\n%s' % error)

    def get_archive_url(self):
        """Return perma.cc archive resource url"""

        if self.archive_id:
            return '%s/%s' % (self.URL_BASE, self.archive_id)

    def _get_post_data_archive(self):
        """Return data necessary to create archive"""

        if self.citation and self.citation.validated and self.folder_id:
            return {
                'url': self.citation.validated,
                'notes': self._get_note(),
                'folder': self.folder_id,
            }

    def _get_post_data_folder(self):
        """Return data necessary to create folder"""

        if self.citation:
            return {'name': self.citation.opinion.name}

    def _get_note(self):
        """Return metadata to associate with archive"""

        if self.citation:
            return 'This url was cited in US Supreme Court opinion "%s", which was published on %s' % (
                self.citation.opinion.name,
                self.citation.opinion.published.strftime('%Y.%m.%d'),
            )

    def _get_headers_dict(self):
        """Return json post headers"""

        return {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }

    def _set_opinion_folder_id(self):
        if PermaFolder.objects.filter(opinion__name=self.citation.opinion.name):
            # A folder for this citation's opinion already exists
            self.folder_id = PermaFolder.objects.get(opinion__name=self.citation.opinion.name).folder_id
        else:
            # Create new perma.cc folder for this citation's opinion
            self._create_opinion_folder()

    def _create_opinion_folder(self):
        if not self.folder_id:
            # Create new folder on perma.cc
            endpoint = '%s/folders/%s/folders/?api_key=%s' % (self.API_BASE, self.PARENT_FOLDER, self.KEY)
            response = post(
                endpoint,
                data=json.dumps(self._get_post_data_folder()),
                headers=self._get_headers_dict(),
            )

            # Create corresponding local database record for new folder on perma.cc
            response_dict = json.loads(response.text)
            self.folder_id = response_dict['id']
            folder = PermaFolder(
                folder_id=self.folder_id,
                opinion=Opinion(self.citation.opinion.id),
            )
            folder.save()
