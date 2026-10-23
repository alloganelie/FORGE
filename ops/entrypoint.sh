#!/bin/sh
set -eu

case "${AGENT_ROLE:-api}" in
  api)
    exec uvicorn agent.interfaces.rest.app:app \
      --host "${AGENT_API_HOST:-0.0.0.0}" \
      --port "${AGENT_API_PORT:-8000}"
    ;;
  worker)
    exec python -m agent.interfaces.worker
    ;;
  *)
    echo "AGENT_ROLE inconnu : ${AGENT_ROLE}" >&2
    exit 64
    ;;
esac
