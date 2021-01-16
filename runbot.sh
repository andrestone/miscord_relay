#!/bin/sh

while true; do $(which screen) -dmS miscord_relay $(pwd)/miscord_relay.py; done
