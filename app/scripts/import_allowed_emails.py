import csv

from cursos.models import Area, AllowedEmail
from django.db import transaction

to_import = {}
with open('/srv/uploads/importar.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        email = row['email']
        if to_import.get(row['email']):
            print(f'WARNING: {email} aparece dos veces en el Excel. Lo cargaremos sin área.')
            to_import[email] = None
        else:
            to_import[email] = Area.objects.get(name=row['area'])

with transaction.atomic():
    for email, area in to_import.items():
        nuevo, created = AllowedEmail.objects.get_or_create(email=email)
        if created:
            if area:
                nuevo.area = area
                nuevo.save()
                print(f'OK. {nuevo.email} agregado para area {nuevo.area.name}.')
            else:
                print(f'OK. {nuevo.email} agregado sin área.')
        else:
            if area:
                if not nuevo.area:
                    nuevo.area = area
                    nuevo.save()
                    print(f'OK. {nuevo.email} ya estaba en la base pero no tenía area asignada. Le asignamos area {nuevo.area.name}.')
                else:
                    if nuevo.area == area:
                        print(f'OK. {nuevo.email} ya estaba en la base con area {nuevo.area.name}.')
                    else:
                        print(f'ERROR: {nuevo.email} ya estaba en la base con area {nuevo.area.name}. No lo modificamos.')
            else:
                if not nuevo.area:
                    print(f'OK. {nuevo.email} ya estaba en la base sin área. No lo modificamos.')
                if nuevo.area:
                    print(f'ERROR: {nuevo.email} ya estaba en la base con área {nuevo.area}. No lo modificamos.')



