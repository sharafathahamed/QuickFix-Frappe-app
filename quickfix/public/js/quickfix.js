frappe.ready(function () {
    if (frappe.boot.quickfix_shop_name) {
        $(".navbar-brand").append(
            ` <span class="small text-muted">- ${frappe.boot.quickfix_shop_name}</span>`
        );
    }
});
