// For bootstrap tooltip
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

// Animated number counter
$('.count').each(function () {
    let $this = $(this);
    jQuery({Counter: 0}).animate({Counter: $this.text()}, {
        duration: 1000,
        easing: 'swing',
        step: function () {
            $this.text(Math.ceil(this.Counter));
        }
    });
});

// for colleges table searchbar
$("#searchbar").on("keyup", function () {
    let term = $(this).val().toLowerCase();
    $("#college-table tbody tr").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(term) > -1);
    });
});

// for invoices table searchbar
$("#invoice-searchbar").on("keyup", function () {
    let term = $(this).val().toLowerCase();
    $("#invoice-table tbody tr").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(term) > -1);
    });
});

// for syb admins table searchbar
$("#syb-admins-searchbar").on("keyup", function () {
    let term = $(this).val().toLowerCase();
    $("#syb-admins-table tbody tr").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(term) > -1);
    });
});


// view_college_details page



// view_invoice_details page
// print invoice button
$(document).on('click', '#print-invoice-btn', function () {
    $(this).hide();
    let prtContent = $('#invoice-details-card');
    let WinPrint = window.open('', '', 'left=0,top=0,width=800,height=900,toolbar=0,scrollbars=0,status=0');
    WinPrint.document.write(document.head.innerHTML);
    WinPrint.document.write(prtContent.html());
    WinPrint.document.close();
    WinPrint.focus();
    WinPrint.print();
    $(this).show();
});
