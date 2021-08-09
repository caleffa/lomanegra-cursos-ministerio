from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command, get_commands, load_command_class
from django.db import connection
from django.utils import timezone
import argparse

from cursos.views import in_memory_xls_from_stats_data, stats_data_users_evolution
from cursos.models import UsersEvolutionReport, UsersEvolutionPerCourseReport, Course


class Command(BaseCommand):
    help = 'Generates user\'s evolution report and saves it to DB and excel file'

    def handle(self, *args, **options):
        evorep = UsersEvolutionReport.objects.create()

        content = in_memory_xls_from_stats_data(stats_data_users_evolution(), 'Evolución usuarios')

        finished = timezone.now()
        started = timezone.localtime(evorep.started)

        evorep.file.save(f'evolucion_usuarios_{started.strftime("%Y%m%d%H%M%S")}.xlsx', content)
        evorep.present = True
        evorep.finished = finished
        evorep.save()

        for course in Course.objects.all():
            uepcr = UsersEvolutionPerCourseReport()
            stats_data = stats_data_users_evolution(course)
            if len(stats_data['table_data']) > 0:
                report_content = in_memory_xls_from_stats_data(stats_data, 'Evolución usuarios por curso')
                finished = timezone.now()
                started = timezone.localtime(uepcr.started)
                
                uepcr.present = True
                uepcr.finished = finished
                uepcr.course = course
                uepcr.file.save(f'evolucion_usuarios_curso_{course.id}_{started.strftime("%Y%m%d%H%M%S")}.xlsx', report_content)
                uepcr.save()

