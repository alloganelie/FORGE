-- Retour arriere MS-1 (developpement uniquement).
DROP TABLE IF EXISTS governance_observations, change_proposals, request_pins,
  governance_artifact_versions, role_assignments CASCADE;
DROP FUNCTION IF EXISTS protect_governance_artifact() CASCADE;
