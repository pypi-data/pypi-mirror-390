from dateutil.relativedelta import relativedelta

from odoo import models, _
from odoo.exceptions import UserError

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

IR_TRANSLATION_NAME = "account.asset.report"


class AssetReportXlsx(models.AbstractModel):
    _inherit = "report.account_asset_management.asset_report_xls"

    def _get_asset_template(self):
        asset_template = super()._get_asset_template()
        asset_template.update(
            {
                "date_end": {
                    "header": {
                        "type": "string",
                        "value": _("Asset End Date"),
                    },
                    "asset": {
                        "value": self._render("period_end_date"),
                        "format": FORMATS["format_tcell_date_left"],
                    },
                    "width": 20,
                },
                "perc_amort_anual": {
                    "header": {
                        "type": "string",
                        "value": _("% Amort Anual"),
                        "format": FORMATS["format_theader_yellow_center"],
                    },
                    "asset": {
                        "value": self._render("perc_amort_anual"),
                        "format": FORMATS["format_tcell_percent_center"],
                    },
                    "width": 20,
                },
            }
        )

        return asset_template

    def _asset_report(self, workbook, ws, ws_params, data, wiz):
        report = ws_params["report_type"]

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])

        wl = ws_params["wanted_list"]
        if "account" not in wl:
            raise UserError(
                _(
                    "The 'account' field is a mandatory entry of the "
                    "'_xls_%s_fields' list !"
                )
                % report
            )

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._report_title(ws, row_pos, ws_params, data, wiz)

        def asset_filter(asset):
            filt = getattr(self, "{}_filter".format(report))
            return filt(wiz, asset)

        assets = data["assets"].filtered(asset_filter)

        if not assets:
            return self._empty_report(ws, row_pos, ws_params, data, wiz)

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_yellow_left"],
        )

        ws.freeze_panes(row_pos, 0)

        row_pos_start = row_pos
        purchase_value_pos = "purchase_value" in wl and wl.index("purchase_value")
        depreciation_base_pos = "depreciation_base" in wl and wl.index(
            "depreciation_base"
        )
        salvage_value_pos = "salvage_value" in wl and wl.index("salvage_value")
        period_start_value_pos = "period_start_value" in wl and wl.index(
            "period_start_value"
        )
        period_end_value_pos = "period_end_value" in wl and wl.index("period_end_value")

        period_start_pos = "date_start" in wl and wl.index("date_start")
        perc_amort_anual_pos = "perc_amort_anual" in wl and wl.index("perc_amort_anual")

        entries = []
        root = wiz.asset_group_id
        root_val = data["grouped_assets"][root]
        error_dict = {
            "no_table": self.env["account.asset"],
            "dups": self.env["account.asset"],
        }

        self._create_report_entries(ws_params, wiz, entries, root, root_val, error_dict)

        # traverse entries in reverse order to calc totals
        for i, entry in enumerate(reversed(entries)):
            if "group" in entry:
                parent = entry["group"].parent_id
                for parent_entry in reversed(entries[: -i - 1]):
                    if "group" in parent_entry and parent_entry["group"] == parent:
                        parent_entry["_purchase_value"] += entry["_purchase_value"]
                        parent_entry["_depreciation_base"] += entry[
                            "_depreciation_base"
                        ]
                        parent_entry["_salvage_value"] += entry["_salvage_value"]
                        parent_entry["_period_start_value"] += entry[
                            "_period_start_value"
                        ]
                        parent_entry["_period_end_value"] += entry["_period_end_value"]
                        continue

        processed = []
        for entry in entries:
            period_start_date_cell = period_start_pos and self._rowcol_to_cell(
                row_pos, period_start_pos
            )
            perc_amort_anual_cell = perc_amort_anual_pos and self._rowcol_to_cell(
                row_pos, perc_amort_anual_pos
            )

            period_end_date_cell = ""
            if period_start_date_cell and perc_amort_anual_cell:
                period_end_date_cell = (
                    period_start_date_cell + "+365*1/" + perc_amort_anual_cell
                )

            period_start_value_cell = period_start_value_pos and self._rowcol_to_cell(
                row_pos, period_start_value_pos
            )
            period_end_value_cell = period_end_value_pos and self._rowcol_to_cell(
                row_pos, period_end_value_pos
            )
            depreciation_base_cell = depreciation_base_pos and self._rowcol_to_cell(
                row_pos, depreciation_base_pos
            )
            period_diff_formula = period_end_value_cell and (
                period_start_value_cell + "-" + period_end_value_cell
            )
            total_depr_formula = period_end_value_cell and (
                depreciation_base_cell + "-" + period_end_value_cell
            )

            if "group" in entry:
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params,
                    col_specs_section="asset_group",
                    render_space={
                        "group": entry["group"],
                        "group_entry": entry,
                        "period_diff_formula": period_diff_formula,
                        "total_depr_formula": total_depr_formula,
                    },
                    default_format=FORMATS["format_theader_blue_left"],
                )

            else:
                asset = entry["asset"]
                if asset in processed:
                    error_dict["dups"] += asset
                    continue
                else:
                    if asset.method_end:
                        period_end_date = asset.method_end
                        years = (
                            relativedelta(asset.method_end, asset.date_start).years
                            + relativedelta(asset.method_end, asset.date_start).months
                            / 12
                        )
                        if years == 0:
                            years = 1
                    else:
                        years = int(
                            asset.method_number
                            if asset.method_time == "year"
                            else 100 / asset.annual_percentage
                        )
                        period_end_date = asset.date_start + relativedelta(years=years)
                        processed.append(asset)
                    perc_amort_anual = 1 / years
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params,
                    col_specs_section="asset",
                    render_space={
                        "asset": entry["asset"],
                        "asset_entry": entry,
                        "period_diff_formula": period_diff_formula,
                        "total_depr_formula": total_depr_formula,
                        "period_end_date_cell": period_end_date_cell,
                        "period_end_date": period_end_date,
                        "years": years,
                        "perc_amort_anual": perc_amort_anual,
                    },
                    default_format=FORMATS["format_theader_blue_left"],
                )
        purchase_total_formula = purchase_value_pos and self._rowcol_to_cell(
            row_pos_start, purchase_value_pos
        )
        asset_total_formula = depreciation_base_pos and self._rowcol_to_cell(
            row_pos_start, depreciation_base_pos
        )
        salvage_total_formula = salvage_value_pos and self._rowcol_to_cell(
            row_pos_start, salvage_value_pos
        )
        period_start_total_formula = period_start_value_pos and self._rowcol_to_cell(
            row_pos_start, period_start_value_pos
        )
        period_end_total_formula = period_end_value_pos and self._rowcol_to_cell(
            row_pos_start, period_end_value_pos
        )
        period_dif_total_formula = period_start_total_formula

        if period_start_total_formula and period_end_total_formula:
            period_dif_total_formula = (
                period_start_total_formula + "-" + period_end_total_formula
            )

        period_start_value_cell = period_start_value_pos and self._rowcol_to_cell(
            row_pos, period_start_value_pos
        )
        period_end_value_cell = period_end_value_pos and self._rowcol_to_cell(
            row_pos, period_end_value_pos
        )
        depreciation_base_cell = depreciation_base_pos and self._rowcol_to_cell(
            row_pos, depreciation_base_pos
        )
        period_diff_formula = period_end_value_cell and (
            period_start_value_cell + "-" + period_end_value_cell
        )
        total_depr_formula = period_end_value_cell and (
            depreciation_base_cell + "-" + period_end_value_cell
        )

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="totals",
            render_space={
                "purchase_total_formula": purchase_total_formula,
                "asset_total_formula": asset_total_formula,
                "salvage_total_formula": salvage_total_formula,
                "period_start_total_formula": period_start_total_formula,
                "period_end_total_formula": period_end_total_formula,
                "period_diff_formula": period_diff_formula,
                "total_depr_formula": total_depr_formula,
                "period_dif_total_formula": period_dif_total_formula,
                "period_end_date_cell": period_end_date_cell,
            },
            default_format=FORMATS["format_theader_yellow_left"],
        )

        for k in error_dict:
            if error_dict[k]:
                if k == "no_table":
                    reason = _("Missing depreciation table")
                elif k == "dups":
                    reason = _("Duplicate reporting entries")
                else:
                    reason = _("Undetermined error")
                row_pos += 1
                err_msg = _("Assets to be corrected") + ": "
                err_msg += "%s" % [x[1] for x in error_dict[k].name_get()]
                err_msg += " - " + _("Reason") + ": " + reason
                ws.write_string(row_pos, 0, err_msg, FORMATS["format_left_bold"])
