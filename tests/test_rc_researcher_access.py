import importlib


def test_researcher_session_signature_requires_configured_secret(monkeypatch):
    monkeypatch.setenv("RESEARCHER_ACCESS_USERNAME", "researcher")
    monkeypatch.setenv("RESEARCHER_ACCESS_PASSWORD", "secret-password")
    monkeypatch.setenv("RESEARCHER_SESSION_SECRET", "test-session-secret")

    import main

    app_module = importlib.reload(main)

    token = app_module.sign_researcher_session("researcher")
    assert app_module.verify_researcher_session(token) is True
    assert app_module.verify_researcher_session(token + "x") is False


def test_researcher_protected_path_classifier():
    import main

    assert main.is_researcher_protected_path("/research-workspace") is True
    assert main.is_researcher_protected_path("/research/participant-data/records") is True
    assert (
        main.is_researcher_protected_path(
            "/pilot/sessions/session-1/consistency-clarifications"
        )
        is True
    )
    assert main.is_researcher_protected_path("/assessment") is False
    assert main.is_researcher_protected_path("/pilot/sessions/session-1/result") is False


def test_render_requires_researcher_access_env(monkeypatch):
    monkeypatch.delenv("RESEARCHER_ACCESS_USERNAME", raising=False)
    monkeypatch.delenv("RESEARCHER_ACCESS_PASSWORD", raising=False)
    monkeypatch.delenv("RESEARCHER_SESSION_SECRET", raising=False)
    monkeypatch.setenv("PILOT_RC_REQUIRE_RESEARCHER_AUTH", "true")

    import rc_config

    importlib.reload(rc_config)

    try:
        rc_config.validate_researcher_access_config()
    except RuntimeError as error:
        assert "Researcher access env vars" in str(error)
    else:
        raise AssertionError("researcher access validation did not fail")
