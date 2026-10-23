-- MS-0 : schema de fondation (ET-013, ET-015, ET-018, ET-019, ET-021, ET-022,
-- ET-027, ET-029, ET-036, ET-038, ET-045, ET-046).
-- Aucune donnee metier reelle. Les identifiants sont des UUIDv7 fournis par l'application.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agent_app') THEN
    CREATE ROLE agent_app NOLOGIN;
  END IF;
END $$;

CREATE TABLE workspaces (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE users (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  display_name text NOT NULL,
  role text NOT NULL CHECK (role IN ('user', 'responsible', 'auditor', 'system')),
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL
);

CREATE TABLE requests (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  author_id uuid NOT NULL REFERENCES users(id),
  original_text text NOT NULL,
  deliverable_type text,
  state st_request NOT NULL DEFAULT 'received',
  has_blocked_elements boolean NOT NULL DEFAULT false,
  suspended_from st_request,
  waiting_origin st_request,
  linked_to uuid REFERENCES requests(id),
  created_at timestamptz NOT NULL,
  row_version integer NOT NULL DEFAULT 0,
  CONSTRAINT finalized_not_suspended CHECK (state <> 'finalized' OR suspended_from IS NULL),
  CONSTRAINT suspended_has_origin CHECK (state <> 'suspended' OR suspended_from IS NOT NULL),
  CONSTRAINT blocked_has_origin CHECK (state NOT IN ('blocked', 'awaiting_decision') OR waiting_origin IS NOT NULL)
);

CREATE TABLE deliverables (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  type_key text NOT NULL,
  target_format text NOT NULL
);

CREATE TABLE deliverable_versions (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  deliverable_id uuid NOT NULL REFERENCES deliverables(id),
  number integer NOT NULL CHECK (number > 0),
  st_v st_version NOT NULL DEFAULT 'provisional',
  st_c st_conformity NOT NULL DEFAULT 'not_evaluated',
  st_a st_approval NOT NULL DEFAULT 'not_submitted',
  st_d st_diffusion NOT NULL DEFAULT 'not_authorized',
  supersedes uuid REFERENCES deliverable_versions(id),
  finalized_at timestamptz,
  seal_id uuid,
  row_version integer NOT NULL DEFAULT 0,
  UNIQUE (deliverable_id, number),
  CONSTRAINT finalized_requires_conforming
    CHECK (st_v NOT IN ('finalized', 'superseded') OR st_c = 'conforming'),
  CONSTRAINT approval_requires_finalized
    CHECK (st_a IN ('not_submitted', 'not_required') OR st_v IN ('finalized', 'superseded')),
  CONSTRAINT diffusion_requires_finalized_and_approved
    CHECK (st_d = 'not_authorized'
           OR (st_v IN ('finalized', 'superseded') AND st_a IN ('approved', 'not_required'))),
  CONSTRAINT abandoned_is_not_diffused
    CHECK (st_v <> 'abandoned' OR (st_d = 'not_authorized' AND st_a = 'not_submitted')),
  CONSTRAINT finalized_has_timestamp
    CHECK (st_v <> 'finalized' OR finalized_at IS NOT NULL)
);

CREATE TABLE elements (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  version_id uuid NOT NULL REFERENCES deliverable_versions(id),
  element_key text NOT NULL,
  mandatory boolean NOT NULL,
  st_e st_element NOT NULL DEFAULT 'to_produce',
  UNIQUE (version_id, element_key)
);

CREATE TABLE state_changes (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  entity_type text NOT NULL,
  entity_id uuid NOT NULL,
  axis char(1) NOT NULL CHECK (axis IN ('R', 'C', 'A', 'D', 'V', 'E')),
  from_state text,
  to_state text NOT NULL,
  transition_id text NOT NULL,
  actor_type text NOT NULL CHECK (actor_type IN ('human', 'agent', 'system')),
  actor_id uuid,
  reason_internal text,
  reason_communicable text,
  at timestamptz NOT NULL,
  ledger_seq bigint NOT NULL
);

CREATE TABLE ledger_events (
  seq bigserial PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid REFERENCES requests(id),
  request_seq integer,
  event_type text NOT NULL,
  payload jsonb NOT NULL,
  actor_type text NOT NULL CHECK (actor_type IN ('human', 'agent', 'system')),
  actor_id uuid,
  at timestamptz NOT NULL,
  prev_hash char(64) NOT NULL CHECK (prev_hash ~ '^[0-9a-f]{64}$'),
  self_hash char(64) NOT NULL CHECK (self_hash ~ '^[0-9a-f]{64}$'),
  UNIQUE (request_id, request_seq),
  CHECK (request_seq IS NULL OR request_seq > 0)
);

CREATE TABLE control_runs (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  version_id uuid NOT NULL REFERENCES deliverable_versions(id),
  catalog_version_id uuid NOT NULL,
  started_at timestamptz NOT NULL,
  trigger text NOT NULL
);

CREATE TABLE control_results (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  run_id uuid NOT NULL REFERENCES control_runs(id),
  control_id text NOT NULL,
  outcome control_outcome NOT NULL,
  examined jsonb NOT NULL,
  rule_ref text,
  at timestamptz NOT NULL,
  mandatory boolean NOT NULL,
  detail_internal jsonb
);

CREATE TABLE documents (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid REFERENCES requests(id),
  sha256 char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
  storage_ref text NOT NULL,
  media_type text NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE content_atoms (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  version_id uuid NOT NULL REFERENCES deliverable_versions(id),
  element_key text NOT NULL,
  origin atom_origin NOT NULL,
  text text NOT NULL,
  evidence_id uuid,
  created_at timestamptz NOT NULL
);

CREATE TABLE decisions (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid REFERENCES requests(id),
  type decision_type NOT NULL,
  object_type text NOT NULL,
  object_id uuid,
  decider_id uuid NOT NULL REFERENCES users(id),
  outcome text NOT NULL,
  reason text,
  scope jsonb NOT NULL,
  decided_at timestamptz NOT NULL
);

CREATE TABLE step_runs (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  step text NOT NULL,
  input_hash char(64) NOT NULL CHECK (input_hash ~ '^[0-9a-f]{64}$'),
  status text NOT NULL CHECK (status IN ('pending', 'running', 'succeeded', 'failed', 'invalidated')),
  attempt integer NOT NULL DEFAULT 0 CHECK (attempt >= 0),
  started_at timestamptz,
  finished_at timestamptz,
  error jsonb,
  UNIQUE (request_id, step, input_hash)
);

CREATE TABLE command_results (
  idempotency_key text PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid REFERENCES requests(id),
  result jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL
);

CREATE TABLE chain_checkpoints (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  checked_at timestamptz NOT NULL,
  first_seq bigint,
  last_seq bigint,
  ok boolean NOT NULL,
  detail jsonb
);

CREATE INDEX requests_workspace_state_idx ON requests (workspace_id, state);
CREATE INDEX requests_author_idx ON requests (author_id);
CREATE INDEX versions_deliverable_idx ON deliverable_versions (deliverable_id, number);
CREATE INDEX elements_version_idx ON elements (version_id);
CREATE INDEX state_changes_entity_idx ON state_changes (entity_type, entity_id, at);
CREATE INDEX ledger_events_request_idx ON ledger_events (request_id, request_seq);
CREATE INDEX ledger_events_workspace_idx ON ledger_events (workspace_id, seq);
CREATE INDEX step_runs_request_idx ON step_runs (request_id, status);
CREATE INDEX command_results_expiry_idx ON command_results (expires_at);

-- 1) Tables strictement en ajout seul (ET-021, ET-027, RT-062).
CREATE FUNCTION forbid_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'Table % en ajout seul : % interdit', TG_TABLE_NAME, TG_OP;
END $$;

CREATE TRIGGER ledger_append_only BEFORE UPDATE OR DELETE ON ledger_events
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER ledger_no_truncate BEFORE TRUNCATE ON ledger_events
  FOR EACH STATEMENT EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER control_results_append_only BEFORE UPDATE OR DELETE ON control_results
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER control_results_no_truncate BEFORE TRUNCATE ON control_results
  FOR EACH STATEMENT EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER documents_immutable BEFORE UPDATE OR DELETE ON documents
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER state_changes_append_only BEFORE UPDATE OR DELETE ON state_changes
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER decisions_immutable BEFORE UPDATE OR DELETE ON decisions
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

-- 2) Versions finalisees : seuls A, D et Finalisee -> Remplacee sont modifiables (RB-067).
CREATE FUNCTION protect_finalized_version() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.st_v IN ('finalized', 'superseded') THEN
    IF NEW.deliverable_id IS DISTINCT FROM OLD.deliverable_id
       OR NEW.number IS DISTINCT FROM OLD.number
       OR NEW.st_c IS DISTINCT FROM OLD.st_c
       OR NEW.finalized_at IS DISTINCT FROM OLD.finalized_at
       OR NEW.seal_id IS DISTINCT FROM OLD.seal_id THEN
      RAISE EXCEPTION 'Version finalisee immuable (RB-067)';
    END IF;
    IF NEW.st_v IS DISTINCT FROM OLD.st_v
       AND NOT (OLD.st_v = 'finalized' AND NEW.st_v = 'superseded') THEN
      RAISE EXCEPTION 'Transition de version interdite';
    END IF;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER finalized_protect BEFORE UPDATE ON deliverable_versions
  FOR EACH ROW EXECUTE FUNCTION protect_finalized_version();

