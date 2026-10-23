# FORGE - commandes standard (ET-353 a ET-356, annexe F.3)
# Sur Windows : make (ezwinports) ; sinon python tools/check.py <cible>.

ifeq ($(OS),Windows_NT)
PYTHON ?= py -3.13
else
PYTHON ?= python3
endif

.PHONY: check test test-acceptance spec-trace gen-transitions gen-enums verify-chain \
        db-up db-down spec toc index briefs brief fmt

check:  ## format, types, dependances, generation, tests, tracabilite
	$(PYTHON) tools/check.py check

test:
	$(PYTHON) tools/check.py test

test-acceptance:
	$(PYTHON) tools/check.py test-acceptance

spec-trace:
	$(PYTHON) tools/check.py spec-trace

gen-transitions:
	$(PYTHON) tools/check.py gen-transitions

gen-enums:
	$(PYTHON) tools/check.py gen-enums

verify-chain:
	$(PYTHON) tools/check.py verify-chain

db-up:
	$(PYTHON) tools/check.py db-up

db-down:
	docker compose -f ops/compose.yaml down -v

fmt:
	$(PYTHON) tools/check.py fmt

spec:  ## make spec ID=CA-099
	$(PYTHON) tools/spec.py show $(ID)

toc:  ## make toc DOC=T
	$(PYTHON) tools/spec.py toc $(DOC)

brief:  ## make brief MS=MS-3
	$(PYTHON) tools/spec.py milestone $(MS)

index:  ## regenere INDEX.md et ids.json
	$(PYTHON) tools/spec.py index

briefs:  ## regenere briefs et prompts de jalons
	$(PYTHON) tools/gen_briefs.py
