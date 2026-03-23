frappe.query_reports["Spare Parts Inventory"] = {
	filters: [],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && flt(data.stock_qty) <= flt(data.reorder_level) && data.part_code) {
			value = `<span style="color:red;font-weight:bold">${value}</span>`;
		}
		return value;
	},
};
