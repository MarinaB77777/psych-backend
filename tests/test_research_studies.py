from research import lab_store, study_store


def test_research_study_registry_creates_and_lists_separate_studies(tmp_path):
    original_file = study_store.DATA_FILE
    study_store.DATA_FILE = tmp_path / "research_studies.json"

    try:
        studies = study_store.list_research_studies()

        assert any(study["study_id"] == "health_model" for study in studies)
        assert any(
            study["study_id"] == "decision_under_uncertainty"
            for study in studies
        )

        created = study_store.create_research_study(
            title="Stress and decisions",
            description="Separate study",
            primary_research_question="How does stress relate to decisions?",
        )

        studies = study_store.list_research_studies()

        assert created["study_id"] == "stress_and_decisions"
        assert any(study["study_id"] == created["study_id"] for study in studies)
    finally:
        study_store.DATA_FILE = original_file


def test_research_objects_are_filtered_by_study_id(tmp_path):
    original_objects = lab_store.RESEARCH_OBJECTS
    original_save_objects = lab_store.save_objects
    lab_store.RESEARCH_OBJECTS = []
    lab_store.save_objects = lambda objects: None

    try:
        first = lab_store.create_research_object(
            object_type="hypothesis",
            owner="researcher",
            title="First",
            study_id="study_a",
        )
        second = lab_store.create_research_object(
            object_type="hypothesis",
            owner="researcher",
            title="Second",
            study_id="study_b",
        )

        assert first["study_id"] == "study_a"
        assert second["study_id"] == "study_b"

        study_a_objects = lab_store.list_research_objects(study_id="study_a")

        assert [item["title"] for item in study_a_objects] == ["First"]
    finally:
        lab_store.RESEARCH_OBJECTS = original_objects
        lab_store.save_objects = original_save_objects
