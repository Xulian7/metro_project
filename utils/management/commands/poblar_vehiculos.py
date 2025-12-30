from django.core.management.base import BaseCommand
from django.db import connections
from vehiculos.models import Vehiculo
from tqdm import tqdm
from datetime import datetime
import os

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

LOG_FILE = "log.txt"

class Command(BaseCommand):
    help = "Migra vehículos desde DB externa (propietario)"

    # 🔤 Normalización a Nombre Propio
    def nom_propio(self, texto):
        return (texto or "").strip().title()

    def detectar_marca_y_serie(self, modelo):
        modelo_up = (modelo or "").upper()

        # 🎯 Regla especial: MILAN → BERA
        if "MILAN" in modelo_up:
            return "Bera", "Sbr 150"

        if "NKD" in modelo_up:
            return "Akt", "Nkd 125"
        if "BERA" in modelo_up:
            return "Bera", "Sbr 150"
        if "BAJA" in modelo_up:
            return "Bajaj", "Boxer Ct"
        if "SUZUKI" in modelo_up:
            return "Suzuki", "GN"

        return None, None

    def detectar_modelo(self, modelo):
        modelo = modelo or ""

        for year in range(2018, 2027):
            if str(year) in modelo:
                return str(year)

        return None

    def normalizar_color(self, color):
        color = self.nom_propio(color)
        return color if color in COLORES_VALIDOS else "Negro"

    def log_omitido(self, data, razon):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"PLACA={data.get('placa')} | "
                f"MODELO_EXT='{data.get('modelo_ext')}' | "
                f"RAZON={razon}\n"
            )

    def handle(self, *args, **options):

        # 🧹 Limpia log anterior
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

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

            if not marca:
                omitidos += 1
                self.log_omitido(data, "Marca no reconocida")
                continue

            # 🎯 Reglas de año
            if marca == "Bera":
                modelo = "2025"
            else:
                modelo = self.detectar_modelo(data["modelo_ext"])
                if not modelo:
                    omitidos += 1
                    self.log_omitido(data, "Modelo (año) no detectado")
                    continue

            defaults = {
                "marca": self.nom_propio(marca),
                "modelo": modelo,
                "serie": self.nom_propio(serie),
                "propietario": self.nom_propio(
                    data["tarjeta_propiedad"]
                ) or "Por Definir",
                "color": self.normalizar_color(data["color"]),
            }

            _, created = Vehiculo.objects.get_or_create(
                placa=(data["placa"] or "").upper().strip(),
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
        self.stdout.write(
            self.style.NOTICE(f"📝 Detalle de omitidos en: {LOG_FILE}")
        )
