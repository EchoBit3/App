from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import os
import base64
from typing import Optional
import warnings
# Obtener encryption key de entorno
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generar key temporal para desarrollo (NO USAR EN PRODUCCIÓN)
    warnings.warn(
        "ADVERTENCIA: ENCRYPTION_KEY no configurada. Usando clave temporal. "
        "Los datos no estarán protegidos entre reinicios. "
        "Define ENCRYPTION_KEY en .env para producción."
    )
    # Key temporal basada en SECRET_KEY si existe
    secret = os.getenv("SECRET_KEY", "dev-temp-key-not-secure")
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'demystify-salt-2025',
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    ENCRYPTION_KEY = key.decode()
# Inicializar cipher
cipher_suite = Fernet(ENCRYPTION_KEY.encode())
def encrypt_data(plaintext: Optional[str]) -> Optional[str]:
    if plaintext is None or plaintext == "":
        return None
    try:
        encrypted = cipher_suite.encrypt(plaintext.encode())
        return encrypted.decode()
    except Exception as e:
        warnings.warn(f"Error al encriptar datos: {str(e)}")
        return plaintext  # Fallback: devolver sin encriptar
def decrypt_data(ciphertext: Optional[str]) -> Optional[str]:
    if ciphertext is None or ciphertext == "":
        return None
    try:
        decrypted = cipher_suite.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception as e:
        # Si falla la desencriptación, probablemente el dato no está encriptado
        # (migración de datos antiguos)
        warnings.warn(f"Error al desencriptar datos: {str(e)}")
        return ciphertext  # Fallback: devolver tal cual
def encrypt_email(email: str) -> str:
    if not email:
        return ""
    # Encriptar el email completo
    encrypted = encrypt_data(email)
    return encrypted if encrypted else email
def decrypt_email(encrypted_email: str) -> str:
    if not encrypted_email:
        return ""
    return decrypt_data(encrypted_email) or encrypted_email
def generate_encryption_key() -> str:
    key = Fernet.generate_key()
    return key.decode()
def is_encryption_configured() -> bool:
    return bool(os.getenv("ENCRYPTION_KEY"))
# Utilidad para CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "generate-key":
        print("\nNueva ENCRYPTION_KEY generada:")
        print(f"\n{generate_encryption_key()}\n")
        print("Agrega esta key a tu archivo .env:")
        print("ENCRYPTION_KEY=<key-generada-arriba>\n")
    else:
        print("Uso: python encryption.py generate-key")