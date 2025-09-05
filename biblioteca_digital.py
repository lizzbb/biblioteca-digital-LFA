from datetime import datetime
from tkinter import TRUE

#tokens
TOKENS = {
    "id_usuario": "ID de Usuario",
    "nombre_usuario": "Nombre del Usuario",
    "id_libro": "ID del Libro",
    "titulo_libro": "Título del Libro",
    "fecha_prestamo": "Fecha de Préstamo",
    "fecha_devolucion": "Fecha de Devolución",
    "coma": "Separador",
    "desconocido": "Símbolo no reconocido"
}

orden_valido=["id_usuario", "nombre_usuario", "id_libro", "titulo_libro", "fecha_prestamo", "fecha_devolucion"]

#validación de tokens

#devolución de error en documento
def reporte_error (linea_num, col_num, char, contexto):
    print(f"Error léxico: línea '{linea_num}', columna '{col_num}', carácter '{char}' inválido en campo {contexto}")

def validar_campo(lexema, campo, linea_num) -> bool:
    letras_validas="abcdefghijklmnopqrstuvwxyzáéíóúñ "
    lex=lexema.strip()

    if campo == "id_usuario":
        for i, c in enumerate(lex):
            if not c.isdigit():
                reporte_error(linea_num, i+1, c, campo)
                return False
    elif campo == "nombre_usuario":
        for i, c in enumerate(lex.lower()):
            if c not in letras_validas:
                reporte_error(linea_num, i+1, c, campo)
    
    elif campo == "id:libro":
        if not lex.startswith("LIB"):
            reporte_error(linea_num, 1, lex[:3], campo)
            return False
        
    elif campo in ("fecha_prestamo", "fecha_devolucion"):
        if lex == "" and campo == "fecha_devolucion":
            return True
        for i, c in enumerate(lex):
            if not (c.isdigit() or c == "-"):
                reporte_error(linea_num, i+1, c, campo)
        try:
            datetime.strptime(lex, "%Y-%m-%d")
        except ValueError:
                print(f"Error semántico: línea '{linea_num}', '{lex}' no cumple YYYY-MM-DD en {campo}")
                return False
    
    elif campo == "titulo_libro":
        if "," in lex:
            idx = lex.index(",") + 1
            reporte_error(linea_num, idx, ",", campo)
            return False
    return True

#clasificar lexemas
def clasificar_lexema(lexema, posicion):
    if posicion == 0 and lexema.isdigit() and len(lexema) >= 4:
        return "id_usuario"

    if posicion == 1 and all(c.isalpha() or c in "áéíóúÁÉÍÓÚñÑ. " for c in lexema):
        return "nombre_usuario"

    if posicion == 2 and lexema.startswith("LIB") and lexema[3:].isdigit() and len(lexema[3:]) >= 3:
        return "id_libro"

    if posicion == 3 and (any(c.isalpha() for c in lexema) or any(c.isdigit() for c in lexema)):
        return "titulo_libro"

    if posicion == 4:
        try:
            datetime.strptime(lexema, "%Y-%m-%d")
            return "fecha_prestamo"
        except ValueError:
            return "desconocido"

    if posicion == 5:
        if lexema.strip() == "":
            return "VACIO"
        try:
            datetime.strptime(lexema, "%Y-%m-%d")
            return "fecha_devolucion"
        except ValueError:
            return "desconocido"

    return "desconocido"

#simulador de análisis léxico
def analizador_lexico(linea):
    lexema = ""
    tokens = []
    posicion = 0

    for c in linea:
        if c == ",":
            if lexema.strip():
                tokens.append((clasificar_lexema(lexema.strip(), posicion), lexema.strip()))
                posicion+=1
            tokens.append(("coma", ","))
            lexema = ""
        else:
            lexema += c
    if lexema.strip():
        tokens.append((clasificar_lexema(lexema.strip(), posicion), lexema.strip()))
    return tokens

