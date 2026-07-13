# State Output And Explanation Principle

This principle defines how a State Snapshot can be transformed into
human-readable output without turning description into authority.

## Output Layers

State output may contain:

- State Summary;
- Explanation Layer;
- Confidence Layer;
- Bottleneck Layer;
- Risk Layer;
- Resource Overdraft Layer;
- Unknown Layer.

## Explanation Boundary

The explanation layer describes why the current snapshot looks the way it does.
It must preserve uncertainty and provenance. It must not present model text as a
medical conclusion, diagnosis, validated scientific fact or behavioral command.

## Bottleneck Boundary

Bottleneck != Worst Score.

A bottleneck is the current limiting factor in the snapshot. It is a contextual
description, not an identity label and not a final explanation.

## Risk Boundary

The risk layer does not provide recommendations. It may describe what becomes
more likely if the observed pattern continues, while preserving that risk is
conditional and uncertainty-aware.

## Resource Overdraft Boundary

Resource overdraft describes a pattern where current load appears to exceed
available or recoverable resources. It is not a diagnosis and not a personal
verdict.

## Unknown Layer

The Unknown Layer must explicitly represent missing or insufficient information,
including:

- missing priority structure;
- missing or uncertain sensor calibration;
- missing domain coverage;
- insufficient temporal coverage;
- unresolved contradiction between sources.

Unknowns must not be silently filled by the model.

