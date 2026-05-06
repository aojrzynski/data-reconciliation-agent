# Extending the Project

When extending this project:

- keep deterministic checks explicit
- avoid framework-heavy abstractions
- preserve CLI-first and local-first behavior
- add tests for each new check or comparator
- update docs when behavior or assumptions change

If a proposed feature weakens auditability, reconsider the design.
