# Research Management Layer Contract

## Purpose

This document defines the ownership, responsibilities, boundaries, lifecycle, and coordination rules for the Research Management Layer within the psychophysical research ecosystem.

The purpose of this layer is:

- coordinate research activities;
- manage research programs;
- manage research goals;
- manage research studies;
- manage research tasks;
- coordinate analytical requests;
- support publication workflows;
- support grant workflows;
- support long-term research extensibility;
- preserve research governance boundaries.

This document governs:

- Research Management responsibilities;
- research-program structure;
- research-goal lifecycle;
- research-study lifecycle;
- research-task coordination;
- research-profile integration;
- publication integration boundaries;
- grant integration boundaries;
- research extensibility principles.

This document does NOT:

- define raw data processing;
- define preprocessing;
- define Data Analysis calculations;
- define Runtime authority;
- define Governance authority;
- define participant truth;
- define medical truth;
- define psychological truth.

---

# Research Management Domain

Research Management is an independent research-management domain.

Research Management
≠
Data Preparation

Research Management
≠
Data Analysis

Research Management
≠
Publication Management

Research Management
≠
Grant Management

Research Management
≠
Governance

Research Management
≠
Runtime

Research Management coordinates research activities.

Research Management does not own source domains.

---

# Core Principle

Research Management coordinates research.

Research Management does not create truth.

Research Management does not create authority.

Research Management does not own analytical outputs.

Coordination
≠
Analysis

Coordination
≠
Authority

Coordination
≠
Truth

Analysis
≠
Authority

---

# Data Analysis Layer Separation

Data Analysis Layer
≠
Research Management Layer

Data Analysis Layer produces analytical outputs.

Research Management coordinates analytical work.

Analysis
≠
Coordination

Analytical outputs remain owned by the producing analytical domain.

Research Management does not become Data Analysis.

---

# Research Program Structure

Research activities follow:

Research Program
↓
Research Goal
↓
Research Study
↓
Research Task
↓
Analysis Request

These levels remain separated.

Research Program
≠
Research Goal

Research Goal
≠
Research Study

Research Study
≠
Research Task

Research Task
≠
Analysis Request

---

# Research Goal Boundary

Research Goal defines research intent.

Research Goal
≠
Research Finding

Research Goal
≠
Research Result

Research Goal
≠
Evidence

Research Goal does not automatically imply a valid hypothesis.

Research Goal does not automatically imply a result.

---

# Research Study Boundary

Research Study represents an organized investigation.

Research Study
≠
Research Goal

Research Study
≠
Analysis Result

Research Study
≠
Publication

Research Study may contain multiple tasks.

Research Study may contain multiple analyses.

Research Study may contain zero analyses.

---

# Research Task Boundary

Research Task represents a bounded unit of research work.

Research Task
≠
Analysis Result

Research Task
≠
Research Finding

Research Task
≠
Participant Truth

Task completion does not automatically generate findings.

Task completion
≠
Study completion

Task completion
≠
Goal completion

---

# Analysis Request Boundary

Research Management may request analysis.

Research Management may coordinate analysis.

Research Management does not fabricate analysis.

Analysis Request
≠
Analysis Result

Analysis Request
≠
Research Finding

Requested analysis
≠
completed analysis

Completed analysis
≠
validated finding

---

# Research Management Result Boundary

Research Management may organize findings.

Research Management may organize reports.

Research Management may organize research outputs.

Research Management does not create findings.

Research Management does not validate findings.

Research Management does not invalidate findings.

Research Management does not own findings.

Research Management Output
≠
Analysis Result

Research Management Output
≠
Research Truth

Research Management Output
≠
Scientific Validation

---

# Research Profile Integration

Research Management may use bounded research profiles.

Examples include:

- Student;
- Professor / Researcher;
- Academic / Analytical;
- Future Research Roles.

Profiles provide workflow context.

Profiles do not provide authority.

Profile
≠
Identity

Profile
≠
Authority

Profile
≠
Research Finding

Profile
≠
Participant Data

Profile
≠
Research Dataset

## Profile Access

Profile Access
=
Read Only

Profile-based routing
≠
Research Conclusion

---

# Session And Consent Boundary

Session collection rules are governed by:

Session Collection and Agreement Contract.

Research Management does not override collection governance.

Research Management does not create collection permissions.

Research Goal
≠
Data Collection Permission

Profile Access
≠
Data Collection Permission

Research participation remains consent-aware.

---

# Publication Integration Boundary

Research Management may coordinate publication activities.

Research Management does not become Publication Management.

Publication
≠
Research Truth

Publication
≠
Ground Truth

Publication
≠
Validation

Publication
≠
Validation Result

Publication Acceptance
≠
Scientific Validation

Publication Rejection
≠
Scientific Refutation

Publication status does not determine scientific truth.

---

# Grant Integration Boundary

Research Management may coordinate grant activities.

Research Management does not become Grant Management.

Grant Approval
≠
Scientific Validation

Funding
≠
Evidence

Grant Success
≠
Research Truth

Funding Priority
≠
Research Priority

Funded Topic
≠
Most Important Topic

Grant status does not determine scientific validity.

---

# Meta-Research Boundary

Research programs may investigate:

- method comparison;
- method evaluation;
- measurement quality;
- predictive usefulness;
- calibration strategies;
- contextual suitability;
- validation strategies;
- research methodology.

Method Comparison
≠
Ground Truth

Method Preference
≠
Method Superiority

Best In Context
≠
Universal Best Method

No Best Method Found
=
Valid Research Outcome

No Superior Method Found
=
Valid Research Outcome

Method evaluation remains uncertainty-aware.

Method Evaluation
≠
Method Validation

Method Validation
≠
Ground Truth

---

# Research Lifecycle

Research entities may have lifecycle states:

- PROPOSED
- ACTIVE
- PAUSED
- COMPLETED
- ARCHIVED
- INVALIDATED

Lifecycle states remain distinct.

---

# Research OS Boundary Addendum

## Research OS Position

The Research Management Layer belongs to the Research OS ecosystem, but it is
not the Research OS Core. It coordinates research work inside Projects. Research
OS coordinates scientific infrastructure and keeps the boundaries between
projects, studies, tasks, evidence, validation and knowledge explicit.

## Project Boundary

The project hierarchy is:

Project -> Research Program -> Research Goal -> Research Study -> Research Task
-> Analysis Request.

A Project is not the same entity as a Research Program. Research Management must
not collapse these levels or create duplicate entities when a lower-level
research task can be represented by a stable reference inside the existing
project hierarchy.

## Asset Boundary

Research Management may reference Assets. It does not own Assets. An Asset is
not a Research Task and not a Research Goal.

## Experiment Boundary

A Research Study may organize Experiments. Experiments produce observations.
Research Management coordinates experiments, but it does not perform
experiments and does not replace the experimental layer.

## Validation Boundary

Research Management may coordinate validation work, but it does not validate
evidence. Validation is separate from Management.

## Knowledge Boundary

Knowledge is not a Research Management output. Research Management organizes
work and traceability; it does not create scientific knowledge by itself.

## AI Boundary

AI assistance is not Research Management authority. AI planning is not
scientific planning approval. AI coordination is not scientific responsibility.

## Human Scientific Responsibility

Researchers remain scientifically responsible for priorities, study design,
interpretation, validation and publication decisions.

## Human Priority Authority

Research priorities remain human decisions. The platform may help expose
conflicts, missing links and next actions, but it must not silently reorder
scientific priorities.

## Traceability

Every coordination artifact must remain traceable to the Project, Study, Task,
Analysis and Evidence it references.
