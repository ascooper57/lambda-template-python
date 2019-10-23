#!/usr/bin/env bash

brew services stop postgres
rm -f /usr/local/var/postgres/postmaster.pid
