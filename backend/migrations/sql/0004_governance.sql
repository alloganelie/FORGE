-- MS-1 : gouvernance versionnee, roles et epinglage (ET-053, ET-057 a ET-060).

CREATE TABLE role_assignments (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  user_id uuid NOT NULL REFERENCES users(id),
  role text NOT NULL CHECK (role IN ('responsible', 'user', 'auditor')),
  valid_from timestamptz NOT NULL,
  valid_to timestamptz,
  granted_by uuid REFERENCES users(id)
);

CREATE UNIQUE INDEX one_active_responsible
  ON role_assignments (workspace_id)
  WHERE role = 'responsible' AND valid_to IS NULL;

CREATE TABLE governance_artifact_versions (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  artifact_type text NOT NULL CHECK (
    artifact_type IN ('rule_pack', 'template', 'source_registry', 'control_catalog')
  ),
  artifact_key text NOT NULL,
  version integer NOT NULL CHECK (version > 0),
  content jsonb NOT NULL,
  content_hash char(64) NOT NULL CHECK (content_hash ~ '^[0-9a-f]{64}$'),
  schema_version text NOT NULL DEFAULT 'v1',
  status text NOT NULL CHECK (status IN ('draft', 'approved', 'retired')),
  effective_from timestamptz,
  approved_by_decision uuid REFERENCES decisions(id),
  created_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL,
  approved_at timestamptz,
  retired_at timestamptz,
  motif text NOT NULL DEFAULT '',
  UNIQUE (workspace_id, artifact_type, artifact_key, version),
  CHECK (status <> 'approved' OR (approved_by_decision IS NOT NULL AND effective_from IS NOT NULL)),
  CHECK (status <> 'retired' OR retired_at IS NOT NULL)
);

CREATE TABLE request_pins (
  request_id uuid NOT NULL REFERENCES requests(id),
  version_id uuid NOT NULL REFERENCES governance_artifact_versions(id),
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  pinned_by uuid NOT NULL REFERENCES users(id),
  pinned_at timestamptz NOT NULL,
  PRIMARY KEY (request_id, version_id)
);

CREATE TABLE change_proposals (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  artifact_type text NOT NULL,
  artifact_key text NOT NULL,
  base_version_id uuid REFERENCES governance_artifact_versions(id),
  content jsonb NOT NULL,
  status text NOT NULL CHECK (status IN ('open', 'accepted', 'rejected')),
  created_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL,
  decided_by uuid REFERENCES users(id),
  decided_at timestamptz
);

CREATE TABLE governance_observations (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  artifact_version_id uuid NOT NULL REFERENCES governance_artifact_versions(id),
  code text NOT NULL,
  message text NOT NULL,
  rule_id text,
  example_id text,
  created_at timestamptz NOT NULL
);

CREATE INDEX governance_versions_lookup_idx
  ON governance_artifact_versions (workspace_id, artifact_type, artifact_key, version);
CREATE INDEX governance_versions_status_idx
  ON governance_artifact_versions (workspace_id, status);
CREATE INDEX request_pins_version_idx ON request_pins (version_id);
CREATE INDEX governance_observations_version_idx
  ON governance_observations (artifact_version_id);

-- Un artefact approuve est immuable ; seule la transition approved -> retired est permise.
CREATE FUNCTION protect_governance_artifact() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.status = 'retired' THEN
    RAISE EXCEPTION 'Artefact retire immuable (GV-01)';
  END IF;
  IF OLD.status = 'approved' THEN
    IF NEW.status NOT IN ('approved', 'retired') THEN
      RAISE EXCEPTION 'Transition de statut interdite (GV-01)';
    END IF;
    IF NEW.content IS DISTINCT FROM OLD.content
       OR NEW.content_hash IS DISTINCT FROM OLD.content_hash
       OR NEW.artifact_type IS DISTINCT FROM OLD.artifact_type
       OR NEW.artifact_key IS DISTINCT FROM OLD.artifact_key
       OR NEW.version IS DISTINCT FROM OLD.version
       OR NEW.effective_from IS DISTINCT FROM OLD.effective_from
       OR NEW.approved_by_decision IS DISTINCT FROM OLD.approved_by_decision THEN
      RAISE EXCEPTION 'Contenu d''un artefact approuve immuable (GV-01, RB-067)';
    END IF;
  END IF;
  IF NEW.status = 'approved' AND OLD.status = 'draft' THEN
    IF NEW.approved_by_decision IS NULL OR NEW.effective_from IS NULL THEN
      RAISE EXCEPTION 'Approbation sans decision DH-07 ou sans date d''effet (GV-02, RB-104)';
    END IF;
    IF NEW.effective_from <= OLD.created_at THEN
      RAISE EXCEPTION 'Date d''effet retrospective interdite (RB-104)';
    END IF;
  END IF;
  IF NEW.status = 'retired' AND OLD.status <> 'approved' THEN
    RAISE EXCEPTION 'Seul un artefact approuve peut etre retire';
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER governance_artifact_protect
  BEFORE UPDATE ON governance_artifact_versions
  FOR EACH ROW EXECUTE FUNCTION protect_governance_artifact();
CREATE TRIGGER governance_artifact_no_delete
  BEFORE DELETE ON governance_artifact_versions
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER governance_artifact_no_truncate
  BEFORE TRUNCATE ON governance_artifact_versions
  FOR EACH STATEMENT EXECUTE FUNCTION forbid_mutation();

-- L'epinglage est en ajout seul : un changement est une nouvelle decision tracee.
CREATE TRIGGER request_pins_append_only
  BEFORE UPDATE OR DELETE ON request_pins
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER request_pins_no_truncate
  BEFORE TRUNCATE ON request_pins
  FOR EACH STATEMENT EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER governance_observations_append_only
  BEFORE UPDATE OR DELETE ON governance_observations
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

ALTER TABLE governance_artifact_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE governance_artifact_versions FORCE ROW LEVEL SECURITY;
ALTER TABLE request_pins ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_pins FORCE ROW LEVEL SECURITY;
ALTER TABLE change_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE change_proposals FORCE ROW LEVEL SECURITY;
ALTER TABLE governance_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE governance_observations FORCE ROW LEVEL SECURITY;

CREATE POLICY governance_versions_visibility ON governance_artifact_versions
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY request_pins_visibility ON request_pins
  USING (
    workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
    AND EXISTS (SELECT 1 FROM requests r WHERE r.id = request_id)
  );
CREATE POLICY change_proposals_visibility ON change_proposals
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY governance_observations_visibility ON governance_observations
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

GRANT SELECT, INSERT, UPDATE ON governance_artifact_versions, change_proposals TO agent_app;
GRANT SELECT, INSERT ON request_pins, governance_observations TO agent_app;
GRANT SELECT, INSERT ON role_assignments TO agent_app;
