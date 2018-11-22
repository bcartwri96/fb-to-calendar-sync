#!/bin/bash
echo "Running Calendar Sync"
cd /home/ec2-user/fb-to-calendar-sync/
pipenv run sync

