from __future__ import annotations

import os
from pathlib import Path


DATA_ROOT_ENV = "PILOT_RC_DATA_ROOT"
REQUIRE_DATA_ROOT_ENV = "PILOT_RC_REQUIRE_PERSISTENT_DATA_ROOT"

RESEARCHER_USERNAME_ENV = "RESEARCHER_ACCESS_USERNAME"
RESEARCHER_PASSWORD_ENV = "RESEARCHER_ACCESS_PASSWORD"
RESEARCHER_SESSION_SECRET_ENV = "RESEARCHER_SESSION_SECRET"


def is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def configured_data_root() -> Path | None:
    value = os.getenv(DATA_ROOT_ENV)
    if not value:
        return None
    return Path(value).expanduser().resolve()


def require_persistent_data_root() -> bool:
    return is_truthy(os.getenv(REQUIRE_DATA_ROOT_ENV)) or is_truthy(
        os.getenv("RENDER")
    )


def data_path(*parts: str, legacy: str | Path) -> Path:
    root = configured_data_root()
    if root is None:
        return Path(legacy)
    return root.joinpath(*parts)


def validate_persistent_data_root() -> dict:
    root = configured_data_root()
    required = require_persistent_data_root()

    if root is None:
        if required:
            raise RuntimeError(
                f"{DATA_ROOT_ENV} is required for Pilot RC persistent storage"
            )
        return {
            "ok": True,
            "configured": False,
            "mode": "legacy-local",
            "warning": (
                "Pilot RC data is using legacy local paths and may not "
                "survive deployment restart."
            ),
        }

    root.mkdir(parents=True, exist_ok=True)
    if not root.is_dir():
        raise RuntimeError(f"{DATA_ROOT_ENV} is not a directory")

    probe = root / ".write_test"
    probe.write_text("ok\n", encoding="utf-8")
    probe.unlink(missing_ok=True)

    return {
        "ok": True,
        "configured": True,
        "mode": "persistent-data-root",
        "path": str(root),
    }


def researcher_access_configured() -> bool:
    return all(
        os.getenv(name)
        for name in (
            RESEARCHER_USERNAME_ENV,
            RESEARCHER_PASSWORD_ENV,
            RESEARCHER_SESSION_SECRET_ENV,
        )
    )


def require_researcher_access_config() -> bool:
    return is_truthy(os.getenv("PILOT_RC_REQUIRE_RESEARCHER_AUTH")) or is_truthy(
        os.getenv("RENDER")
    )


def validate_researcher_access_config() -> dict:
    configured = researcher_access_configured()
    if not configured and require_researcher_access_config():
        raise RuntimeError(
            "Researcher access env vars are required for Pilot RC: "
            f"{RESEARCHER_USERNAME_ENV}, {RESEARCHER_PASSWORD_ENV}, "
            f"{RESEARCHER_SESSION_SECRET_ENV}"
        )
    return {
        "ok": True,
        "configured": configured,
        "mode": "cookie-gate" if configured else "legacy-local-unprotected",
    }
