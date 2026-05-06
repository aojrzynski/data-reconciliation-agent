# Sample Data

This folder contains deterministic fixture datasets for realistic source-to-target reconciliation scenarios.

Purpose:
- provide practical migration-style examples for development and testing
- support deterministic checks as the project source of truth
- give future milestones stable inputs for repeatable test coverage

Subfolders:
- `customers/`: customer profile migration fixtures with clean and issue variants
- `orders/`: order migration fixtures including tolerance and formatting edge cases
- `crm_migration/`: Salesforce-to-Dynamics contact migration fixtures with cross-system key mapping

See `docs/sample_scenarios.md` for expected high-level outcomes.
