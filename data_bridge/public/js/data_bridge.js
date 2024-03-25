frappe.ui.form.on('Warranty Claim', {
    refresh: function(frm) {
        var customer = frm.fields_dict['delivery_note'];
        if (customer) {
            customer.get_query = function(doc) {
                return {
                    filters: {
                        customer: frm.doc.customer
                    }
                };
            };
        }
    }
});

frappe.ui.form.on('Partner Quotation', {
    refresh: function(frm) {
        //Add filter to seller profile
        var seller = frm.fields_dict['seller']
        if (seller) {
            seller.get_query = function(doc) {
                return {
                    filters: {
                        my_company_name: frm.doc.my_company_name
                    }
                };
            };
        }
        
        //Add filter to customer profile
        var customer = frm.fields_dict['customer']
        if (customer) {
            customer.get_query = function(doc) {
                return {
                    filters: {
                        my_company_name: frm.doc.my_company_name
                    }
                };
            };
        }
        
      
        //Add filter to website item code
        var website_item = frm.fields_dict['items'].grid.get_field('website_item');
        if (website_item) {
            website_item.get_query = function(doc) {
                return {
                    filters: {
                        published: 1
                    }
                };
            };
        }
        
        //Add filter to partner item code
        var partner_item = frm.fields_dict['items'].grid.get_field('partner_item');
        if (partner_item) {
            partner_item.get_query = function(doc) {
                return {
                    filters: {
                        my_company_name: frm.doc.my_company_name
                    }
                };
            };
        }
    },
    
    my_company_name: function(frm) {
        frm.set_value("seller", null);
        frm.set_value("customer", null);
    },

	total: function(frm) {
        calculate_total_charges(frm);
        calculate_taxable_amount(frm);
        calculate_net_total(frm);
    },
    
    sub_total: function(frm) {
        calculate_taxable_amount(frm);
    },
    
    discount_type: function(frm) {
        if(frm.doc.discount_type == "Percentage") {
            frm.set_value("discount_amount", null);
        } else if(frm.doc.discount_type == "Amount") {
            frm.set_value("discount_percent", null);
        }
        else if (!frm.doc.discount_type) {  // If discount_type is empty
            frm.set_value("discount_amount", null);
            frm.set_value("discount_percent", null);
        }
        
        calculate_taxable_amount(frm);
        calculate_net_total(frm)
    },
    
    discount_percent: function(frm) {
        calculate_taxable_amount(frm);
        calculate_net_total(frm)
    },
    
    discount_amount: function(frm) {
        calculate_taxable_amount(frm);
        calculate_net_total(frm)
    },
    
    taxable_amount: function(frm) {
        calculate_net_total(frm);
    },
    
    add_tax: function(frm) {
        calculate_net_total(frm);
    },
    
    tax_rate: function(frm) {
        calculate_net_total(frm);
    },
    
    net_total: function(frm) {
        calculate_grand_total(frm);
    },
    
    non_taxable_charge: function(frm) {
        calculate_grand_total(frm);
    }
    
})


frappe.ui.form.on('Partner Quotation Item', {
    
    // Reset all the fetched fields
    
    item_master: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        
        if(child.item_master == "Website Item") {
            child.partner_item = "";
    
        } else if(child.item_master == "Partner Item") {
            child.website_item = "";
        }
        
        child.item_name = "";
        child.item_code = "";
        child.qty = "1";
        child.rate = "";
        child.price_list_rate = "";
        child.description = "";
        child.image = "";
        child.warranty = "";
        frm.refresh_field('items');
    },
    
    // Fetch required fields from item code
    
    //For website item code
    
    website_item: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Website Item',
                'filters': {'name': child.website_item},
                'fieldname': ['item_code', 'short_description', 'website_image']
            },
            callback: function(r){	
                frappe.model.set_value(cdt, cdn, 'item', r.message.item_code);
                frappe.model.set_value(cdt, cdn, 'description', r.message.short_description);
                frappe.model.set_value(cdt, cdn, 'image', r.message.website_image);
                
                frappe.call({
                    method: 'frappe.client.get_value',
                    args: {
                        'doctype': 'Item Price',
                        'filters': {'item_code': child.item, 'price_list': 'Standard Selling'},
                        'fieldname': 'price_list_rate'
                    },
                    callback: function(r){	
                        frappe.model.set_value(cdt, cdn, 'rate', r.message.price_list_rate);
                        frappe.model.set_value(cdt, cdn, 'price_list_rate', r.message.price_list_rate);
                    }
                });
                
                frappe.call({
                    method: 'frappe.client.get_value',
                    args: {
                        'doctype': 'Item',
                        'filters': {'item_code': child.item},
                        'fieldname': 'warranty_period'
                    },
                    callback: function(r){	
                        frappe.model.set_value(cdt, cdn, 'warranty', r.message.warranty_period);
                    }
                });
                                    
                frm.refresh_field('items');
            }
            
        });
        

        
    },
    
    //For partner item code

    partner_item: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Partner Item',
                'filters': {'name': child.partner_item},
                'fieldname': ['item_name', 'rate', 'description', 'image', 'warranty']
            },
            callback: function(r){
                frappe.model.set_value(cdt, cdn, 'item', r.message.item_name);
                frappe.model.set_value(cdt, cdn, 'rate', r.message.rate);
                frappe.model.set_value(cdt, cdn, 'price_list_rate', r.message.rate);
                frappe.model.set_value(cdt, cdn, 'description', r.message.description);
                frappe.model.set_value(cdt, cdn, 'image', r.message.image);
                frappe.model.set_value(cdt, cdn, 'warranty', r.message.warranty);
                
                frm.refresh_field('items');
            }
        });

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
    var total = 0;

    frm.doc.items.forEach(function(item) {
        if (item.qty) {
            total_qty += item.qty;
        }

        if (item.qty && item.rate) {
            total += (item.qty * item.rate);
        }
    });

    frm.set_value('total_qty', total_qty);
    frm.set_value('total', total);
}


