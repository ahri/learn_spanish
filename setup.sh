#!/bin/sh
db="spanish.db"
sql="spanish.sql"

rm -f "$db"
sqlite3 "$db" < "$sql"
