#tokens
TOKENS = {
    "ID_USUARIO": "ID de Usuario",
    "NOMBRE": "Nombre del Usuario",
    "ID_LIBRO": "ID del Libro",
    "TITULO": "Título del Libro",
    "FECHA": "Fecha",
    "COMA": "Separador",
    "DESCONOCIDO": "Símbolo no reconocido"
}

def clasificar_lexema(lexema):
    if lexema.isdigit():
        return "ID_USUARIO"
    elif lexema.startswith("LIB"):
        return "ID_LIBRO"
    elif "-" in lexema and len(lexema) == 10:
        return "FECHA"
    elif all(c.isalpha() or c in "áéíóúÁÉÍÓÚñÑ." or c.isspace() for c in lexema):
        return "NOMBRE" if " " in lexema else "TITULO"
    elif lexema == ",":
        return "COMA"
    else:
        return "DESCONOCIDO"

def analizador_lexico(linea):
    lexema = ""
    tokens = []
    for c in linea:
        if c == ",":
            if lexema.strip():
                tokens.append((clasificar_lexema(lexema.strip()), lexema.strip()))
            tokens.append(("COMA", ","))
            lexema = ""
        else:
            lexema += c
    if lexema.strip():
        tokens.append((clasificar_lexema(lexema.strip()), lexema.strip()))
    return tokens

def leer_archivo(nombre_archivo):
    prestamos = []
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        encabezado = f.readline()  # ignorar encabezado
        for linea in f:
            tokens = analizador_lexico(linea.strip())
            valores = [t[1] for t in tokens if t[0] != "COMA"]
            if len(valores) == 6:
                prestamos.append({
                    "id_usuario": valores[0],
                    "nombre_usuario": valores[1],
                    "id_libro": valores[2],
                    "titulo_libro": valores[3],
                    "fecha_prestamo": valores[4],
                    "fecha_devolucion": valores[5] if valores[5] != "" else None
                })
    return prestamos

#Préstamos
def historial_prestamos(prestamos):
    print("\nHISTORIAL DE PRÉSTAMOS")
    for p in prestamos:
        print(p)

#Listado usuarios
def listado_usuarios(prestamos):
    print("\nLISTADO DE USUARIOS")
    usuarios = {p["id_usuario"]: p["nombre_usuario"] for p in prestamos}
    for uid, nombre in usuarios.items():
        print(uid, "-", nombre)

#Listado Libros 
def listado_libros(prestamos):
    print("\nLIBROS PRESTADOS")
    libros = {p["id_libro"]: p["titulo_libro"] for p in prestamos}
    for lid, titulo in libros.items():
        print(lid, "-", titulo)

def estadisticas(prestamos):
    print("\nESTADÍSTICAS")
    total = len(prestamos)
    usuarios = {p["id_usuario"]: 0 for p in prestamos}
    libros = {p["id_libro"]: 0 for p in prestamos}
    for p in prestamos:
        usuarios[p["id_usuario"]] += 1
        libros[p["id_libro"]] += 1
    mas_activo = max(usuarios, key=usuarios.get)
    mas_prestado = max(libros, key=libros.get)
    print("Total préstamos:", total)
    print("Usuario más activo:", mas_activo)
    print("Libro más prestado:", mas_prestado)
    print("Usuarios únicos:", len(usuarios))

#Vencidos
def prestamos_vencidos(prestamos, fecha_actual="2025-07-15"):
    print("\nPRÉSTAMOS VENCIDOS")
    for p in prestamos:
        if p["fecha_devolucion"] and p["fecha_devolucion"] < fecha_actual:
            print(p)


def main():
    archivo = "prestamos.txt"
    prestamos = leer_archivo(archivo)

    historial_prestamos(prestamos)
    listado_usuarios(prestamos)
    listado_libros(prestamos)
    estadisticas(prestamos)
    prestamos_vencidos(prestamos)

if __name__ == "__main__":
    main()
"""
up 3-09 ml 
"""
