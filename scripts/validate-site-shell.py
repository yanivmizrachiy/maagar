#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the active static site shell and premium navigation contract.

The check does not modify files.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"
CSS = REPO / "assets" / "site.css"
PREMIUM_CSS = REPO / "assets" / "site-premium-nav.css"
JS = REPO / "assets" / "site.js"
URL_STATE_JS = REPO / "assets" / "site-url-state.js"
DEEPLINK_JS = REPO / "assets" / "site-deeplink.js"
SHARE_JS = REPO / "assets" / "site-share.js"
MODAL_SHARE_JS = REPO / "assets" / "site-modal-share.js"
HELP_JS = REPO / "assets" / "site-help.js"
SITE_STRUCTURE = REPO / "metadata" / "site-structure.json"
TAXONOMY = REPO / "metadata" / "taxonomy.json"

REQUIRED_IDS = ["q", "clear", "filters", "ttl", "meta", "app", "modal", "mt", "ms", "mo", "md", "x", "viewer"]
REQUIRED_HTML_SNIPPETS = ["viewport-fit=cover", 'name="theme-color"', 'name="color-scheme"', "apple-mobile-web-app-capable", "black-translucent", 'href="assets/site.css"', 'href="assets/site-premium-nav.css"']
REQUIRED_JS_SNIPPETS = [
    "metadata/index.json", "function card(", "function open(", "download", "view.officeapps.live.com",
    "const SORTS", "const GRADE_BUTTONS", "const DOMAIN_BUTTONS", "const EXAM_BUCKETS",
    "gradeGateway", "gradeGatewayCard", "grade-entry", "grade-entry-grid", "gradeHub",
    "data-grade-go", "data-domain", "data-exam", "data-sort", "infoLine", "file-details", "renderSoon", "prepareFiles",
]
REQUIRED_URL_STATE_SNIPPETS = [
    "searchParams", "grade", "category", "type", "exam", "sort", "cleanSort", "cleanExam", "activeGrade",
    "activeExam", "activeSort", "clickGrade", "clickExam", "clickSort", "history.replaceState", "data-k",
    "data-grade-go", "data-domain", "data-exam", "data-sort",
]
REQUIRED_DEEPLINK_SNIPPETS = ["searchParams.get('file')", "window.maagarFileLink", "data-view", "scrollIntoView"]
REQUIRED_SHARE_SNIPPETS = ["navigator.clipboard", "WhatsApp", "https://wa.me/", "MutationObserver", "העתק קישור", "maagarFileLink"]
REQUIRED_MODAL_SHARE_SNIPPETS = ["currentFileLink", "currentFileTitle", "copy-modal-file-link", "share-modal-file-whatsapp", "קישור לקובץ הועתק", "https://wa.me/"]
REQUIRED_HELP_SNIPPETS = ["skip-to-maagar", "ensureAccessibilityBasics", "normalizeActionButtons", "assets/icon.svg"]
REQUIRED_RESPONSIVE_CSS_SNIPPETS = ["safe-area-inset-top", "overflow-x:hidden", "@media(max-width:920px)", "@media(max-width:760px)", "@media(max-width:390px)", "@media(max-height:620px)", "minmax(min(285px,100%),1fr)", ".sortbar", ".sort-chip"]
REQUIRED_PREMIUM_CSS_SNIPPETS = [
    ".grade-gateway", ".grade-gateway-head", ".grade-entry-grid", ".grade-entry", ".grade-entry-kicker",
    ".gradebar", ".grade-go", ".grade-hub", ".domainbar", ".exambar", ".domain-chip", ".exam-chip", ".file-details", "Premium teacher navigation",
]
EXPECTED_HOME_LABELS = ["מתמטיקה לכיתה ז׳", "מתמטיקה לכיתה ח׳", "מתמטיקה לכיתה ט׳", "חטיבה עליונה"]
EXPECTED_GRADE_HUBS = ["middle-school-grade-7", "middle-school-grade-8", "middle-school-grade-9"]
EXPECTED_GRADE_BUTTONS = ["all", "algebra", "geometry", "summaries", "exams", "uncategorized_when_needed"]
EXPECTED_EXAM_NAV = ["all", "end", "mid", "start", "skill"]
EXPECTED_EXAM_KINDS = ["start", "mid", "end", "skill", "unknown"]
EXPECTED_FILE_FIELDS = ["author", "year", "grades", "primary_category", "topics", "tags", "document_type", "exam_kind", "source_type"]
EXPECTED_GATEWAY_CLASSES = ["grade-gateway", "grade-gateway-head", "grade-entry-grid", "grade-entry", "grade-entry-kicker"]
EXPECTED_GATEWAY_CARD_GRADES = ["7", "8", "9", "high-school"]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Path, label: str, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{label} invalid JSON: {exc}")
        return {}


