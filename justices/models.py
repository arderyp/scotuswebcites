from django.db import models

class Justice(models.Model):
    JUSTICE_IDS = {
        'A': 'Samuel Alito',
        'AS': 'Antonin Scalia',
        'B': 'Stephen Breyer',
        'D': 'Decree',
        'DS': 'David Souter',
        'EK': 'Elana Kagan',
        'G': 'Ruth Bader Ginsburg',
        'JS': 'John Paul Stephens',
        'K': 'Anthony Kennedy',
        'PC': 'Per Curiam',
        'R': 'John G. Roberts',
        'SS': 'Sonia Sotomayor',
        'T': 'Clarence Thomas',
        'UK': 'UNKNOWN',
    }

    id = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=50) 

    def set_counts(self):
        """Initialize opinion_count and citation_average_count properties"""
        from opinions.models import Opinion
        from citations.models import Citation

        self.opinion_count = Opinion.objects.filter(justice_id=self.id).count()
        self.citation_count = Citation.objects.filter(opinion_id__justice_id=self.id).count()

        if self.citation_count:
            average = self.citation_count / float(self.opinion_count)

            # Format to 2 decimal places
            self.citation_average_count = float("%.2f" % average)
        else:
            self.citation_average_count = 0
