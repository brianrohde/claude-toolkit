"""
Waiver loader: reads .claude/audit-waivers.json and checks expiry.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def load_waivers(root: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load waivers from .claude/audit-waivers.json."""
    waivers_file = root / '.claude' / 'audit-waivers.json'

    if not waivers_file.exists():
        return {}

    try:
        return json.loads(waivers_file.read_text(encoding='utf-8'))
    except Exception:
        return {}


def is_waived(rule_id: str, waivers: Dict[str, List[Dict[str, Any]]]) -> tuple[bool, str]:
    """
    Check if a rule is waived.
    Returns (is_waived, reason).
    """
    if rule_id not in waivers:
        return False, ""

    waiver_list = waivers[rule_id]
    if not waiver_list:
        return False, ""

    # Check first waiver (assuming only one per rule, but structure allows multiple)
    waiver = waiver_list[0]

    # Check expiry
    expires_str = waiver.get('expires')
    if expires_str:
        try:
            expires = datetime.strptime(expires_str, '%Y-%m-%d').date()
            today = datetime.now().date()

            if today > expires:
                return False, f"waiver expired on {expires_str}"
        except ValueError:
            pass

    reason = waiver.get('reason', 'No reason provided')
    return True, reason


def get_waiver_details(rule_id: str, waivers: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Get full waiver details for a rule."""
    if rule_id not in waivers or not waivers[rule_id]:
        return {}

    return waivers[rule_id][0]
