# ----------------------------
# Variables
# ----------------------------
$DATABASE_URL = "postgresql://postgres:tSOTklzLYfQQZiXxFZIcAPtZkDJxdKgN@metro.proxy.rlwy.net:30259/railway"

# ----------------------------
# Función para ejecutar SQL en remoto
# ----------------------------
function Exec-SQL($sql) {
    $escapedSql = $sql -replace '"', '\"'
    psql $DATABASE_URL -c "$escapedSql"
}

# ----------------------------
# 1️⃣ Limpiar migraciones antiguas de la app almacen
# ----------------------------
Write-Host "🔹 Limpiando registros de migraciones de la app almacen..."
Exec-SQL "DELETE FROM django_migrations WHERE app='almacen';"

# ----------------------------
# 2️⃣ Borrar tabla vieja si existe
# ----------------------------
Write-Host "🔹 Borrando tablas huérfanas..."
Exec-SQL "DROP TABLE IF EXISTS almacen_movimientoinventario;"
Exec-SQL "DROP SEQUENCE IF EXISTS almacen_movimientoinventario_id_seq;"

# ----------------------------
# 3️⃣ Crear migraciones locales
# ----------------------------
Write-Host "🔹 Creando migraciones locales de la app almacen..."
python manage.py makemigrations almacen

# ----------------------------
# 4️⃣ Aplicar migraciones en DB remota
# ----------------------------
Write-Host "🔹 Aplicando migraciones en la DB remota..."
python manage.py migrate

# ----------------------------
# 5️⃣ Recolectar archivos estáticos
# ----------------------------
Write-Host "🔹 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

Write-Host "✅ ¡Deploy completado! Tu app almacen está lista y funcionando."