-- 3) Contenu d'une version finalisee : atomes et elements immuables (ET-028).
CREATE FUNCTION protect_atoms() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  version_state st_version;
  target_version uuid;
BEGIN
  target_version := COALESCE(NEW.version_id, OLD.version_id);
  SELECT st_v INTO version_state FROM deliverable_versions WHERE id = target_version;
  IF version_state IN ('finalized', 'superseded') THEN
    RAISE EXCEPTION 'Contenu d''une version finalisee immuable';
  END IF;
  RETURN COALESCE(NEW, OLD);
END $$;

CREATE TRIGGER atoms_protect BEFORE UPDATE OR DELETE ON content_atoms
  FOR EACH ROW EXECUTE FUNCTION protect_atoms();

CREATE FUNCTION protect_elements() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  version_state st_version;
  target_version uuid;
BEGIN
  target_version := COALESCE(NEW.version_id, OLD.version_id);
  SELECT st_v INTO version_state FROM deliverable_versions WHERE id = target_version;
  IF version_state IN ('finalized', 'superseded') THEN
    RAISE EXCEPTION 'Elements d''une version finalisee immuables';
  END IF;
  RETURN COALESCE(NEW, OLD);
END $$;

CREATE TRIGGER elements_protect BEFORE UPDATE OR DELETE ON elements
  FOR EACH ROW EXECUTE FUNCTION protect_elements();

