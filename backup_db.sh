#!/bin/bash
set -euo pipefail
# backup_db.sh - Sauvegarde PostgreSQL en utilisant DATABASE_URL (Render)

# Répertoire de sauvegarde (chemin dans le conteneur Render)
BACKUP_DIR="/opt/render/project/src/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "📦 Début de la sauvegarde : ${TIMESTAMP}"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "❌ DATABASE_URL non défini. Exporter la variable d'environnement dans Render."
  exit 1
fi

# Utiliser pg_dump via l'URL fournie par Render
pg_dump "${DATABASE_URL}" --no-owner --no-acl | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

echo "✅ Sauvegarde terminée : ${BACKUP_FILE}"
echo "📏 Taille : $(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)"

# Nettoyage : supprimer les sauvegardes de plus de 7 jours
find "${BACKUP_DIR}" -name "backup_*.sql.gz" -mtime +7 -print -delete || true
echo "🗑️  Nettoyage des anciennes sauvegardes effectué"

echo "✅ Script de sauvegarde terminé"
