#!/bin/sh

find . -type f -path "./*/booking_server/*.py" ! -path "*/.venv/*" | entr -rs "echo ''; echo ===============================================; echo ''; python booking-server/booking_server"
