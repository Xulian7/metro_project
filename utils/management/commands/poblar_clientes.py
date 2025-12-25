from django.core.management.base import BaseCommand
from django.db import connections
from clientes.models import Cliente
from tqdm import tqdm

# Campos que vienen de la DB externa
MAPEO = {
    "cedula": "cedula",
    "nombre": "nombre",
    "nacionalidad": "nacionalidad",
    "telefono": "telefono",
    "direccion": "direccion",
}

TIPO_DEFAULT = "Normal"
STATUS_DEFAULT = "Normal"

class Command(BaseCommand):
    help = "Migra clientes básicos con barra de progreso"

    def handle(self, *args, **options):

        columnas_externas = ", ".join(MAPEO.values())

        with connections['externa'].cursor() as cursor:
            cursor.execute(f"""
                SELECT {columnas_externas}
                FROM clientes
            """)
            filas = cursor.fetchall()

        creados = 0

        for fila in tqdm(filas, desc="Migrando clientes", unit="cliente"):
            data = {
                campo_modelo: fila[i]
                for i, campo_modelo in enumerate(MAPEO.keys())
            }

            data["tipo"] = TIPO_DEFAULT
            data["status"] = STATUS_DEFAULT

            _, created = Cliente.objects.get_or_create(
                cedula=data["cedula"],
                defaults=data
            )

            if created:
                creados += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n✔ Clientes creados: {creados}")
        )
