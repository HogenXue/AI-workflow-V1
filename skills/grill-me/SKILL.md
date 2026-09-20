---
name: grill-me
description: Align on a loose idea through a user-invoked, stateless conversation before committing to a plan or implementation.
disable-model-invocation: true
---

# Grill Me

This is an explicit user entrypoint. Do not invoke it automatically. Use it when the user has an idea worth taking seriously but has not yet worked out what it involves. If the idea is already precise, grilling is unnecessary.

The session is stateless: do not write files, update tasks, create specs, implement code, run tests, commit, push, or publish while grilling. In a Trellis project, read existing facts as context but leave persistence and task state to Trellis after the session.

## Conversation method

Map the idea as a decision tree. Work in rounds. Each round contains the current frontier: every decision whose prerequisites are already settled. Number each question and give a recommended answer with the main trade-off. Do not ask a question whose answer depends on another unresolved question in the same round. If the user requests it, ask one question at a time.

Finding facts is the agent's job. Use available project files and tools rather than asking the user for discoverable information. The user owns the scope and decisions: recommendations are proposals, not confirmation. Welcome disagreement and accept `I don't know` as a real answer.

Do not let the session drift into passive agreement or endless questioning. Some questions cannot be answered by talking, especially interaction feel, layout, or competing shapes that need something concrete to react to. Mark those as requiring a bounded prototype or research step and stop that branch; do not start the work without authorization.

Finish when the frontier is empty or all remaining branches require external evidence. Summarize the choices the user actually made, the resulting acceptance criteria, and remaining blockers. Ask once whether the summary matches the shared understanding, then return control to the user's normal workflow.
