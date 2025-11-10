$(document).ready(function() {
    $("select#variables-dropdown").on("change", function (e) {
        var searchText = $("select#variables-dropdown").val().toLowerCase();
        var variables = $(".variable");
        variables.each(function (index) {
            var element = $(this).children().first().children().first();
            var title = element.attr("title") ? element.attr("title").toLowerCase() : undefined;
            var isMatch = title == searchText;
            if(searchText == ""){isMatch = true};
            $(this).toggle(isMatch);
        });
    });
});
