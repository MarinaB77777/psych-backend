from pilot_session.schemas import ParticipantSession, SessionStatus


CLOSED_STATES = {
    SessionStatus.CLOSED,
    SessionStatus.INVALIDATED,
}


def is_operationally_closed(session: ParticipantSession) -> bool:
    return session.status == SessionStatus.CLOSED


def is_invalidated(session: ParticipantSession) -> bool:
    return session.status == SessionStatus.INVALIDATED or session.invalidated


def is_research_usable(session: ParticipantSession) -> bool:
    return not is_invalidated(session)


def can_generate_export(session: ParticipantSession) -> bool:
    return (
        session.status == SessionStatus.RUN_COMPLETED
        and not is_invalidated(session)
    )
