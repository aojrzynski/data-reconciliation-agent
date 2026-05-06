# CRM Migration Fixtures

Fixtures for a Salesforce-to-Dynamics contact migration scenario.

Key mapping:
- source key: `salesforce_contact_id`
- target key: `legacy_salesforce_id`

Files:
- `source_contacts_salesforce.csv`: Salesforce-style source contacts
- `target_contacts_dynamics_clean.csv`: clean Dynamics-style migrated contacts
- `target_contacts_dynamics_issues.csv`: migration issues including key and field mismatches

Use with `config/examples/crm_contacts_mapping.yaml`.
