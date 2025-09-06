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
                return False
    
    elif campo == "id_libro":
        if not lex.startswith("LIB"):
            reporte_error(linea_num, 1, lex[:3], campo)
            return False
        
    elif campo in ("fecha_prestamo", "fecha_devolucion"):
        if lex == "" and campo == "fecha_devolucion":
            return True
        for i, c in enumerate(lex):
            if not (c.isdigit() or c == "-"):
                reporte_error(linea_num, i+1, c, campo)
                return False
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
    if posicion == 0 and lexema.isdigit() and len(lexema) == 4:
        return "id_usuario"

    if posicion == 1 and all(c.isalpha() or c in "áéíóúÁÉÍÓÚñÑ. " for c in lexema):
        return "nombre_usuario"

    if posicion == 2 and lexema.startswith("LIB") and lexema[3:].isdigit() and len(lexema[3:]) == 3:
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
            return "fecha_devolucion"
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
    else:
        tokens.append((clasificar_lexema("", posicion), ""))
    return tokens

#validar línea completa
def validar_linea(tokens, linea, num_linea):
    tipos = [t[0] for t in tokens if t[0] != "coma"]
    valores = [t[1] for t in tokens if t[0] != "coma"]

    if len(valores) != 6:
        print(f"inválido: cantidad incorrecta de campos en linea {num_linea}, se esperaban 6 campos, se encontraron {len(valores)}.")
        return None

    if "desconocido" in tipos:
        dir=tipos.index("desconocido")
        print(f"Inválido: lexema inválido '{valores[dir]}' en linea {num_linea}, posición {dir+1}.")
        return None
    
    if tipos != orden_valido:
        print(f"inválido: orden de tokens inválido en línea {num_linea}; se obtuvo {tipos}, y se esperaban {orden_valido}.")
        return None
    
    for campo, valor in zip(orden_valido, valores):
        if not validar_campo(valor, campo, num_linea):
            return None
    
    fecha_prestamo = valores[4]
    fecha_devolucion = valores[5]

    if fecha_devolucion.strip():  # Si existe fecha_devolucion
        f_prestamo = datetime.strptime(fecha_prestamo, "%Y-%m-%d")
        f_devolucion = datetime.strptime(fecha_devolucion, "%Y-%m-%d")

        if f_prestamo > f_devolucion:
            print(f"Error semántico: línea {num_linea}, la fecha de préstamo "
                f"'{fecha_prestamo}' es posterior a la fecha de devolución "
                f"'{fecha_devolucion}'.")
            return None
    else:
        pass
    return valores

###

def leer_archivo(nombre_archivo, usuarios: dict[str, str], libros: dict[str,str]):
    prestamos = []
    try: 
        with open(nombre_archivo, "r", encoding="utf-8") as f:
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
    except FileNotFoundError: 
        print(f"\nNo existe el archivo: '{nombre_archivo}'")
    return prestamos
    

#Cargar usuarios y catalogo de libros
def cargar_archivo(nombre_archivo):
    datos = {}
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            encabezado = f.readline().strip()
            lineas_leidas = 1

            # Detectar tipo de archivo según encabezado
            if encabezado == "id_usuario,nombre_usuario":
                clave_campo, valor_campo = "id_usuario", "nombre_usuario"
            elif encabezado == "id_libro,titulo_libro":
                clave_campo, valor_campo = "id_libro", "titulo_libro"
            else:
                print(f"Error: Campos inválidos '{encabezado}' en archivo '{nombre_archivo}'. (Línea {lineas_leidas})")
                return None
            
            for linea in f:
                lineas_leidas += 1
                partes = linea.strip().split(",")
                if len(partes) != 2:
                    print(f"Inválido: Cantidad incorrecta de campos en línea {lineas_leidas}, se esperaban 2, se encontraron {len(partes)}.")
                    continue
                
                clave, valor = partes[0].strip(), partes[1].strip()

                # Validar que la clave y valor coincida con los campos
                if not (validar_campo(clave, clave_campo, lineas_leidas) and 
                        validar_campo(valor, valor_campo, lineas_leidas)):
                    print(f"Inválido: Datos no coinciden con campos ('{clave_campo}', '{valor_campo}') esperados. (Línea {lineas_leidas})")
                    continue
                
                # Verificar duplicados
                if clave in datos:
                    print(f"Inválido: ID '{clave}' ya registrado. (Línea {lineas_leidas}: '{linea.strip()}').")
                    continue

                datos[clave] = valor
    except FileNotFoundError: 
        print(f"\nNo existe el archivo: '{nombre_archivo}'")
    
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
def prestamos_vencidos(prestamos, fecha_actual):
    print("\nPRÉSTAMOS VENCIDOS")

    fecha_actual = datetime.strptime(fecha_actual, "%Y-%m-%d") 
    for p in prestamos:
        fecha_devolucion = p["fecha_devolucion"]

        if not fecha_devolucion:  
            continue  

        fecha_devolucion = datetime.strptime(fecha_devolucion, "%Y-%m-%d")

        if fecha_devolucion < fecha_actual:
            print(p)  # préstamo vencido


