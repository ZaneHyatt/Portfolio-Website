$(document).ready(function() {
    $('textarea').keyup(function(event) {
        if (event.which === 13)
        {
            event.preventDefault();
            $('form').submit();
        }
    });
});