#validar línea completa
def validar_linea(tokens, linea, num_linea):
    tipos = [t[0] for t in tokens if t[0] != "coma"]
    valores = [t[1] for t in tokens if t[0] != "coma"]

    if len(valores) != 6:
        print(f"inválido: cantidad incorrecta de campos en linea {num_linea}, se esperaban 6 campos, se encontraron {len(valores)}.")
        return None

    if "desconcoido" in tipos:
        dir=tipos.index("desconocido")
        print(f"Inválido: lexema inválido '{valores[dir]}' en linea {num_linea}posición {dir+1}.")
        return None
    
    if tipos != orden_valido:
        print(f"inválido: orden de tokens inváñido en línea {num_linea}; se obtuvo {tipos}, y se esperaban {orden_valido}.")
        return None
    
    for campo, valor in zip(orden_valido, valores):
        if not validar_campo(valor, campo, num_linea):
            return None
    
    return valores

###

def leer_archivo(nombre_archivo, usuarios: dict[str, str], libros: dict[str,str]):
    prestamos = []
    with open(nombre_archivo, "r") as f:
        encabezado = f.readline()  # ignorar encabezado
        lineas_leidas = 1
        for linea in f:
            lineas_leidas += 1
            tokens = analizador_lexico(linea.strip()) #clasificación de tokens
            valores = validar_linea(tokens, linea, lineas_leidas)
            if not valores:
                continue  # descartar línea inválida

            id_usuario, nombre_usuario, id_libro, titulo_libro_libro, fecha_prestamo, fecha_devolucion = valores
            fecha_devolucion = fecha_devolucion if fecha_devolucion != "" else None

            # Verificación de usuario
            if id_usuario not in usuarios: 
                print(f"inválido: Usuario '{id_usuario}' no registrado. (Línea {lineas_leidas})")
                continue
            if usuarios[id_usuario] != nombre_usuario: 
                print(f"inválido: nombre_usuario '{nombre_usuario}' no coincide con registro de '{id_usuario}'. (Línea {lineas_leidas})")
                continue

            # Verificación de libro
            if id_libro not in libros: 
                print(f"inválido: Libro '{id_libro}' no registrado. (Línea {lineas_leidas})")
                continue
            if libros[id_libro] != titulo_libro_libro: 
                print(f"Error: titulo_libro '{titulo_libro_libro}' no coincide con registro de '{id_libro}'. (Línea {lineas_leidas})")
                continue

            prestamos.append({
                "id_usuario": id_usuario,
                "nombre_usuario": nombre_usuario,
                "id_libro": id_libro,
                "titulo_libro": titulo_libro_libro,
                "fecha_prestamo": fecha_prestamo,
                "fecha_devolucion": fecha_devolucion
            })

    return prestamos

#Cargar usuarios y catalogo de libros
def cargar_archivo(nombre_archivo):
    datos = {}

    with open(nombre_archivo, "r", encoding="utf-8") as f:
        encabezado = f.readline()  # ignorar encabezado
        lineas_leidas = 1
        for linea in f:
            lineas_leidas += 1
            partes = linea.strip().split(",")
            if len(partes) != 2:
                print(f"Inválido: cantidad incorrecta de campos en línea {lineas_leidas}, se esperaban 2, se encontraron {len(partes)}.")
                continue

            clave, valor = partes[0].strip(), partes[1].strip()

            if clave in datos:
                print(f"Inválido: ID '{clave}' ya registrado. (Línea {lineas_leidas}: '{linea.strip()}').")
                continue

            datos[clave] = valor

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
def prestamos_vencidos(prestamos):
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
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

    # Reportes en consola
    historial_prestamos(prestamos)
    listado_usuarios(prestamos)
    listado_libros(prestamos)
    estadisticas(prestamos)
    prestamos_vencidos(prestamos)

if __name__ == "__main__":
    main()
