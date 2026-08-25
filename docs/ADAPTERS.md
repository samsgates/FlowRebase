# Adapter Model

FlowRebase separates source parsing from target compilation.

## Source adapter

A source adapter receives source content and metadata and returns a validated `UAMProcess`.

## Target adapter

A target adapter receives only UAM and produces a candidate artifact plus warnings. Environment binding, secrets, platform connection references and deployment are separate responsibilities.

## Why this matters

For N source technologies and M targets, direct pairwise conversion trends toward N×M converter logic. UAM reduces the architecture toward N parsers + M compilers and provides one place for verification, policy and governance.