//Calculate taxable charge and non taxable charge

function calculate_total_charges(frm) {
    var taxable_charge = 0;
    var non_taxable_charge = 0;
    var sub_total = 0;
    var total = frm.doc.total;
    frm.doc.additional_charge.forEach(function(row) {
        if(row.include_tax) {
            taxable_charge += row.amount;
        } else {
            non_taxable_charge += row.amount;
        }
    });
    
    if (taxable_charge) {
        sub_total = total + taxable_charge;
        
    } else {
        sub_total = total;
    }

    frm.set_value('taxable_charge', taxable_charge);
    frm.set_value('non_taxable_charge', non_taxable_charge);
    frm.set_value('sub_total', sub_total);
}


//Calculate taxable charge and non taxable charge while changing the Partner Quotation Additional Charges values

frappe.ui.form.on('Partner Quotation Additional Charge', {
    amount: function(frm, cdt, cdn) {
        calculate_total_charges(frm);
    },
    include_tax: function(frm, cdt, cdn) {
        calculate_total_charges(frm);
    },
    additional_charge_remove: function(frm, cdt, cdn) {
        calculate_total_charges(frm);
    },
});


//Calculate taxable amount

function calculate_taxable_amount(frm) {
    var sub_total = frm.doc.sub_total;
    var discount_amount = frm.doc.discount_amount;
    var discount_percent = frm.doc.discount_percent;
    var discount_type = frm.doc.discount_type;
    var taxable_amount = frm.doc.sub_total;

    if (discount_type === "Percentage") {
        if (discount_percent) {
            taxable_amount = sub_total * (100 - discount_percent) / 100;
        }
    } else if (discount_type === "Amount") {
        if (discount_amount) {
            taxable_amount = sub_total - discount_amount;
        }
    } else {
        taxable_amount = sub_total;
    }
    
    frm.set_value('taxable_amount', taxable_amount);
}


// Calculate net total

function calculate_net_total(frm) {
    var taxable_amount = frm.doc.taxable_amount;
    var net_total = 0;
    
    if (frm.doc.add_tax) {
        var tax_rate = frm.doc.tax_rate;
        var tax_amount = taxable_amount * (tax_rate / 100);
        frm.set_value('tax_amount', tax_amount);
        net_total = taxable_amount + tax_amount;
    } else {
        frm.set_value('tax_amount', 0);
        net_total = taxable_amount;
    }
    
    frm.set_value('net_total', net_total);
}


// Calculate grand total

function calculate_grand_total(frm) {
    var net_total = frm.doc.net_total;
    var grand_total = 0;
    var non_taxable_charge = frm.doc.non_taxable_charge;    
    
    grand_total += non_taxable_charge;
    grand_total += net_total;  // add net_total to grand_total
    
    frm.set_value('grand_total', grand_total);
}


frappe.ui.form.on('Partner Quotation Template', {
    refresh: function(frm) {
        var print_format = frm.fields_dict['template'].grid.get_field('print_format');
        if (print_format) {
            print_format.get_query = function(doc) {
                return {
                    filters: {
                        doc_type: "Partner Quotation",
                    }
                };
            };
        }    
    }
})  