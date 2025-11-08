# Purpose and background

This section covers the purpose of this project and the background why we
initiated the project.

## Purpose

- Centralize access to governance-approved LLMs
- Monitor LLM interactions for security and debugging
- Manage LLM costs and budgets
- Provide guard rails for safer LLM solutions

## Background

At Info Support we're starting to see developers build their own LLM-based
applications. Right now, the access to language models is fragmented and not
very well managed. This causes issues with:

- **Cost management:** we don't know how much money we're spending on models.
  We're limiting the access to models to protect ourselves against overspending,
  while it may make more sense to help people manage their budget through a
  centralized tool.
  
- **Security:** not everybody is taking the same measures to protect their
  applications against abuse, it is important for our reputation and the safety
  of our users to support people better in this regard.

- **Monitoring:** people need to add their own monitoring solution to track
  interactions with LLMs, but this is quite hard to get right. Centralizing LLM
  monitoring will make life easier for developers while enabling monitoring for
  security and safety purposes.

- **Compliance:** people are using model providers that we haven't verified.
  This can cause problems with compliance at some clients, also we maybe leaking
  data.

## Strategic context

Initially we want to use this solution for our internal agents and agentic
systems. However, this project also has value for customers looking to take a
more professional approach to integrating LLMs in their IT landscape.

We want our AI gateway to be self-hosted and available as open-source because 
we believe that:

- Self-hosting makes us more independent from cloud vendors.
- Open-source makes it so our clients can be more independent if they have the
  skills

We looked at existing open-source products and came to the conclusion that
almost 100% of these solutions are a front for a cloud-based solution with
associated vendor lock-in. We'll use the existing products as inspiration for
this project.