-- 4) Continuite de la chaine du journal (ET-022, ET-026).
CREATE FUNCTION check_ledger_chain() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  last_hash char(64);
  last_seq integer;
BEGIN
  IF NEW.request_id IS NULL THEN
    RETURN NEW;
  END IF;
  SELECT self_hash, request_seq INTO last_hash, last_seq
    FROM ledger_events
   WHERE request_id = NEW.request_id
   ORDER BY request_seq DESC
   LIMIT 1;
  IF last_seq IS NULL THEN
    IF NEW.request_seq <> 1 OR NEW.prev_hash <> repeat('0', 64) THEN
      RAISE EXCEPTION 'Chaine invalide (debut)';
    END IF;
  ELSIF NEW.request_seq <> last_seq + 1 OR NEW.prev_hash <> last_hash THEN
    RAISE EXCEPTION 'Chaine invalide (continuite)';
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER ledger_chain BEFORE INSERT ON ledger_events
  FOR EACH ROW EXECUTE FUNCTION check_ledger_chain();

-- 5) Aucune ecriture d'etat hors du moteur lifecycle (DR-03, ET-036).
CREATE FUNCTION protect_state_columns() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF COALESCE(NULLIF(current_setting('app.transition_id', true), ''), NULL) IS NOT NULL THEN
    RETURN NEW;
  END IF;
  IF TG_TABLE_NAME = 'requests' THEN
    IF NEW.state IS DISTINCT FROM OLD.state THEN
      RAISE EXCEPTION 'Etat de demande modifie hors moteur de transitions';
    END IF;
  ELSIF TG_TABLE_NAME = 'deliverable_versions' THEN
    IF NEW.st_v IS DISTINCT FROM OLD.st_v
       OR NEW.st_c IS DISTINCT FROM OLD.st_c
       OR NEW.st_a IS DISTINCT FROM OLD.st_a
       OR NEW.st_d IS DISTINCT FROM OLD.st_d THEN
      RAISE EXCEPTION 'Etat de version modifie hors moteur de transitions';
    END IF;
  ELSIF TG_TABLE_NAME = 'elements' THEN
    IF NEW.st_e IS DISTINCT FROM OLD.st_e THEN
      RAISE EXCEPTION 'Etat d''element modifie hors moteur de transitions';
    END IF;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER requests_state_guard BEFORE UPDATE ON requests
  FOR EACH ROW EXECUTE FUNCTION protect_state_columns();
CREATE TRIGGER versions_state_guard BEFORE UPDATE ON deliverable_versions
  FOR EACH ROW EXECUTE FUNCTION protect_state_columns();
CREATE TRIGGER elements_state_guard BEFORE UPDATE ON elements
  FOR EACH ROW EXECUTE FUNCTION protect_state_columns();

-- 6) Etats finaux figes (IV-04) et finalisation coherente (IV-05, IV-13).
CREATE FUNCTION protect_finalized_request() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.state IN ('finalized', 'cancelled') AND NEW.state IS DISTINCT FROM OLD.state THEN
    RAISE EXCEPTION 'Demande finalisee ou annulee : etat fige (IV-04)';
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER request_final_protect BEFORE UPDATE ON requests
  FOR EACH ROW EXECUTE FUNCTION protect_finalized_request();

