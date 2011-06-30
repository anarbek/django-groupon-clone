#!/usr/bin/env bash
# Currently we save only FlatPages
./manage.py dumpdata --format=json --indent=4 flatpages.Flatpage > engine/fixtures/initial_data.json

