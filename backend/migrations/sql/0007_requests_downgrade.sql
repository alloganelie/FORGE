-- Retour arriere MS-2 (developpement uniquement).
DROP TABLE IF EXISTS request_items, split_proposals, llm_calls, feasibility_reports,
  conversation_messages, clarifications, request_parameters, request_analyses CASCADE;
ALTER TABLE requests DROP COLUMN IF EXISTS diagnostic_only;
ALTER TABLE requests DROP COLUMN IF EXISTS target_format;
