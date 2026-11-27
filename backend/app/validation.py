#  InGen FastAPI wrapper — validation report derivation (pure logic)
#
#  Builds a ValidationReport in the SAME shape the frontend expects
#  ({ results:[{interface,column,expectation,severity,status,unexpectedCount}], summary }).
#
#  Best-effort: InGen runs great_expectations during execution and logs results, but does not emit
#  structured GE output. So this enumerates the column validations configured in the YAML and marks
#  status from the run outcome (a failing interface fails/wars its expectations by severity; a
#  succeeding interface passes them). Replacing this with parsed GE results is the future seam.


def _col_name(col: dict) -> str:
    return col.get("dest_col_name") or col.get("src_col_name") or "(unnamed)"


def derive_validation(config: dict, interface_names, failed_interfaces) -> dict:
    failed_interfaces = set(failed_interfaces or [])
    interfaces_cfg = config.get("interfaces", {}) or {}
    results = []

    for name in interface_names:
        iface = interfaces_cfg.get(name, {})
        for col in iface.get("columns", []) or []:
            column = _col_name(col)
            for v in col.get("validations", []) or []:
                severity = v.get("severity", "warning")
                if name in failed_interfaces:
                    status = "warning" if severity == "warning" else "failed"
                else:
                    status = "passed"
                results.append({
                    "interface": name,
                    "column": column,
                    "expectation": v.get("type"),
                    "severity": severity,
                    "status": status,
                    "unexpectedCount": 0 if status == "passed" else 1,
                })

    summary = {
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "warning": sum(1 for r in results if r["status"] == "warning"),
        "total": len(results),
    }
    return {"results": results, "summary": summary}
