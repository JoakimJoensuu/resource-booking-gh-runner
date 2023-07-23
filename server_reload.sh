#!/bin/sh

find . -type f -name "*.py" ! -path "*/.venv/*" | entr -rs "echo ''; echo ===============================================; echo ''; python booking-server/booking_server"
