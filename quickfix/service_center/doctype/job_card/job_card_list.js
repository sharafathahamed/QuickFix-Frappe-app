frappe.listview_settings["Job Card"] = {
	add_fields: ["status", "final_amount", "priority", "assigned_technician"],
	has_indicator_for_draft: true,
	get_indicator: function (doc) {
		let color_map = {
			Draft: "gray",
			"Pending Diagnosis": "yellow",
			"Awaiting Customer Approval": "orange",
			"In Repair": "blue",
			"Ready for Delivery": "green",
			Delivered: "darkgreen",
			Cancelled: "red",
		};
		return [doc.status, color_map[doc.status] || "gray", "status,=," + doc.status];
	},
	formatters: {
		final_amount: function (value) {
			if (!value) return "-";
			return `<b>₹${value.toLocaleString()}</b>`;
		},
		priority: function (value) {
			let color =
				{
					Normal: "green",
					High: "orange",
					Urgent: "red",
				}[value] || "gray";
			return `<span style="color:${color}"><b>${value}</b></span>`;
		},
	},
	button: {
		show: function (doc) {
			return doc.status === "In Repair";
		},
		get_label: function () {
			return "Mark Ready";
		},
		get_description: function (doc) {
			return `Mark ${doc.name} is Ready for Delivery!`;
		},
		action: function (doc) {
			frappe.confirm(`Mark ${doc.name} as Ready for Delivery?`, function () {
				frappe.call({
					method: "frappe.client.set_value",
					args: {
						doctype: "Job Card",
						name: doc.name,
						fieldname: "status",
						value: "Ready for Delivery",
					},
					callback: function () {
						cur_list.refresh();
					},
				});
			});
		},
	},
};