CREATE FUNCTION check_request_finalized() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.state = 'finalized' AND OLD.state IS DISTINCT FROM 'finalized' THEN
    IF NOT EXISTS (
      SELECT 1
        FROM deliverables d
        JOIN deliverable_versions v ON v.deliverable_id = d.id
       WHERE d.request_id = NEW.id
         AND v.st_c = 'conforming'
         AND v.st_v IN ('finalized', 'superseded')
    ) THEN
      RAISE EXCEPTION 'Finalisation sans version conforme (IV-05)';
    END IF;
    IF EXISTS (
      SELECT 1
        FROM deliverables d
        JOIN deliverable_versions v ON v.deliverable_id = d.id
        JOIN elements e ON e.version_id = v.id
       WHERE d.request_id = NEW.id
         AND e.mandatory
         AND e.st_e NOT IN ('controlled_ok', 'not_applicable')
    ) THEN
      RAISE EXCEPTION 'Finalisation avec elements obligatoires non conformes (IV-13)';
    END IF;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER request_finalization_check BEFORE UPDATE ON requests
  FOR EACH ROW EXECUTE FUNCTION check_request_finalized();

CREATE FUNCTION check_version_finalized() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.st_v = 'finalized' AND OLD.st_v IS DISTINCT FROM 'finalized' THEN
    IF EXISTS (
      SELECT 1 FROM elements
       WHERE version_id = NEW.id
         AND mandatory
         AND st_e NOT IN ('controlled_ok', 'not_applicable')
    ) THEN
      RAISE EXCEPTION 'Finalisation avec elements obligatoires non conformes (IV-13)';
    END IF;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER version_finalization_check BEFORE UPDATE ON deliverable_versions
  FOR EACH ROW EXECUTE FUNCTION check_version_finalized();

-- 7) Securite au niveau des lignes : activee et forcee (ET-029).
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests FORCE ROW LEVEL SECURITY;
ALTER TABLE deliverables ENABLE ROW LEVEL SECURITY;
ALTER TABLE deliverables FORCE ROW LEVEL SECURITY;
ALTER TABLE deliverable_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE deliverable_versions FORCE ROW LEVEL SECURITY;
ALTER TABLE elements ENABLE ROW LEVEL SECURITY;
ALTER TABLE elements FORCE ROW LEVEL SECURITY;
ALTER TABLE state_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE state_changes FORCE ROW LEVEL SECURITY;
ALTER TABLE ledger_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_events FORCE ROW LEVEL SECURITY;
ALTER TABLE control_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_results FORCE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
ALTER TABLE content_atoms ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_atoms FORCE ROW LEVEL SECURITY;
ALTER TABLE step_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE step_runs FORCE ROW LEVEL SECURITY;

CREATE POLICY requests_visibility ON requests
  USING (
    workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
    AND (
      current_setting('app.role', true) IN ('responsible', 'system', 'auditor')
      OR author_id = NULLIF(current_setting('app.user_id', true), '')::uuid
    )
  );

CREATE POLICY deliverables_visibility ON deliverables
  USING (
    workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
    AND EXISTS (SELECT 1 FROM requests r WHERE r.id = request_id)
  );

CREATE POLICY versions_visibility ON deliverable_versions
  USING (
    workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
    AND EXISTS (SELECT 1 FROM deliverables d WHERE d.id = deliverable_id)
  );

CREATE POLICY elements_visibility ON elements
  USING (
    workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
    AND EXISTS (SELECT 1 FROM deliverable_versions v WHERE v.id = version_id)
  );

CREATE POLICY state_changes_visibility ON state_changes
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

CREATE POLICY ledger_events_visibility ON ledger_events
  USING (
    workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
    AND (request_id IS NULL OR EXISTS (SELECT 1 FROM requests r WHERE r.id = request_id))
  );

CREATE POLICY control_results_visibility ON control_results
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

CREATE POLICY documents_visibility ON documents
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

CREATE POLICY content_atoms_visibility ON content_atoms
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

CREATE POLICY step_runs_visibility ON step_runs
  USING (
    workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
    AND EXISTS (SELECT 1 FROM requests r WHERE r.id = request_id)
  );

-- 8) Privileges du role applicatif : jamais proprietaire, jamais DELETE (ET-019, ET-029).
GRANT USAGE ON SCHEMA public TO agent_app;
GRANT SELECT, INSERT, UPDATE ON workspaces, users, requests, deliverables,
  deliverable_versions, elements, control_runs, content_atoms, step_runs,
  command_results, chain_checkpoints TO agent_app;
GRANT SELECT, INSERT ON ledger_events, state_changes, control_results, documents, decisions TO agent_app;
GRANT USAGE, SELECT ON SEQUENCE ledger_events_seq_seq TO agent_app;