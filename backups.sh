#!/bin/bash

## Esto es el script que se ejecuta todas las madrugadas para hacer el backup en la VM de produccion

export RESTIC_REPOSITORY=gs:backups-lomanegra-prod:/
export RESTIC_PASSWORD=**********
export GOOGLE_PROJECT_ID=429394962910
export GOOGLE_APPLICATION_CREDENTIALS=./lomanegra-cursos-c92390e364b4.json




/usr/bin/docker exec -ti cursoslomanegraproduction_postgres_1 pg_dump -U postgres postgres > /backups/lomanegra-prod-backup.sql

/usr/local/bin/restic --verbose backup /backups /srv/volumes
