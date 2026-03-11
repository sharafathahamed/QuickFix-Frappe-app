frappe.ui.form.on("Job Card",
    {
        priority: function(frm){
            if(frm.doc.priority==="Urgent"){
                frappe.show_alert({
                    message:"This is an URGENT job!",
                    indicator:"red"
                });
            }
        },
        onload: function(frm){
            frappe.call("frappe.client.get_count",{doctype:"Job Card"});
            frappe.realtime.on("job_ready",function(data){
                frappe.show_alert({
                    message:`Job ${data.job_card} is Ready for Delivery!`,
                    indicator:"green"
                });
            });
        },
        setup: function(frm){
            frm.set_query("assigned_technician",function(){
                return{
                    filters:{
                        "status":"Active",
                        "specialization":frm.doc.device_type
                    }
                };
            });
        },
        refresh: function(frm){
            if(frappe.boot.quickfix_shop_name){
                frm.set_intro(frappe.boot.quickfix_shop_name,"blue");
            }
            let colorm={
                "Draft":"gray",
                "Pending Diagnosis":"yellow",
                "Awaiting Customer Approval":"orange",
                "In Repair":"blue",
                "Ready for Delivery":"green",
                "Delivered":"darkgreen",
                "Cancelled":"red"
            };
            frm.dashboard.add_indicator(frm.doc.status,colorm[frm.doc.status]||"gray");
            if(frm.doc.status==="Ready for Delivery" && frm.doc.docstatus===1){
                frm.add_custom_button("Mark as Delivered",function(){
                    frappe.confirm("Mark this Job Card as Delivered?",function(){
                        frm.set_value("status","Delivered");
                        frm.save();
                    });
                }).addClass("btn-success");
            }
            if(frm.doc.docstatus===0 && frm.doc.status!=="Cancelled"){
                frm.add_custom_button("Reject Job",function(){
                    let dialog=new frappe.ui.Dialog({
                        title:"Reject Job",
                        fields:[
                            {
                                fieldname:"rejection_reason",
                                fieldtype:"Text",
                                label:"Rejection Reason",
                                reqd:1
                            }
                        ],
                        primary_action_label:"Reject",
                        primary_action:function(values){
                            frappe.call({
                                method:"quickfix.api.reject_job",
                                args:{
                                    job_card:frm.doc.name,
                                    reason:values.rejection_reason
                                },
                                callback:function(r){
                                    dialog.hide();
                                    frm.reload_doc();
                                }
                            });
                        }
                    });
                    dialog.show();
                }).addClass("btn-danger");
            }
            if(frm.doc.docstatus===0){
                frm.add_custom_button("Transfer Technician",function(){
                    frappe.prompt(
                        {
                            fieldname:"new_technician",
                            fieldtype:"Link",
                            options:"Technician",
                            label:"New Technician",
                            reqd:1
                        },
                        function(values){
                            frappe.confirm(
                                `Transfer job to ${values.new_technician}?`,
                                function(){
                                    frappe.call({
                                        method:"quickfix.api.transfer_technician",
                                        args:{
                                            job_card:frm.doc.name,
                                            new_technician:values.new_technician
                                        },
                                        callback:function(r){
                                            frm.set_value("assigned_technician",values.new_technician);
                                            frm.trigger("assigned_technician");
                                            frm.save();
                                        }
                                    });
                                }
                            );
                        },
                        "Transfer Technician",
                        "Transfer"
                    );
                }).addClass("btn-warning");
            }
            if(!frappe.user.has_role("QF Manager")){
                frm.set_df_property("customer_phone","hidden",1);
            }
        },
        device_type: function(frm){
            frm.set_value("assigned_technician","");
        },
        assigned_technician: function(frm){
            if(!frm.doc.assigned_technician) return;
            frappe.db.get_value(
                "Technician",
                frm.doc.assigned_technician,
                "specialization",
                function(data){
                    if(data && data.specialization!==frm.doc.device_type){
                        frappe.msgprint({
                            title:"Warning",
                            message:`Technician specializes in ${data.specialization} but device is ${frm.doc.device_type}`,
                            indicator:"orange"
                        });
                    }
                }
            );
        }
    }
);
frappe.ui.form.on("Part Usage Entry",{
    quantity:function(frm,cdt,cdn){
        let row=locals[cdt][cdn];
        frappe.model.set_value(cdt,cdn,"total_price",row.quantity*row.unit_price);
    }
});