#!/bin/sh

GITHUB_TOKEN="$1"

(find . -type f -path "./*/booking_server/*.py" ! -path "*/.venv/*" | entr -rs "echo ''; echo ===============================RELOAD===============================; echo ''; python booking-server/booking_server $GITHUB_TOKEN" | tee stdout.log) 3>&1 1>&2 2>&3 | tee stderr.log
