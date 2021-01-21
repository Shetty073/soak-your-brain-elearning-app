$(document).ready(function () {
    // Search the assignment submission table
    $("#assignments-list-search").on("keyup", function () {
        let term = $(this).val().toLowerCase();

        $("#assignments-table tbody tr").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(term) > -1);
        });
    });
});
