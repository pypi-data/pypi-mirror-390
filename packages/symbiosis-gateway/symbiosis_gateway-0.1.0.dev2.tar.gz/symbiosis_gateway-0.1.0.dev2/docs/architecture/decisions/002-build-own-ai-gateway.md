# ADR002 - Build our own AI gateway

- Date: 2025-11-8
- Status: Accepted

## Context

When we started thinking of the issues discussed in our [product documentation](../../product/README.md) we thought that we could find a ready-made AI gateway
to solve the challenges we faced.

After doing research into several products we found that:

- All products so far are cloud based SaaS solutions where data ownership and
  storage is unclear. The companies are very young and we'll have a hard time
  vetting them. Also, the costs of these products are substantial.

- We need an open-source product that we can self-host and control, but with
  enterprise features for better manageability. We didn't find that in the
  products we researched so far.

While not easy, we think we can produce an MVP version of an AI gateway quite fast thanks to the advances in AI coding agents.

## Decision

- We build our own AI gateway in Python so that we can build it fast.
- We use AI coding agents extensively to help us speed up the building process.

## Consequences

- We have a product that we can use without having to worry about data
  ownership, licensing costs, and other issues that come with SaaS.
- We need to maintain the project over a longer period of time.
