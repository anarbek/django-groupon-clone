#!/usr/bin/env bash
# Currently we save only FlatPages, PhotoSize
./manage.py dumpdata --format=json --indent=4 flatpages.Flatpage photologue.PhotoSize > engine/fixtures/initial_data.json

