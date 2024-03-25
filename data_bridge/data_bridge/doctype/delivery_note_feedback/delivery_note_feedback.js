// Copyright (c) 2023, Ribik Khoteja and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Note Feedback', {
	refresh(frm) {
	    var delivery_note = frm.fields_dict['delivery_note']
        if (delivery_note) {
            delivery_note.get_query = function(doc) {
                return {
                    filters: {
                        customer: frm.doc.company_name
                    }
                };
            };
        }  
	}
});