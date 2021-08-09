source ../../.env
echo $NGENV
npm install
npm run build:elements-ng8
rm -rvf ../../app/static/elements/admin-encuesta
cp -rvf dist ../../app/static/elements/admin-encuesta