import psycopg2

try:
    conexion = psycopg2.connect(
        dbname='postgres',
        user='postgres.ycfjnkfrrobzbsqkwjpo',
        password='Ferremas2025',
        host='aws-0-us-east-2.pooler.supabase.com',
        port='6543'
    )
    print("Conexion exitosa a Supabase.")
    conexion.close()
except Exception as e:
    print("Error de conexión:", e)