# Quick start:

	docker network create webproxy
	cp .env.sample .env
	cd app
	npm install
	cd ..

Si tenés un dump, copiarlo en `./volumes/postgres_initialize` y luego

	docker-compose up --build


La URL para desarrollo local `https://local.cursoslomanegra.clementine.com.ar/`



Para usar pgadmin, descomentar en `docker-compose.override.yml`
  host: postgres
  el resto lo dejás como viene


Para levantar shell de Django:

	docker-compose run --rm app python manage.py shell_plus


# Para levantar un nuevo entorno

1. Crear un nuevo branch del repo. El branch no debe tener guiones, solo letras o números. Llamémoslo "nuevoentorno"
2. En master, modificar el `.gitlab-ci.yml` hay que agregar un job de deployment como este:

```
	deploy_nuevoentorno:
	  variables:
	    COMPOSE_FILE: docker-compose.yml:docker-compose.deployments.yml
	    VIRTUAL_HOST: nuevoentorno.everycompliance.com
	    LOGLEVEL: INFO
	    DEBUG: "True"
	    MAILGUN_API_KEY: $MAILGUN_API_KEY
	    SENTRY_DSN: $nuevoentorno_SENTRY_DSN
	    SECRET_KEY: $nuevoentorno_SECRET_KEY
	    POSTGRES_PASSWORD: $nuevoentorno_POSTGRES_PASSWORD
	    SENTRY_FRONTEND_DSN: $nuevoentorno_SENTRY_FRONTEND_DSN
	  stage: deploy
	  environment:
	    name: nuevoentorno
	    url: https://nuevoentorno.everycompliance.com
	  script:
	    - docker-compose up -d
	  only:
	    - nuevoentorno
```
3. En la interfaz web de Gitlab, agregar las secret variables que acabamos de definir en el job (las de SENTRY, la pass de POSTGRES, la SECRET KEY, etc.)
4. Apuntar los DNS a la VM
5. Pushear a master y mergear de master al branch nuevo.

# Para levantar un backup de Loma Negra (disaster recovery)

Los backups están almacenados en un bucket de Google Cloud Storage usando [restic](https://restic.readthedocs.io/en/stable/).

1. Para hacer un restore, tenemos que acceder de alguna manera al bucket. Podemos crear una "service account" en [Google Cloud IAM](https://console.cloud.google.com/iam-admin/serviceaccounts?project=lomanegra-cursos).

No debemos asignarle ningún rol, solo crearla y crearle una key (descargar el JSON).

2. Luego vamos [Google Cloud Storage, al bucket backups-lomanegra-prod](https://console.cloud.google.com/storage/browser/backups-lomanegra-prod?project=lomanegra-cursos). Vamos a la pestaña 'Permissions' y agregamos la service account que creamos (debemos usar el campo `client_email` del JSON), asignándole el rol 'Storage Object Admin'.

3. Con eso, ya podemos hacer los siguientes 4 exports de variables de entorno para configurar restic:

    export RESTIC_REPOSITORY=gs:backups-lomanegra-prod:/
    export RESTIC_PASSWORD=**********
    export GOOGLE_PROJECT_ID=429394962910
    export GOOGLE_APPLICATION_CREDENTIALS=./lomanegra-cursos-c92390e364b4.json


Por supuesto, `RESTIC_PASSWORD` hay que reemplazarlo por la password que tenemos en nuestros password managers.

4. Con ejecutar `restic snapshots` podemos ver qué backups hay. Se están backupeando dos directorios del servidor:

  * /backups   donde están los dumps de PostgreSQL
  * /srv/volumes  donde están todos los volúmenes de Docker

5. Debemos hacer [restore](https://restic.readthedocs.io/en/stable/050_restore.html) de todo el `/srv/volumes` salvo el volumen de `postgres_persistence`, ya que es preferible hacer restore desde el dump.

El dump se puede ubicar en un volumen a llamar `postgres_initialize` y montarlo en `/docker-entrypoint-initdb.d` en el container de PostgreSQL (como hacemos en `docker-compose.override.yml`).

Por ejemplo, para hacer un restore en mi computadora, hice esto:

    mkdir restored
    restic restore latest --target restored --verbose --verify
    mkdir volumes/postgres_initialize
    mv restored/srv/volumes/production/* volumes
    mv restored/backups/lomanegra-prod-backup.sql volumes/postgres_initialize
    rm -r volumes/postgres_persistence/pgdata