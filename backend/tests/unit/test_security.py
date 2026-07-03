from security import hash_password, verify_password


class TestHashPassword:
    def test_formato_del_hash(self):
        resultado = hash_password("clave123")
        partes = resultado.split("$")
        assert len(partes) == 4
        assert partes[0] == "pbkdf2_sha256"

    def test_dos_hashes_del_mismo_password_son_distintos(self):
        h1 = hash_password("clave123")
        h2 = hash_password("clave123")
        assert h1 != h2  # salt aleatorio


class TestVerifyPassword:
    def test_password_correcto(self):
        stored = hash_password("clave123")
        assert verify_password(stored, "clave123") is True

    def test_password_incorrecto(self):
        stored = hash_password("clave123")
        assert verify_password(stored, "otra-clave") is False

    def test_ambos_hashes_verifican_correctamente(self):
        h1 = hash_password("clave123")
        h2 = hash_password("clave123")
        assert verify_password(h1, "clave123") is True
        assert verify_password(h2, "clave123") is True

    def test_hash_corrupto_sin_separadores(self):
        assert verify_password("esto-no-es-un-hash-valido", "clave123") is False

    def test_hash_con_campos_faltantes(self):
        assert verify_password("pbkdf2_sha256$260000", "clave123") is False

    def test_metodo_desconocido(self):
        stored = hash_password("clave123").replace("pbkdf2_sha256", "md5")
        assert verify_password(stored, "clave123") is False

    def test_iteraciones_no_numericas_no_lanza_excepcion(self):
        assert verify_password("pbkdf2_sha256$abc$c2FsdA==$ZGs=", "clave123") is False

    def test_salt_no_base64_no_lanza_excepcion(self):
        assert verify_password("pbkdf2_sha256$1000$***$***", "clave123") is False
