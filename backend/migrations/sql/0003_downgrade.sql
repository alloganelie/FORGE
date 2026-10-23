-- Retour arriere du schema de fondation (developpement uniquement).
DROP TABLE IF EXISTS chain_checkpoints, command_results, step_runs, decisions,
  content_atoms, documents, control_results, control_runs, ledger_events,
  state_changes, elements, deliverable_versions, deliverables, requests, users,
  workspaces CASCADE;

DROP FUNCTION IF EXISTS check_version_finalized() CASCADE;
DROP FUNCTION IF EXISTS check_request_finalized() CASCADE;
DROP FUNCTION IF EXISTS protect_finalized_request() CASCADE;
DROP FUNCTION IF EXISTS protect_state_columns() CASCADE;
DROP FUNCTION IF EXISTS check_ledger_chain() CASCADE;
DROP FUNCTION IF EXISTS protect_elements() CASCADE;
DROP FUNCTION IF EXISTS protect_atoms() CASCADE;
DROP FUNCTION IF EXISTS protect_finalized_version() CASCADE;
DROP FUNCTION IF EXISTS forbid_mutation() CASCADE;

DROP TYPE IF EXISTS st_request, st_conformity, st_approval, st_diffusion,
  st_version, st_element, qi_status, lc_status, atom_origin, control_outcome,
  anomaly_class, decision_type, auth_level CASCADE;
