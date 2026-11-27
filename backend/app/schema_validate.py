#  InGen FastAPI wrapper — config schema validation (pure logic, no execution)
#
#  Lightweight structural checks for POST /api/configs/validate. Returns issues in the same shape
#  the frontend's ConfigIssue uses ({ level, code, message, path }). Mirrors the integrity rules the
#  InGen MetaDataParser/SourceFactory rely on, without running the pipeline.

import yaml

from ingen.data_source.data_source_type import DataSourceType

# Source of truth: ingen's own enum. Adding a source type to ingen makes this validator accept it
# automatically — no parallel list to keep in sync. (Killed the drift the code review flagged.)
_VALID_SOURCE_TYPES = {e.value for e in DataSourceType}


def validate_yaml(yaml_text: str) -> dict:
    """Parse + structurally validate an InGen config. Returns { valid, issues }."""
    issues = []
    try:
        doc = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return {"valid": False, "issues": [{
            "level": "error", "code": "PARSE_ERROR",
            "message": f"Invalid YAML: {getattr(exc, 'problem', exc)}", "path": "",
        }]}

    if not isinstance(doc, dict):
        return {"valid": False, "issues": [{
            "level": "error", "code": "PARSE_ERROR",
            "message": "Top-level YAML must be a mapping with sources/interfaces.", "path": "",
        }]}

    sources = doc.get("sources") or []
    interfaces = doc.get("interfaces") or {}
    source_ids = {s.get("id") for s in sources if isinstance(s, dict)}

    if not interfaces:
        issues.append({"level": "warning", "code": "NO_INTERFACES",
                       "message": "Config defines no interfaces.", "path": "interfaces"})

    for s in sources:
        if not isinstance(s, dict) or not s.get("id"):
            issues.append({"level": "error", "code": "SOURCE_NO_ID",
                           "message": "A source is missing an id.", "path": "sources"})
            continue
        if s.get("type") not in _VALID_SOURCE_TYPES:
            issues.append({"level": "error", "code": "UNKNOWN_SOURCE_TYPE",
                           "message": f"Source '{s['id']}' has unsupported type '{s.get('type')}'.",
                           "path": f"sources.{s['id']}"})

    for name, iface in interfaces.items():
        iface = iface or {}
        for sid in iface.get("sources", []) or []:
            if sid not in source_ids:
                issues.append({"level": "error", "code": "UNKNOWN_SOURCE_REF",
                               "message": f"Interface '{name}' references undefined source '{sid}'.",
                               "path": f"interfaces.{name}.sources"})

    valid = not any(i["level"] == "error" for i in issues)
    return {"valid": valid, "issues": issues}
