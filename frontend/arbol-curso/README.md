## Local development

Para desarrollo local, correr

    ng serve


Y en el `settings.py` comentar las líneas de `REST_FRAMEWORK` que settean `'rest_framework.permissions.IsAdminUser'` como `DEFAULT_PERMISSION_CLASSES`. Esto para poder usar las APIs desde el development server sin estar autenticados.

## Compilar para prod


    npm run build:elements-ng8
    rm -r ../../app/static/elements/arbol-curso
    cp -r dist ../../app/static/elements/arbol-curso

