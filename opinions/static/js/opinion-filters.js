$(document).ready(function() {
    table_rows = $('tbody tr');

    filters = [
        {badge: $('#filter-all-count'), count: table_rows.length},
        {badge: $('#filter-citations-count'), count: $('.citation-count').length},
        {badge: $('#filter-revisions-count'), count: $('.revision').length},
    ];

    for (var i = 0; i < filters.length; i++) {
        filter = filters[i];
        filter.badge.text(filter.count);
        filter.badge.addClass((filter.count) ? 'label label-primary label-as-badge' : 'badge');
    }

    $('#javascript-filters').show();


    // All tab filter clicked
    $('#filter-all').on('click', function() {
        table_rows.show();
    });

    // With Citations tab filter clicked
    $('#filter-citations').on('click', function() {
        table_rows.hide();
        $('tr.has-citations').show();
    });

    // Revisions tab filter clicked
    $('#filter-revisions').on('click', function() {
        table_rows.hide();
        $('tr.revision').show();
    });
});
