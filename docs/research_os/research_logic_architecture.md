# Research Logic Architecture v1

This is a working architecture agreement for questionnaires, research sessions
and game-linked research questions. It is not automatic truth and must not
silently change runtime behavior without explicit implementation review.

## Purpose

Research Logic answers: why are we asking these questions?

It sits between Question Bank, Questionnaire Session, Answers, Engine and Public
Output:

Question Bank -> Research Logic -> Questionnaire Session -> Answers -> Engine
-> Public Output.

After calculation, Engine may request Clarification Logic for additional
questions:

Engine -> Clarification Logic -> Additional Questions.

## Research Is Defined By Goal

Research is defined by a goal, not by question count, block count, bank
membership or time spent. Completion is determined by the research goal and
completion criteria.

## Question Identity

Question texts live separately from logic and localization. Research Logic must
refer to stable question identity. For new work, stable `question_uuid` is the
primary link. Existing `question_code` may remain as compatibility metadata, but
bank membership must not be used as the authority for whether a question can be
used in a questionnaire or game.

Questions from any bank may be used in any questionnaire or game when they are
linked by stable UUID and the research logic allows that use.

Internal IDs, enum values, API fields and research codes are not localized.

## Research Logic Fields

A research logic definition may contain:

- goal;
- research question references;
- question sequence;
- completion criteria;
- clarification permission;
- required outputs;
- provenance requirements;
- version.

It must not contain user-facing question text.

## Clarification Logic

Research Logic and Clarification Logic are separate:

- Research Logic defines what the study wants to learn.
- Clarification Logic asks why data do not fit, are missing or contradict.

Clarification questions do not belong to one research logic and may appear
wherever the engine identifies insufficient or contradictory information.

## Pilot v1 Logics

The first Pilot v1 research logics are:

1. Intro: understand who the person is, what they do, what matters to them and
   why they came. Mostly free text. Clarifications are allowed.
2. Resource depletion: evaluate resources and build a resource profile for
   state, prognosis, stability and decision support.
3. Decision making: evaluate noticing options, updating decisions, fixing
   errors, adapting to new information and uncertainty.

## Game Boundary

Games may answer predefined research questions through stable question UUIDs.
Games provide events and prepared signal bundles. A game must not interpret
answers, assign diagnoses, become truth authority or directly modify Health
Model runtime scores.

