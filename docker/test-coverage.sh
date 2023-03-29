#!/bin/sh

export PATH=${PATH}:/app/.local/bin

cat << EOF
=============================================
== Begin OCR Service API test coverage ==
=============================================
EOF

coverage report -m

cat << EOF
===========================================
== End OCR Service API test coverage ==
===========================================
EOF
