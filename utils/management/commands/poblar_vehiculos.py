from django.core.management.base import BaseCommand
from django.db import connections
from vehiculos.models import Vehiculo
from tqdm import tqdm

# Campos que vienen de la DB externa (tabla propietario)
MAPEO = {
    "placa": "placa",
    "color": "color",
    "tarjeta_propiedad": "tarjeta_propiedad",
    "modelo_ext": "modelo",
}

COLORES_VALIDOS = [
    "Negro", "Negro Mate", "Gris", "Blanco",
    "Morado", "Azul", "Rojo"
]

class Command(BaseCommand):
    help = "Migra vehículos desde DB externa (propietario)"

    def detectar_marca_y_serie(self, modelo):
        modelo = (modelo or "").upper()

        if "NKD" in modelo:
            return "NKD", "NKD 1125"
        if "BERA" in modelo:
            return "BERA", "SBR 150"
        if "BAJA" in modelo:
            return "BAJAJ", "BOXER CT"

        return None, None

    def detectar_modelo(self, modelo):
        modelo = modelo or ""

        if "2024" in modelo:
            return "2024"
        if "2025" in modelo:
            return "2025"
        if "2026" in modelo:
            return "2026"

        return None

    def normalizar_color(self, color):
        color = (color or "").title()
        return color if color in COLORES_VALIDOS else "Negro"

    def handle(self, *args, **options):

        columnas_externas = ", ".join(MAPEO.values())

        with connections["externa"].cursor() as cursor:
            cursor.execute(f"""
                SELECT {columnas_externas}
                FROM propietario
            """)
            filas = cursor.fetchall()

        creados = 0
        omitidos = 0

        for fila in tqdm(filas, desc="Migrando vehículos", unit="vehículo"):
            data = {
                campo_modelo: fila[i]
                for i, campo_modelo in enumerate(MAPEO.keys())
            }

            marca, serie = self.detectar_marca_y_serie(data["modelo_ext"])
            modelo = self.detectar_modelo(data["modelo_ext"])

            # 🚨 Si no se puede inferir marca o modelo → se omite
            if not marca or not modelo:
                omitidos += 1
                continue

            defaults = {
                "marca": marca,
                "modelo": modelo,
                "serie": serie,
                "propietario": data["tarjeta_propiedad"] or "Por definir",
                "color": self.normalizar_color(data["color"]),
            }

            _, created = Vehiculo.objects.get_or_create(
                placa=data["placa"],
                defaults=defaults
            )

            if created:
                creados += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n✔ Vehículos creados: {creados}")
        )
        self.stdout.write(
            self.style.WARNING(f"⚠ Vehículos omitidos: {omitidos}")
        )
