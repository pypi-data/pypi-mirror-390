# ADR004 - Use Architecture Decision Records

- Date: 2025-11-8
- Status: Accepted

## Context

We learned over the past year that using an agent can speed up your coding, but
only if you use it correctly. It will only get 70% right. That's why we started
looking at spec-driven development and found that this will help us beyond the
70% correct on the project.

Setting up spec-driven development is quite a lot of work that is repetitive in
nature because you're essentially building prompt templates. We came across
[Agent OS](https://buildermethods.com/agent-os) that provides a nice end-to-end
approach for spec-driven development. 

There are several other options here:

- [OpenSpec](https://github.com/Fission-AI/OpenSpec/)
- [Github Spec Kit](https://github.com/github/spec-kit)
- [BMAD](https://github.com/bmad-code-org/BMAD-METHOD)

They each have their own specific options and approach. It's hard to tell which
of these kits work best, so we'll stick to one that works well with Claude Code.

## Decision

- We choose to use [Agent OS](https://buildermethods.com/agent-os) for the
  project

## Consequences

- We can get better results out of our agents speeding up the project.
- We accept that other options work as well or better with other coding agents.
