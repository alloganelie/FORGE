-- Types enumeres generes depuis la specification (ET-017, DC-05).
-- NE PAS MODIFIER A LA MAIN. Regenerer : python tools/gen_enums.py
-- Sources : specification fonctionnelle section 8, specification technique 6.3.

CREATE TYPE st_request AS ENUM ('received', 'clarifying', 'feasibility', 'producing', 'quality_control', 'blocked', 'awaiting_decision', 'suspended', 'finalized', 'cancelled');
CREATE TYPE st_conformity AS ENUM ('not_evaluated', 'in_control', 'non_conforming', 'conforming');
CREATE TYPE st_approval AS ENUM ('not_submitted', 'not_required', 'pending', 'approved', 'refused');
CREATE TYPE st_diffusion AS ENUM ('not_authorized', 'authorized', 'revoked');
CREATE TYPE st_version AS ENUM ('provisional', 'finalized', 'superseded', 'abandoned');
CREATE TYPE st_element AS ENUM ('to_produce', 'produced', 'blocked', 'awaiting', 'controlled_ok', 'non_conforming', 'not_applicable');
CREATE TYPE qi_status AS ENUM ('verified', 'candidate', 'uncertain', 'contradictory', 'out_of_period', 'prohibited', 'absent');
CREATE TYPE lc_status AS ENUM ('satisfied', 'partial', 'to_clarify', 'blocked', 'not_applicable');
CREATE TYPE atom_origin AS ENUM ('quotation', 'reformulation', 'computation', 'template_text', 'structure');
CREATE TYPE control_outcome AS ENUM ('passed', 'failed', 'not_executable', 'not_applicable');
CREATE TYPE anomaly_class AS ENUM ('established_nonconformity', 'established_inconsistency', 'observation');
CREATE TYPE decision_type AS ENUM ('contradiction_arbitration', 'uncovered_decision', 'exception', 'temporary_source_authorization', 'approval', 'diffusion_authorization', 'rule_change', 'priority_arbitration', 'cancellation', 'uncovered_correction');
CREATE TYPE auth_level AS ENUM ('access', 'use', 'integration', 'diffusion');
