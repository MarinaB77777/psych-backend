import re
from pathlib import Path


ALLOWLIST_FILES = [
    Path("static/assessment.html"),
    Path("static/pilot_result.html"),
    Path("static/research_workspace.html"),
    Path("static/data_check.html"),
    Path("static/data_preparation.html"),
    Path("static/analysis_builder.html"),
    Path("static/analysis_check.html"),
    Path("static/scientific_results.html"),
]


def _platform_i18n_source() -> str:
    return Path("static/platform_i18n.js").read_text(encoding="utf-8")


def test_allowlist_data_i18n_keys_exist_in_platform_i18n():
    source = _platform_i18n_source()
    missing = []

    for file_path in ALLOWLIST_FILES:
        html = file_path.read_text(encoding="utf-8")
        keys = sorted(set(re.findall(r'data-i18n="([^"]+)"', html)))
        for key in keys:
            if not re.search(rf"\b{re.escape(key)}\s*:", source):
                missing.append(f"{file_path}:{key}")

    assert missing == []


def test_platform_i18n_registered_phrases_have_all_rc_languages():
    source = _platform_i18n_source()
    assert "const PHRASES = {" in source
    body = source.split("const PHRASES = {", 1)[1].split(
        "for (const sourcePhrase of Object.keys",
        1,
    )[0]

    missing = []
    for phrase, value in re.findall(
        r'"([^"]+)":\s*\{([^{}]+)\}',
        body,
        re.S,
    ):
        for lang in ("ru", "en", "es"):
            if not re.search(rf"\b{lang}\s*:", value):
                missing.append(f"{phrase}:{lang}")

    assert missing == []
