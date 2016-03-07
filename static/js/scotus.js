$(document).ready(function(){
    // Dissolve flash messages
    $('.flash-dissolve').delay(4000).fadeOut(800)

    // Hide messages for sessions with js disabled
    $('.js-disabled').hide();

    // Show loading wheel when click verify
    $('input[value="Verify"]').click(function () {
        $('div.load-wheel').show();
    });

    // Move overview div down so displays under the chart
    $('.overview').css( 'top', '275px');

    // Use sticky table header if table on page
    $(".sticky-header").floatThead({scrollingTop:50});
});
