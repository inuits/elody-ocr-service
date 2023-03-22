#!/bin/sh

export PATH=${PATH}:/app/.local/bin
export DB_ENGINE=$1
export REQUIRE_TOKEN=0
export STORAGE_API_URL=https://dams-storage-api.inuits.io
export STORAGE_API_URL_EXT=https://dams-storage-api.inuits.io
export COLLECTION_API=http://collection-api:5000/
export COLLECTION_API_URL=http://collection-api:5000/
export FLASK_ENV=development

cat << EOF
============================================
== Begin DAMS OCR Service API test results ==
============================================
EOF

coverage run -m pytest -s

cat << EOF
==========================================
== End DAMS OCR Service API test results ==
==========================================
EOF
