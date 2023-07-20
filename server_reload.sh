#!/bin/sh

find booking-server booking-common | entr -r python booking-server/booking_server
