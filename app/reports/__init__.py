from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.doctemplate import _doNothing
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT

from django.utils import timezone
import copy

import unidecode

left_margin =  1.25 * cm
right_margin = 1.25 * cm
top_margin = 1 * cm
bottom_margin = 1 * cm
line_spacing = 0.3 * cm

term_format = '%m/%Y'
date_format = '%d/%m/%Y'
time_format = '%H:%M'
datetime_format = date_format + ' ' + time_format

size = landscape(A4)
width, height = size
available_width, available_height = width - left_margin - right_margin, height - top_margin - bottom_margin
separator = Table([''], colWidths=[available_width], rowHeights=line_spacing, style=[('LINEABOVE', (0,0), (0,0), 1, colors.black)])

default_style = ParagraphStyle('default')
right_aligned_style = ParagraphStyle('right_align', alignment=TA_RIGHT)
huge_centered = ParagraphStyle('huge_centered', fontSize=30, alignment=TA_CENTER )
nombre_y_apellido = ParagraphStyle('nombre_y_apellido', fontName='NeoSans', fontSize=30, textColor=colors.gray, alignment=TA_CENTER )
curso = ParagraphStyle('curso', fontName='NeoSans Bold', fontSize=13, leading=17, textColor=colors.dimgray, alignment=TA_CENTER, textTransform='uppercase' )


class HeaderImage(Image):
    def __init__(self, filename, member, width=None, height=None, kind='direct',
                 mask="auto", lazy=1, hAlign='CENTER'):
        self.member = member
        super(HeaderImage, self).__init__(filename, width=width, height=height,
                                          kind=kind, mask=mask, lazy=lazy, hAlign=hAlign)

    def draw(self):
        now = timezone.now()
        super(HeaderImage, self).draw()
        self.canv.setFont('Helvetica', 10)
        self.canv.drawString(12.25*cm, 0.55*cm, now.strftime(date_format))

        if self.member.code:
            self.canv.drawString(12.25 * cm, 1.2 * cm, '%d' % (self.member.code_id,))


def single_row_table(data, draw_line=True, style_commands=[]):
    columns = len(data)
    t = Table([data])
    if draw_line:
        style_commands = style_commands + [('LINEBELOW', (i, 0), (i, 0), 0.5, colors.black) for i in range(len(data)) if i % 2 != 0]
    t.setStyle(TableStyle(style_commands))

    tc = copy.copy(t)
    tc._calc(available_width, available_height)

    occupied_width = sum([tc._colWidths[i] for i in range(columns) if i % 2 == 0])
    remaining_width = available_width - occupied_width
    data_column_width = remaining_width / (columns / 2)

    for c in [i for i in range(columns) if i % 2 == 1]:
        t._argW[c] = data_column_width

    return t


def new_line(data):
    story = []

    t = single_row_table(data)
    story.append(t)
    story.append(Spacer(0, line_spacing))

    return story


def sino_string(si):
    fmt = '%s     %s'
    string = ''
    if si is None:
        string = fmt % ('SI', 'NO')
    else:
        string = fmt % ('SI' if si else '<strike>SI</strike>', '<strike>NO</strike>' if si else 'NO')

    return Paragraph(string, default_style)


def report_to_stream(report_func):
    import io
    stream = io.BytesIO()
    rep = report_func(stream)
    return stream


def AllPageSetup(ce):
    """

    :param ce: CourseEnrollment
    :return:
    """
    def f(canvas, doc):
        canvas.saveState()

        certif_template_path = ce.course.certificate_template.path if ce.course.certificate_template else '/app/reports/img/Certificado.png'
        canvas.drawImage(certif_template_path, 0, 0, width=width, height=height)

        # nombre_ceo = 'CEO. SERGIO FAIFMAN'
        # w = canvas.stringWidth(nombre_ceo, fontName='NeoSans Bold', fontSize=16)
        # to = canvas.beginText((width-w)/2-2.5*cm, 2*cm)
        # to.setFont('NeoSans Bold', 16)
        # to.setFillGray(0.4)
        # to.textLine(nombre_ceo)
        #
        # canvas.drawText(to)

        canvas.restoreState()

    return f


def nombre_y_apellido_stories(nombre):
    return [
        Spacer(0, 8.6*cm),
        Paragraph(unidecode.unidecode(nombre), nombre_y_apellido)
    ]


def curso_stories(nombreCurso):
    return [
        Spacer(0, 2.6*cm),
        Paragraph(nombreCurso, curso)
    ]


def ceo_stories(nombreCEO):
    return [
        Spacer(0, 5 * cm),
        Paragraph('<b>%s</b>' % unidecode.unidecode(nombreCEO), curso)
    ]


def dummy_diploma(course_enrollment, stream):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont('NeoSans', '/app/static/fonts/neosans/neosans.ttf'))
    pdfmetrics.registerFont(TTFont('NeoSans Bold', '/app/static/fonts/neosans-bold/neosans-bold.ttf'))
    pdfmetrics.registerFont(TTFont('NeoSans Italic', '/app/static/fonts/neosans-italic/neosans-italic.ttf'))
    pdfmetrics.registerFont(TTFont('NeoSans Light', '/app/static/fonts/neosans-light/NeoSans-Light.ttf'))
    pdfmetrics.registerFont(TTFont('NeoSans Medium', '/app/static/fonts/neosans-medium/NeoSans-Medium.ttf'))

    doc = SimpleDocTemplate(stream,
                            pagesize=size,
                            leftMargin=left_margin,
                            rightMargin=right_margin,
                            bottomMargin=bottom_margin,
                            topMargin=top_margin,
                            title='Constancia')
    
    nombreYApellido = f'{course_enrollment.user.name} {course_enrollment.user.last_name}'
    # nombreCurso = course_enrollment.course.title
    # nombreCurso = ["OBJETIVOS DEL CODIGO DE CONDUCTA", "LEYES Y REGULACIONES APLICABLES", "VALORES COMITÉ DE ETICA Y CUMPLIMIENTO", "OFICIAL DE ETICA Y CUMPLIMIENTO", "COMO ACTUAR ANTE DIFERENTES SITUACIONES", "DERECHOS FUNDAMENTALES DEL COLABORADOR", "CONDUCTA PERSONAL DEL COLABORADOR", "RELACIÓN DEL GRUPO CON TERCEROS", "RELACIÓN CON EL MERCADO ACCIONARIO"]
    # nombreCurso = " &#47; ".join([unidecode.unidecode(s) for s in nombreCurso])

    story = nombre_y_apellido_stories(nombreYApellido) # + \
            # curso_stories(nombreCurso)

    doc.build(story, onFirstPage=AllPageSetup(course_enrollment), onLaterPages=AllPageSetup(course_enrollment))

    return doc