# ADR003 - Use Python for the project

- Date: 2025-11-8
- Status: Accepted

## Context

While Python isn't the fastest language/runtime around we think it can add value
to the project for the following reasons:

- It's a simple language which makes programming more straightforward.
- AI Coding Agents support the language really well, so we can be sure that we
  have fewer issues controlling our coding agents during development.
- We are at a stage where we are learning how to build an AI gateway, and we
  want to focus on getting the thing working first. We'll worry about
  performance issues at a later date. We may never run into these issues because
  LLMs themselves are slow and we can horizontally scale our application.

## Decision

- We build our own AI gateway in Python so that we can build it fast.
- We use AI coding agents extensively to help us speed up the building process.

## Consequences

- We may have to redo the work, because we find that Python can't keep up with
  the performance demands. We accept this, because by then we'll have a much
  better idea how to build the project.
- We can move faster because our agent works better and we have a more pleasant
  working environment.