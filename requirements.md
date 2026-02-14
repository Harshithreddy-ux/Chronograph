Requirements Specification: ChronoGraph
1. Project Overview
ChronoGraph is an agentic simulation environment that helps developers learn codebases by debugging injected faults in a secure, sandboxed environment. It combines Knowledge Graph visualization with active fault injection.

2. User Stories & Acceptance Criteria (EARS Notation)
Feature: Codebase Ingestion & Visualization
Req-1.1: WHEN the user submits a valid GitHub repository URL, THE SYSTEM SHALL clone the repository into a temporary workspace.

Req-1.2: WHEN the repository is cloned, THE SYSTEM SHALL parse the source code using Tree-sitter to identify functions, classes, and their dependencies.

Req-1.3: WHEN parsing is complete, THE SYSTEM SHALL populate a Neo4j graph database with nodes representing code artifacts and edges representing calls/imports.

Req-1.4: THE SYSTEM SHALL render an interactive dependency graph on the frontend using React Flow, highlighting the relationships between files.

Feature: Simulation & Fault Injection
Req-2.1: WHEN a learning mission starts, THE SYSTEM SHALL initialize a secure E2B sandbox (microVM) isolated from the host machine.

Req-2.2: WHEN the sandbox is ready, THE SYSTEM SHALL inject a specific, pre-defined software fault (e.g., "Race Condition", "Memory Leak") into the sandboxed code.

Req-2.3: THE SYSTEM SHALL execute a load test (using k6) against the sandboxed application to trigger the fault and generate failure logs.

Req-2.4: THE SYSTEM SHALL stream real-time standard output (stdout) and error logs (stderr) from the E2B sandbox to the user interface.

Feature: Agentic Tutoring
Req-3.1: WHEN the user asks a question about the bug, THE SYSTEM SHALL query the Neo4j Knowledge Graph to retrieve the relevant semantic context (e.g., "Function A calls Function B").

Req-3.2: THE SYSTEM SHALL use a "Scaffolding" prompt pattern to provide progressive hints (Observation -> Concept -> Action) rather than revealing the solution immediately.

Req-3.3: WHEN the user submits a code fix, THE SYSTEM SHALL attempt to run the updated code in the E2B sandbox to verify if the fault is resolved.

Feature: Time-Travel Debugging (Visualization)
Req-4.1: WHEN the simulation runs, THE SYSTEM SHALL record the execution state (variable values) at discrete timestamps.

Req-4.2: WHEN the user drags the timeline slider, THE SYSTEM SHALL update the graph visualization to reflect the active function calls at that specific timestamp.