import sys
from pathlib import Path
# Agregar el directorio backend al path
sys.path.append(str(Path(__file__).parent))
from database import SessionLocal, Usuario, Consulta, engine, Base
from encryption import encrypt_email, encrypt_data, is_encryption_configured
from sqlalchemy import inspect
import warnings
def check_if_migration_needed():
    """
    Verifica si la migración ya se realizó
    """
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('usuarios')]
    # Si ya tiene las columnas con _ es que ya migró el schema
    return '_email' not in columns
def migrate_existing_data():
    """
    Encripta datos de usuarios y consultas existentes
    """
    if not is_encryption_configured():
        print("ADVERTENCIA: ENCRYPTION_KEY no configurada.")
        print("   Los datos se encriptarán con key temporal.")
        print("   Configura ENCRYPTION_KEY en .env antes de continuar.")
        response = input("\n¿Continuar de todos modos? (sí/no): ")
        if response.lower() not in ['sí', 'si', 'yes', 'y']:
            print("Migración cancelada")
            return
    print("\nIniciando migración de datos...")
    print("=" * 50)
    db = SessionLocal()
    try:
        # Verificar si necesita migración de schema
        if check_if_migration_needed():
            print("\nEl schema de la BD necesita actualizarse primero.")
            print("   Ejecuta: python -c 'from database import init_db; init_db()'")
            return
        # Contar registros
        total_usuarios = db.query(Usuario).count()
        total_consultas = db.query(Consulta).count()
        print(f"\nEncontrados:")
        print(f"   - {total_usuarios} usuarios")
        print(f"   - {total_consultas} consultas")
        if total_usuarios == 0 and total_consultas == 0:
            print("\nNo hay datos para migrar")
            return
        print(f"\nEncriptando datos...")
        # Migrar usuarios
        usuarios_migrados = 0
        for usuario in db.query(Usuario).all():
            try:
                # Los hybrid properties se encargan de la encriptación automáticamente
                # Solo necesitamos hacer commit
                db.commit()
                usuarios_migrados += 1
                if usuarios_migrados % 10 == 0:
                    print(f"   Procesados {usuarios_migrados}/{total_usuarios} usuarios...")
            except Exception as e:
                print(f"   Error en usuario {usuario.id}: {str(e)}")
                db.rollback()
        print(f"   OK: {usuarios_migrados} usuarios encriptados")
        # Migrar consultas
        consultas_migradas = 0
        for consulta in db.query(Consulta).all():
            try:
                # Los hybrid properties se encargan de la encriptación
                db.commit()
                consultas_migradas += 1
                if consultas_migradas % 50 == 0:
                    print(f"   Procesadas {consultas_migradas}/{total_consultas} consultas...")
            except Exception as e:
                print(f"   Error en consulta {consulta.id}: {str(e)}")
                db.rollback()
        print(f"   OK: {consultas_migradas} consultas encriptadas")
        print("\n" + "=" * 50)
        print("Migración completada exitosamente")
        print(f"\nResumen:")
        print(f" - Usuarios: {usuarios_migrados}/{total_usuarios}")
        print(f" - Consultas: {consultas_migradas}/{total_consultas}")
        print(f"\nIMPORTANTE: Guarda tu ENCRYPTION_KEY de forma segura")
        print(f" Sin ella, no podrás desencriptar los datos")
    except Exception as e:
        print(f"\nError en migración: {str(e)}")
        db.rollback()
    finally:
        db.close()
def verify_encryption():
    """
    Verifica que los datos estén correctamente encriptados
    """
    print("\nVerificando encriptación...")
    print("=" * 50)
    db = SessionLocal()
    try:
        # Verificar un usuario
        usuario = db.query(Usuario).first()
        if usuario:
            print(f"\nUsuario de prueba:")
            print(f"   Username: {usuario.username}")
            print(f"   Email (desencriptado): {usuario.email}")
            email_bd = usuario._email[:50] + "..." if len(usuario._email) > 50 else usuario._email
            print(f"   Email (en BD): {email_bd}")
            print(f"   Nombre: {usuario.nombre_completo}")
            # Verificar que efectivamente está encriptado
            if usuario._email and not usuario._email.startswith("gAAAAA"):
                print(f"\nAdvertencia: El email podría no estar encriptado")
            else:
                print(f"\nEmail correctamente encriptado")
        # Verificar una consulta
        consulta = db.query(Consulta).first()
        if consulta:
            print(f"\nConsulta de prueba:")
            print(f"   Texto (desencriptado): {consulta.texto_original[:50]}...")
            print(f"   Texto (en BD): {consulta._texto_original[:50]}...")
            if consulta._texto_original and not consulta._texto_original.startswith("gAAAAA"):
                print(f"\nAdvertencia: El texto podría no estar encriptado")
            else:
                print(f"\nTexto correctamente encriptado")
        print("\n" + "=" * 50)
        print("Verificación completada")
    except Exception as e:
        print(f"\nError en verificación: {str(e)}")
    finally:
        db.close()
if __name__ == "__main__":
    print("\nMIGRACIÓN DE DATOS - ENCRIPTACIÓN")
    print("=" * 50)
    if len(sys.argv) > 1:
        if sys.argv[1] == "verify":
            verify_encryption()
        elif sys.argv[1] == "migrate":
            migrate_existing_data()
        else:
            print("Uso:")
            print("  python migrate_encryption.py migrate  - Encripta datos existentes")
            print("  python migrate_encryption.py verify   - Verifica encriptación")
    else:
        print("\nEste script encriptará todos los datos sensibles en la base de datos.")
        print("\n ADVERTENCIAS:")
        print("   1. Haz un backup de demystify.db antes de continuar")
        print("   2. Asegúrate de tener ENCRYPTION_KEY configurada en .env")
        print("   3. Guarda la ENCRYPTION_KEY en un lugar seguro")
        print("   4. Esta operación NO se puede deshacer sin el backup")
        print("\nUso:")
        print("  python migrate_encryption.py migrate  - Encripta datos existentes")
        print("  python migrate_encryption.py verify   - Verifica encriptación")