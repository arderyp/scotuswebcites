$(document).ready(function() {
    table_rows = $('tbody tr');

    filters = [
        {badge: $('#filter-all-count'), count: table_rows.length},
        {badge: $('#filter-available-count'), count: $('.status-a').length},
        {badge: $('#filter-redirect-count'), count: $('.status-r').length},
        {badge: $('#filter-unavailable-count'), count: $('.status-u').length},
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

    // Available tab filter clicked
    $('#filter-available').on('click', function() {
        table_rows.hide();
        $('.status-a').parent().parent().show();
    });

    // Reidrect tab filter clicked
    $('#filter-redirect').on('click', function() {
        table_rows.hide();
        $('.status-r').parent().parent().show();
    });

    // Unavailable tab filter clicked
    $('#filter-unavailable').on('click', function() {
        table_rows.hide();
        $('.status-u').parent().parent().show();
    });
});
