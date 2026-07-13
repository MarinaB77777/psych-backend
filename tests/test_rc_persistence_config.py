import importlib


def test_data_root_routes_rc_stores_to_configured_root(tmp_path, monkeypatch):
    monkeypatch.setenv("PILOT_RC_DATA_ROOT", str(tmp_path))

    import rc_config
    import research.records_store as records_store
    import research.analysis_store as analysis_store
    import research.analysis_runner as analysis_runner

    importlib.reload(rc_config)
    importlib.reload(records_store)
    importlib.reload(analysis_store)
    importlib.reload(analysis_runner)

    assert records_store.RESEARCH_RECORDS_PATH == (
        tmp_path / "research_snapshots" / "research_records.json"
    )
    assert analysis_store.ANALYSIS_INDEX_PATH == (
        tmp_path / "derived" / "analysis" / "research_analysis_results.json"
    )
    assert analysis_runner.PILOT_SESSIONS_PATH == (
        tmp_path / "primary" / "pilot_sessions.json"
    )


def test_restart_persistence_with_configured_data_root(tmp_path, monkeypatch):
    monkeypatch.setenv("PILOT_RC_DATA_ROOT", str(tmp_path))

    import rc_config
    import main

    importlib.reload(rc_config)
    app_module = importlib.reload(main)

    account = app_module.account_service.create_account(
        preferred_language="ru"
    )
    first = app_module.session_start_flow.start_session_after_agreement(
        account_id=account.account_id,
        consent_record={
            "consent_status": "granted",
            "consent_version": "consent-policy-1",
            "consent_scope": ["pilot_participation"],
            "granted_at": "2026-07-12T00:00:00+00:00",
        },
        study_id="health_model",
    )["session"]
    app_module.pilot_service.submit_answers(
        first.session_id,
        {"d0": 1},
    )

    app_module = importlib.reload(main)
    reloaded_first = app_module.pilot_service.get_session(first.session_id)
    assert reloaded_first is not None
    assert reloaded_first.participant_id == account.participant_id
    assert reloaded_first.answers == {"d0": 1}

    second = app_module.session_start_flow.start_session_after_agreement(
        account_id=account.account_id,
        consent_record={
            "consent_status": "granted",
            "consent_version": "consent-policy-1",
            "consent_scope": ["pilot_participation"],
            "granted_at": "2026-07-12T01:00:00+00:00",
        },
        study_id="health_model",
    )["session"]
    app_module.pilot_service.invalidate_session(
        second.session_id,
        "test invalidation is retained",
    )

    app_module = importlib.reload(main)
    sessions = app_module.store.list_all()
    participant_sessions = [
        session for session in sessions
        if session.participant_id == account.participant_id
    ]

    assert {session.session_id for session in participant_sessions} == {
        first.session_id,
        second.session_id,
    }
    assert len({session.participant_id for session in participant_sessions}) == 1
    assert app_module.pilot_service.get_session(second.session_id).invalidated is True


def test_production_requires_explicit_data_root(monkeypatch):
    monkeypatch.delenv("PILOT_RC_DATA_ROOT", raising=False)
    monkeypatch.setenv("PILOT_RC_REQUIRE_PERSISTENT_DATA_ROOT", "true")

    import rc_config

    importlib.reload(rc_config)

    try:
        rc_config.validate_persistent_data_root()
    except RuntimeError as error:
        assert "PILOT_RC_DATA_ROOT" in str(error)
    else:
        raise AssertionError("production persistence validation did not fail")
