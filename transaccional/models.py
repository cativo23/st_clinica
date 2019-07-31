from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone as tz
from django.contrib.auth.models import User


# Create your models here.
class Doctor(models.Model):
    nombre = models.CharField('Nombre del doctor', max_length=40, null=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctores'


class Medicamento(models.Model):
    nombre_producto = models.CharField('Nombre del producto', max_length=30, blank=False, null=False)
    marca_producto = models.CharField('Marca del producto', max_length=30, blank=False, null=False)
    existencia_producto = models.IntegerField('Exitencias', blank=False, null=False)
    precio_producto = models.DecimalField('Precio unitario', max_digits=5, decimal_places=2, blank=True, null=True)
    formafarmaceutica = models.CharField('Forma Farmaceutica', max_length=30, blank=False, null=False)

    def __str__(self):
        return self.nombre_producto + ", " + self.marca_producto

    class meta:
        ordering = ['existencia_producto']
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        unique_together = (("nombre_producto", "marca_producto", "precio_producto"))


class LoteMedicamento(models.Model):
    medicamento = models.ForeignKey(Medicamento, blank = False, null = False,on_delete = models.CASCADE)
    fecha_vencimiento = models.DateField('Fecha de Vencimiento',blank = False, null = False)
    fecha_entrada = models.DateField('Fecha de entrada',blank = False, null = False , default=tz.now)
    cantidad=models.IntegerField('Cantidad de entrada',blank=False,null=False,validators = [MinValueValidator(0)])


class Odontograma(models.Model):
    medico = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    fechaCreacion = models.DateTimeField('date_created', auto_now_add=True)
    fechaUltimaModificacion = models.DateTimeField('Última modificación', auto_now=True)
    notas = models.TextField()

    def __str__(self):
        return '#%s - Ondontograma del %s' % (self.id, Expediente.objects.filter(odontograma=self.id).first())


class Paciente(models.Model):
    MASCULINO = 'M'
    FEMENINO = "F"
    SEXO_CHOICES = (
        (MASCULINO, 'Masculino'),
        (FEMENINO, 'Femenino'),
    )
    nombresPaciente = models.CharField('Nombres del paciente', max_length=60, blank=False, null=False)
    apellidosPaciente = models.CharField(max_length=60, blank=False, null=False)
    sexo = models.CharField(max_length=2, choices=SEXO_CHOICES, default=None, blank=False, null=False)
    fechaNacimiento = models.DateField('Fecha de nacimiento', blank=False, null=False)
    referencia = models.CharField('Responsable', max_length=60, help_text='(En caso de ser niño)', blank=True, null=True)

    def __str__(self):
        return self.apellidosPaciente + ", " + self.nombresPaciente

    class Meta:
        ordering = ['apellidosPaciente', 'nombresPaciente']
        unique_together = (("nombresPaciente", "apellidosPaciente"),)
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'


class Expediente(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    odontograma = models.OneToOneField(Odontograma, on_delete=models.CASCADE, null=True, blank=True)
    fechaCreacion = models.DateTimeField('date_created', default=tz.now)
    pagado = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=False, default=0)
    saldo = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=False, default=0)
    observacionExp = models.TextField('Observaciones', max_length=250, blank=True, null=True)

    def __str__(self):
        return "Expediente de " + self.paciente.apellidosPaciente + ", " + self.paciente.nombresPaciente

    class Meta:
        ordering = ['paciente']
        verbose_name = 'Expediente'
        verbose_name_plural = 'Expedientes'


class Cita(models.Model):
    asuntoCita=models.CharField('Asunto de la cita', max_length=50,blank=False,null=False)
    paciente = models.ForeignKey(Expediente, on_delete=models.PROTECT)
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    fechaCita = models.DateField('Fecha de Cita', blank=False, null=False)
    horaCita = models.TimeField('Hora de Cita', blank=False, null=False)
    observacionCita = models.TextField('Observaciones', max_length=250, blank=True, null=True)

    def __str__(self):
        return 'Cita de {} el dia {}'.format(self.paciente.paciente.nombresPaciente, self.fechaCita)

    class Meta:
        ordering = ['fechaCita', 'horaCita']
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'


class Tratamiento(models.Model):
    nombreTratamiento = models.CharField('Nombre del tratamiento', max_length=100, blank=False, null=False)
    descripcionTratamiento = models.TextField('Descripcion del tratamiento', max_length=250, blank=True, null=True)
    precioBase = models.DecimalField('Precio Base', max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nombreTratamiento

    class Meta:
        ordering = ['nombreTratamiento']
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'


class Consulta(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    paciente = models.ForeignKey(Expediente, on_delete=models.PROTECT)
    fechaConsulta = models.DateField('Fecha de Consulta', default=tz.now)
    horaInicio = models.TimeField('Hora de inicio', auto_now_add=True)
    horaFinal = models.TimeField('Hora de Final', auto_now_add=False, null=True)
    observacionCons = models.TextField('Observaciones', max_length=250, blank=True, null=True)
    precio = models.DecimalField('Precio Base', max_digits=5, decimal_places=2, default=10.00)

    def __str__(self):
        return 'Consulta de {} del dia {}'.format(self.paciente.paciente.nombresPaciente, self.fechaConsulta)

    class Meta:
        ordering = ['fechaConsulta', 'horaInicio']
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'


class Procedimiento(models.Model):
    CARAS_CHOICES = (
        ('S', 'Vestibular'),
        ('C', 'Oclusal'),
        ('X', 'Pieza Completa'),
        ('Z', 'Distal'),
        ('D', 'Mesial'),
        ('I', 'Palatino'),
    )
    STATUS_CHOICES = (
        ('recomendado', 'Recomendado'),
        ('autorizado', 'Autorizado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado')
    )

    pieza = models.IntegerField()
    cara = models.CharField(max_length=4, choices=CARAS_CHOICES)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    odontograma = models.ForeignKey(Odontograma, on_delete=models.CASCADE)
    diagnostico = models.TextField()
    consulta_realizada = models.ForeignKey(Consulta, on_delete=models.CASCADE, null=True)
    notas = models.TextField(blank=True)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default='recomendado')

    def __str__(self):
        return '{} de {}'.format(self.tratamiento.nombreTratamiento, self.consulta_realizada.paciente)


class Pago(models.Model):
    Expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, null=True, blank=False)
    fechaPago = models.DateTimeField('Fecha de Pago', auto_now_add=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False, default=0.00)
    procedimiento = models.ForeignKey(Procedimiento, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '#%s - Pago por: %s del %s para %s' % (self.fechaPago, self.cantidad, self.Expediente, self.procedimiento.tratamiento.nombreTratamiento)


class Receta(models.Model):
    nombreReceta = models.CharField('Nombre de la receta', max_length=100, blank=False, null=False, default='Receta')
    consulta = models.ForeignKey('Consulta', on_delete=models.PROTECT)
    medicamento = models.ManyToManyField(Medicamento, through='Especificacion')

    def __str__(self):
        return self.nombreReceta


class Especificacion(models.Model):
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    dosis = models.CharField('Dosis', max_length=45, blank=False, null=False)
    duracion = models.CharField('Duracion', max_length=45, blank=False, null=False)


class Bitacora(models.Model):
    usuario=models.ForeignKey(User,null=False, on_delete=models.CASCADE)
    accion=models.CharField('Accion realizada',max_length=255)
    fecha=models.DateTimeField('Fecha accion',null=False)