#plantilla documetno HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 20px;
        }}
        h1 {{
            text-align: center;
            color: #E3AAAA;
        }}
        table {{
            border-collapse: collapse;
            width: 90%;
            margin: auto;
            background: white;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }}
        th {{
            background-color: #9E366D;
            color: white;
        }}
    </style>
</head>
<body>
    <h1>{titulo}</h1>
    <table>
        <thead>
            <tr>{encabezados}</tr>
        </thead>
        <tbody>
            {filas}
        </tbody>
    </table>
    <div class="footer">
        Generado automáticamente el {fecha}
    </div>
</body>
</html>
"""

#manejo de HTML, carga de reportes
def exportar_html(nombre_archivo, titulo, encabezados, datos):
    filas_html = ""
    for fila in datos:
        celdas = "".join(f"<td>{col}</td>" for col in fila)
        filas_html += f"<tr>{celdas}</tr>\n"

    encabezados_html = "".join(f"<th>{col}</th>" for col in encabezados)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = HTML_TEMPLATE.format(
        titulo=titulo,
        encabezados=encabezados_html,
        filas=filas_html,
        fecha=fecha_actual
    )

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Reporte '{titulo}' exportado como {nombre_archivo}")

def exportar_historial(prestamos):
    datos = [[p["id_usuario"], p["nombre_usuario"], p["id_libro"], p["titulo_libro"], p["fecha_prestamo"], p["fecha_devolucion"] or "Pendiente"] for p in prestamos]
    exportar_html("reporte_historial.html", "Historial de Préstamos",
                  ["ID Usuario", "Nombre Usuario", "ID Libro", "Título Libro", "Fecha Préstamo", "Fecha Devolución"], datos)


def exportar_usuarios(prestamos):
    usuarios = {p["id_usuario"]: p["nombre_usuario"] for p in prestamos}
    datos = [[uid, nombre] for uid, nombre in usuarios.items()]
    exportar_html("reporte_usuarios.html", "Listado de Usuarios",
                  ["ID Usuario", "Nombre Usuario"], datos)


def exportar_libros(prestamos):
    libros = {p["id_libro"]: p["titulo_libro"] for p in prestamos}
    datos = [[lid, titulo] for lid, titulo in libros.items()]
    exportar_html("reporte_libros.html", "Listado de Libros Prestados",
                  ["ID Libro", "Título Libro"], datos)


def exportar_estadisticas(prestamos):
    from collections import Counter
    usuarios = Counter(p["id_usuario"] for p in prestamos)
    libros = Counter(p["id_libro"] for p in prestamos)
    total = len(prestamos)
    mas_activo = max(usuarios, key=usuarios.get)
    mas_prestado = max(libros, key=libros.get)

    datos = [
        ["Total préstamos", total],
        ["Usuario más activo", f"{mas_activo} ({usuarios[mas_activo]} préstamos)"],
        ["Libro más prestado", f"{mas_prestado} ({libros[mas_prestado]} préstamos)"],
        ["Usuarios únicos", len(usuarios)]
    ]
    exportar_html("reporte_estadisticas.html", "Estadísticas",
                  ["Métrica", "Valor"], datos)


def exportar_vencidos(prestamos, fecha_actual):
    fecha_actual = datetime.strptime(fecha_actual, "%Y-%m-%d")
    vencidos = []
    for p in prestamos:
        if p["fecha_devolucion"]:
            devol = datetime.strptime(p["fecha_devolucion"], "%Y-%m-%d")
            if devol < fecha_actual:
                vencidos.append([p["id_usuario"], p["id_libro"], p["titulo_libro"], p["fecha_prestamo"], p["fecha_devolucion"]])

    exportar_html("reporte_vencidos.html", "Préstamos Vencidos",
                  ["ID Usuario", "ID Libro", "Título", "Fecha Préstamo", "Fecha Devolución"], vencidos)

# Colores y estilos ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
PURPLE = "\033[35m"
PINK = "\033[95m"
CYAN = "\033[36m"

def mostrar_menu():
    print("\n" + "="*50)
    print(f"{BOLD}{PINK}BIBLIOTECA DIGITAL{RESET}".center(50))
    print("="*50)
    print(f"{YELLOW}1.{RESET} Cargar usuarios")
    print(f"{YELLOW}2.{RESET} Cargar libros")
    print(f"{YELLOW}3.{RESET} Cargar registro de préstamos desde archivo")
    print(f"{YELLOW}4.{RESET} Mostrar historial de préstamos")
    print(f"{YELLOW}5.{RESET} Mostrar listado de usuarios únicos")
    print(f"{YELLOW}6.{RESET} Mostrar listado de libros prestados")
    print(f"{YELLOW}7.{RESET} Mostrar estadísticas de préstamos")
    print(f"{YELLOW}8.{RESET} Mostrar préstamos vencidos")
    print(f"{YELLOW}9.{RESET} Exportar todos los reportes a HTML")
    print(f"{RED}0.{RESET} Salir")
    print("="*50)

def main():
    usuarios = {}
    libros = {}
    prestamos = []

    while True:
        mostrar_menu()
        opcion = input(f"{ITALIC}Seleccione una opción: {RESET}")

        match opcion:
            case "1":
                archivo_usuarios = input(f"{ITALIC}Ingrese el nombre del archivo de usuarios: {RESET}")
                usuarios = cargar_archivo(archivo_usuarios)
                print(f"{GREEN}Usuarios cargados: {len(usuarios)}{RESET}")
                for u in usuarios:
                    print(f"- {u}: {usuarios[u]}")

            case "2":
                archivo_libros = input(f"{ITALIC}Ingrese el nombre del archivo de libros: {RESET}")
                libros = cargar_archivo(archivo_libros)
                print(f"{GREEN}Libros cargados: {len(libros)}{RESET}")

            case "3":
                archivo_prestamos = input(f"{ITALIC}Ingrese el archivo de préstamos (.lfa): {RESET}")
                prestamos = leer_archivo(archivo_prestamos, usuarios, libros)
                print(f"{GREEN}Préstamos cargados: {len(prestamos)}{RESET}")

            case "4":
                if prestamos:
                    historial_prestamos(prestamos)
                else:
                    print(f"{YELLOW}{ITALIC}No existen préstamos cargados{RESET}")

            case "5":
                if prestamos:
                    listado_usuarios(prestamos)
                else:
                    print(f"{YELLOW}{ITALIC}No existen préstamos cargados{RESET}")

            case "6":
                if prestamos:
                    listado_libros(prestamos)
                else:
                    print(f"{YELLOW}{ITALIC}No existen préstamos cargados{RESET}")

            case "7":
                if prestamos:
                    estadisticas(prestamos)
                else:
                    print(f"{YELLOW}{ITALIC}No existen préstamos cargados{RESET}")

            case "8":
                if prestamos:
                    fecha = datetime.now().strftime("%Y-%m-%d")
                    print(f"{PURPLE}Usando la fecha actual del sistema: {fecha}{RESET}")
                    prestamos_vencidos(prestamos, fecha)
                else:
                    print(f"{YELLOW}{ITALIC}No existen préstamos cargados{RESET}")

            case "9":
                if prestamos:
                    exportar_historial(prestamos)
                    exportar_usuarios(prestamos)
                    exportar_libros(prestamos)
                    exportar_estadisticas(prestamos)
                    fecha = datetime.now().strftime("%Y-%m-%d")
                    exportar_vencidos(prestamos, fecha)
                    print(f"{GREEN}Reportes exportados a HTML.{RESET}")
                else:
                    print(f"{YELLOW}{ITALIC}No existen préstamos cargados{RESET}")

            case "0":
                print(f"{RED}{BOLD}Saliendo del sistema...{RESET}")
                break

            case _:
                print(f"{RED}{ITALIC}Opción inválida. Intente de nuevo.{RESET}")

if __name__ == "__main__":
    main()