def require(text: str, snippets: list[str], label: str, errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{label} missing snippet: {snippet}")


def validate_structure(structure: dict, taxonomy: dict, errors: list[str]) -> None:
    home_labels = [button.get("label") for button in structure.get("home", {}).get("buttons", [])]
    for label in EXPECTED_HOME_LABELS:
        if label not in home_labels:
            errors.append(f"site-structure home label missing: {label}")

    design = structure.get("design_policy", {})
    if design.get("navigation_style") != "premium-teacher-navigation":
        errors.append("site-structure design_policy.navigation_style is not premium-teacher-navigation")
    if design.get("visual_layer") != "assets/site-premium-nav.css":
        errors.append("site-structure design_policy.visual_layer is not assets/site-premium-nav.css")
    if design.get("must_use_large_gateway_cards_on_home") is not True:
        errors.append("site-structure design_policy.must_use_large_gateway_cards_on_home must be true")

    gateway = structure.get("grade_gateway", {})
    if gateway.get("id") != "grade-gateway":
        errors.append("site-structure grade_gateway.id must be grade-gateway")
    for css_class in EXPECTED_GATEWAY_CLASSES:
        if css_class not in gateway.get("visual_classes", []):
            errors.append(f"site-structure grade_gateway.visual_classes missing: {css_class}")
    gateway_grades = [card.get("target_grade") for card in gateway.get("cards", [])]
    for grade in EXPECTED_GATEWAY_CARD_GRADES:
        if grade not in gateway_grades:
            errors.append(f"site-structure grade_gateway.cards missing target_grade: {grade}")

    hubs = {screen.get("id"): screen for screen in structure.get("middle_school_screens", [])}
    for hub_id in EXPECTED_GRADE_HUBS:
        screen = hubs.get(hub_id)
        if not screen:
            errors.append(f"site-structure missing grade hub: {hub_id}")
            continue
        for button in EXPECTED_GRADE_BUTTONS:
            if button not in screen.get("buttons", []):
                errors.append(f"site-structure {hub_id} missing button: {button}")

    for key in EXPECTED_EXAM_NAV:
        if key not in structure.get("exam_navigation", {}):
            errors.append(f"site-structure exam_navigation missing: {key}")

    file_fields = set(structure.get("file_card_fields", []))
    for field in EXPECTED_FILE_FIELDS:
        if field not in file_fields:
            errors.append(f"site-structure file_card_fields missing: {field}")

    exam_kinds = set(taxonomy.get("exam_kinds", []))
    for key in EXPECTED_EXAM_KINDS:
        if key not in exam_kinds:
            errors.append(f"taxonomy exam_kinds missing: {key}")

    required_nav = taxonomy.get("site_navigation_required", {})
    for key in EXPECTED_EXAM_NAV:
        if key not in required_nav.get("exam_navigation", []):
            errors.append(f"taxonomy site_navigation_required.exam_navigation missing: {key}")


def main() -> int:
    errors: list[str] = []
    required_files = [
        (INDEX, "index.html"), (CSS, "assets/site.css"), (PREMIUM_CSS, "assets/site-premium-nav.css"),
        (JS, "assets/site.js"), (URL_STATE_JS, "assets/site-url-state.js"), (DEEPLINK_JS, "assets/site-deeplink.js"),
        (SHARE_JS, "assets/site-share.js"), (MODAL_SHARE_JS, "assets/site-modal-share.js"),
        (HELP_JS, "assets/site-help.js"), (SITE_STRUCTURE, "metadata/site-structure.json"), (TAXONOMY, "metadata/taxonomy.json"),
    ]
    for path, label in required_files:
        if not path.exists():
            errors.append(f"{label} missing")
    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    html = read(INDEX)
    css = read(CSS)
    premium_css = read(PREMIUM_CSS)
    js = read(JS)
    url_state_js = read(URL_STATE_JS)
    deeplink_js = read(DEEPLINK_JS)
    share_js = read(SHARE_JS)
    modal_share_js = read(MODAL_SHARE_JS)
    help_js = read(HELP_JS)
    structure = load_json(SITE_STRUCTURE, "metadata/site-structure.json", errors)
    taxonomy = load_json(TAXONOMY, "metadata/taxonomy.json", errors)

    require(html, REQUIRED_HTML_SNIPPETS, "index.html", errors)
    for item_id in REQUIRED_IDS:
        if f'id="{item_id}"' not in html:
            errors.append(f"index.html missing id={item_id}")
    for script in ["site.js", "site-url-state.js", "site-deeplink.js", "site-share.js", "site-modal-share.js", "site-help.js"]:
        if f'src="assets/{script}"' not in html:
            errors.append(f"index.html does not load assets/{script}")

    require(js, REQUIRED_JS_SNIPPETS, "assets/site.js", errors)
    require(url_state_js, REQUIRED_URL_STATE_SNIPPETS, "assets/site-url-state.js", errors)
    require(deeplink_js, REQUIRED_DEEPLINK_SNIPPETS, "assets/site-deeplink.js", errors)
    require(share_js, REQUIRED_SHARE_SNIPPETS, "assets/site-share.js", errors)
    require(modal_share_js, REQUIRED_MODAL_SHARE_SNIPPETS, "assets/site-modal-share.js", errors)
    require(help_js, REQUIRED_HELP_SNIPPETS, "assets/site-help.js", errors)
    require(css, REQUIRED_RESPONSIVE_CSS_SNIPPETS, "assets/site.css", errors)
    require(premium_css, REQUIRED_PREMIUM_CSS_SNIPPETS, "assets/site-premium-nav.css", errors)
    validate_structure(structure, taxonomy, errors)

    print("MAAGAR SITE SHELL VALIDATION")
    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1
    print("OK    site shell, premium grade gateway, teacher navigation, metadata navigation, exam taxonomy, sharing and help are wired correctly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
