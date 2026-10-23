-- MS-2 : demande, clarification, faisabilite, passerelle LLM et suivi.

ALTER TABLE requests ADD COLUMN target_format text;
ALTER TABLE requests ADD COLUMN diagnostic_only boolean NOT NULL DEFAULT false;

CREATE TABLE request_analyses (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE request_parameters (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  name text NOT NULL,
  value text NOT NULL,
  justification_quote text NOT NULL,
  source text NOT NULL DEFAULT 'user',
  quality_status qi_status NOT NULL DEFAULT 'candidate',
  created_at timestamptz NOT NULL,
  UNIQUE (request_id, name)
);

CREATE TABLE clarifications (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  parameter text NOT NULL,
  question_text text NOT NULL,
  why_needed text NOT NULL,
  blocking boolean NOT NULL,
  status text NOT NULL CHECK (status IN ('open', 'answered')),
  answer text,
  created_at timestamptz NOT NULL,
  answered_at timestamptz
);

CREATE TABLE conversation_messages (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  role text NOT NULL CHECK (role IN ('user', 'agent', 'system')),
  template_key text NOT NULL,
  text text NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE feasibility_reports (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  payload jsonb NOT NULL,
  outcome text NOT NULL CHECK (outcome IN ('realizable', 'to_clarify', 'blocked', 'suspended')),
  created_at timestamptz NOT NULL
);

CREATE TABLE llm_calls (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid REFERENCES requests(id),
  task_id text NOT NULL,
  prompt_version text NOT NULL,
  model text NOT NULL,
  provider text NOT NULL,
  input_sha256 char(64) NOT NULL CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
  output_sha256 char(64) CHECK (output_sha256 IS NULL OR output_sha256 ~ '^[0-9a-f]{64}$'),
  input_ref text,
  output_ref text,
  tokens_in integer,
  tokens_out integer,
  cost_micro_eur bigint,
  latency_ms integer,
  stop_reason text NOT NULL,
  validation_outcome text NOT NULL,
  at timestamptz NOT NULL
);

CREATE TABLE split_proposals (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  author_id uuid NOT NULL REFERENCES users(id),
  original_text text NOT NULL,
  parts jsonb NOT NULL,
  status text NOT NULL CHECK (status IN ('proposed', 'confirmed')),
  created_at timestamptz NOT NULL
);

CREATE TABLE request_items (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  request_id uuid NOT NULL REFERENCES requests(id),
  item_key text NOT NULL,
  label text NOT NULL,
  state text NOT NULL,
  created_at timestamptz NOT NULL,
  UNIQUE (request_id, item_key)
);

CREATE INDEX request_analyses_request_idx ON request_analyses (request_id);
CREATE INDEX clarifications_request_idx ON clarifications (request_id, status);
CREATE INDEX conversation_request_idx ON conversation_messages (request_id, created_at);
CREATE INDEX feasibility_request_idx ON feasibility_reports (request_id, created_at);
CREATE INDEX llm_calls_request_idx ON llm_calls (request_id, at);
CREATE INDEX request_items_request_idx ON request_items (request_id);

CREATE TRIGGER conversation_messages_no_update
  BEFORE UPDATE OR DELETE ON conversation_messages
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER conversation_messages_no_truncate
  BEFORE TRUNCATE ON conversation_messages
  FOR EACH STATEMENT EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER llm_calls_no_update
  BEFORE UPDATE OR DELETE ON llm_calls
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();
CREATE TRIGGER request_parameters_no_update
  BEFORE UPDATE OR DELETE ON request_parameters
  FOR EACH ROW EXECUTE FUNCTION forbid_mutation();

ALTER TABLE request_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_analyses FORCE ROW LEVEL SECURITY;
ALTER TABLE request_parameters ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_parameters FORCE ROW LEVEL SECURITY;
ALTER TABLE clarifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE clarifications FORCE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages FORCE ROW LEVEL SECURITY;
ALTER TABLE feasibility_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE feasibility_reports FORCE ROW LEVEL SECURITY;
ALTER TABLE llm_calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_calls FORCE ROW LEVEL SECURITY;
ALTER TABLE split_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE split_proposals FORCE ROW LEVEL SECURITY;
ALTER TABLE request_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_items FORCE ROW LEVEL SECURITY;

CREATE POLICY request_analyses_visibility ON request_analyses
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY request_parameters_visibility ON request_parameters
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY clarifications_visibility ON clarifications
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY conversation_messages_visibility ON conversation_messages
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY feasibility_reports_visibility ON feasibility_reports
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY llm_calls_visibility ON llm_calls
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY split_proposals_visibility ON split_proposals
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
CREATE POLICY request_items_visibility ON request_items
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

GRANT SELECT, INSERT ON request_analyses, request_parameters, clarifications,
  conversation_messages, feasibility_reports, llm_calls, split_proposals,
  request_items TO agent_app;
GRANT UPDATE ON clarifications TO agent_app;
