## Local development

Para desarrollo local, correr

    ng serve


Y en el `settings.py` comentar las líneas de `REST_FRAMEWORK` que settean `'rest_framework.permissions.IsAdminUser'` como `DEFAULT_PERMISSION_CLASSES`. Esto para poder usar las APIs desde el development server sin estar autenticados.

Pero también es necesario settear this.configObj de alguna manera.... por ahora lo hice a mano pero es un bajón.

## Compilar para prod


    ng build --output-hashing none
    rm -r ../../app/static/elements/iniciar-conversacion-form/*
    cp dist/* ../../app/static/elements/iniciar-conversacion-form/

TODO: cuando compilo con el flag `--prod` me tira un error al cargar el componente:

ERROR ReferenceError: Must call super constructor in derived class before accessing 'this' or returning from derived constructor
    at new hh (main.js:1)