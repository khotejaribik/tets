// Copyright (c) 2023, Ribik Khoteja and contributors
// For license information, please see license.txt

frappe.ui.form.on('Guest Quotation Item', {
    
    item_code: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    'doctype': 'Item Price',
                    'filters': {'item_code': child.item_code, 'price_list': 'Standard Selling'},
                    'fieldname': 'price_list_rate'
                },
                callback: function(r){	
                    frappe.model.set_value(cdt, cdn, 'rate', r.message.price_list_rate);
                    frappe.model.set_value(cdt, cdn, 'price_list_rate', r.message.price_list_rate);
                }
            });
                
            frm.refresh_field('items');
        },
    
    // Calculate Total Amount of Quotaion Item
    
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total_amount(frm);
    },
    
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total_amount(frm);
    },
    
    items_remove: function(frm) {
        calculate_total_amount(frm);
    },
});


//Calculate amount of items

function calculate_amount(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    var rate = child.rate;
    var qty = child.qty;
    var amount = rate * qty;
    frappe.model.set_value(cdt, cdn, 'amount', amount);
}


// Calculate sub total

function calculate_total_amount(frm) {
    var total_qty = 0;
    var sub_total = 0;

    frm.doc.items.forEach(function(item) {
        if (item.qty) {
            total_qty += item.qty;
        }

        if (item.qty && item.rate) {
            sub_total += (item.qty * item.rate);
        }
    });

    frm.set_value('total_qty', total_qty);
    frm.set_value('sub_total', sub_total);
}

