#!/bin/bash
docker run \
	--name othello_psql \
       	-e POSTGRES_DB=othello \
       	-e POSTGRES_USER=othello \
       	-e POSTGRES_PASSWORD=pwd \
       	-v pgdata:/var/lib/postgresql/data \
       	-d -p 5432:5432 postgres:latest
