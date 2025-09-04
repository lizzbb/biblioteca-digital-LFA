from datetime import datetime

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
    if lexema.isdigit() and len(lexema) == 4:
        return "ID_USUARIO"
    elif lexema.startswith("LIB") and lexema[3:].isdigit() and len(lexema) == 6:
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

def leer_archivo(nombre_archivo, usuarios: dict[str, str], libros: dict[str,str]):
    prestamos = []
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        encabezado = f.readline()  # ignorar encabezado
        lineas_leidas = 1
        for linea in f:
            lineas_leidas += 1
            tokens = analizador_lexico(linea.strip()) #clasificación de tokens
            valores = [t[1] for t in tokens if t[0] != "COMA"] # asignación de valores en tokens (excluyendo separadores)
            if len(valores) == 6:
                id_usuario, nombre_usuario, id_libro, titulo_libro, fecha_prestamo, fecha_devolucion = valores
                fecha_devolucion = fecha_devolucion if fecha_devolucion != "" else None
                
                # Verificación de usuario
                if id_usuario not in usuarios: 
                    print(f"Error: Usuario '{id_usuario}' no registrado. (Línea {lineas_leidas})")
                    continue
                if usuarios[id_usuario] != nombre_usuario: 
                    print(f"Error: Nombre de usuario '{nombre_usuario}' no coincide con registro para usuario '{id_usuario}'. (Línea {lineas_leidas})")
                    continue

                # Verificación de libro
                if id_libro not in libros: 
                    print(f"Error: Libro '{id_libro}' no registrado. (Línea {lineas_leidas})")
                    continue
                if libros[id_libro] != titulo_libro: 
                    print(f"Error: Titulo '{titulo_libro}' no coincide con registro para libro '{id_libro}'. (Línea {lineas_leidas})")
                    continue

                prestamos.append({
                    "id_usuario": id_usuario,
                    "nombre_usuario": nombre_usuario,
                    "id_libro": id_libro,
                    "titulo_libro": titulo_libro,
                    "fecha_prestamo": fecha_prestamo,
                    "fecha_devolucion": fecha_devolucion
                })

    return prestamos

#Cargar usuarios y catalogo de libros
def cargar_archivo(nombre_archivo):
    datos = {}
    id_unicos = set()

    with open(nombre_archivo, "r", encoding="utf-8") as f:
        encabezado = f.readline()  # ignorar encabezado
        lineas_leidas = 1
        for linea in f:
            lineas_leidas += 1
            tokens = analizador_lexico(linea.strip())
            valores = [t[1] for t in tokens if t[0] != "COMA"]

            if(tokens[0][0] == "ID_USUARIO"):
                if valores[0] in id_unicos: 
                   print(f"ID '{valores[0]}' repetido en linea {lineas_leidas}: '{linea}'.") 
                   continue
                
                id_unicos.add(valores[0])

                datos[valores[0]] = valores[1]

            elif(tokens[0][0] == "ID_LIBRO"):
                if valores[0] in id_unicos: 
                   print(f"ID '{valores[0]}' repetido en linea {lineas_leidas}: '{linea}'.") 
                   continue

                id_unicos.add(valores[0])

                datos[valores[0]] = valores[1]

            else: 
                print(f"Error: token {tokens[0]} no válido. (Línea {lineas_leidas})")
                continue
            
    return datos


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
    archivo_usuarios = "usuarios.txt"
    archivo_libros = "libros.txt"
    archivo = "prueba.lfa"
    usuarios = cargar_archivo(archivo_usuarios)
    libros = cargar_archivo(archivo_libros)
    prestamos = leer_archivo(archivo, usuarios, libros)
    

    for u in usuarios:
        print(f"{u}: {usuarios[u]}")
    
    for l in libros: 
        print(f"{l}: {libros[l]}")

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
