# ADR-007 — Image unique, deux rôles, SBOM

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-007, ET-009, ET-010, ET-011, ET-012, ET-347, ADR-016 (spécification technique)

## Contexte

Une seule image doit servir l'API et le travailleur, sans privilèges
administrateur, avec une liste de composants.

## Décision

- ops/Dockerfile multi-étapes : construction des dépendances avec uv, image
  d'exécution python:3.13-slim, utilisateur forge UID/GID 10001.
- ops/entrypoint.sh choisit le rôle avec AGENT_ROLE (api ou worker).
- ops/compose.yaml fournit PostgreSQL local, l'API et le travailleur.
- La CI construit l'image, vérifie l'UID 10001 et publie une SBOM SPDX via
  anchore/sbom-action. ops/sbom.sh permet de la produire localement avec syft.
- Les quatre environnements ont des fichiers séparés dans ops/env/.

## Conséquences

- Aucun secret dans l'image ni dans le dépôt ; les valeurs sont injectées.
- Une image unique réduit la dérive entre API et travailleur.
- La SBOM est un artefact de CI, pas un fichier versionné.

## Alternatives écartées

- Deux images : duplication et risque de versions divergentes.
- Exécution en root : contredit ET-009.
