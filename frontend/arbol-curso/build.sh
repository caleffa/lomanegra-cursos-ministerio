source ../../.env
export NGENV
echo $NGENV
npm install
npm run build:elements-ng8
rm -rfv ../../app/static/elements/arbol-curso
cp -rfv dist ../../app/static/elements/arbol-curso
(cd ../.. && docker-compose run --rm app ./manage.py collectstatic --no-input)
