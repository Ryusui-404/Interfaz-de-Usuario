import streamlit as st
from fpdf import FPDF
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import clase_alumno
import clase_maestro
import clase_admin

conexion = sqlite3.connect('prueba4.db')
cursor = conexion.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Registro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dia INTEGER NOT NULL,
    id_mes INTEGER NOT NULL,
    año INTEGER NOT NULL,
    id_materia TEXT NOT NULL,
    asistencia BOOLEAN NOT NULL
);''')

conexion.commit()

def login(user, password) -> int:
    '''
    0. error
    1. admin
    2. maestro
    3. alumno
    '''
    with sqlite3.connect("prueba4.db") as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE no_cuenta = ? AND contraseña = ?", (user, password))
        user = cursor.fetchone()

        if not user:
            return 0, None
        else:
            match user[-1]:
                case 'admin':
                    usuario = clase_admin.Admin()
                    code = 1
                case 'maestro':
                    user_id = user[0]
                    usuario = clase_maestro.Maestro(user_id)    
                    code = 2            
                case 'alumno' : 
                    user_id = user[0]
                    usuario = clase_alumno.Alumno(user_id)
                    code = 3

            usuario.nombre = user[1]
            usuario.apellidop = user[2]
            usuario.apellidom = user[3]
            usuario.id = user[0]
            if usuario.__class__.__name__ == 'Maestro' or usuario.__class__.__name__ == 'Alumno':
                usuario.horario = usuario.generar_horario()
            return code, usuario

def modificar_asistencia(materia_nombre: str, dia: int, mes: int, año: int, asistencia: bool) -> bool:
    try:
        with sqlite3.connect("prueba4.db") as conexion:
            cursor = conexion.cursor()

            cursor.execute('''SELECT id_asignatura FROM Asignaturas 
                              WHERE nombre = ?''', (materia_nombre,))
            id_asignatura = cursor.fetchone()

            if id_asignatura is None:
                st.error(f"No se encontró el id para la materia {materia_nombre}.")
                return False

            cursor.execute('''SELECT * FROM Registro 
                              WHERE dia = ? AND id_mes = ? AND año = ? AND id_materia = ?''', (dia, mes, año, id_asignatura[0]))
            datos = cursor.fetchone()

            if not datos:
                cursor.execute('''INSERT INTO Registro (dia, id_mes, año, id_materia, asistencia) 
                                  VALUES (?, ?, ?, ?, ?)''', (dia, mes, año, id_asignatura[0], asistencia))
            else:
                cursor.execute('''UPDATE Registro 
                                  SET asistencia = ? 
                                  WHERE dia = ? AND id_mes = ? AND año = ? AND id_materia = ?''', (asistencia, dia, mes, año, id_asignatura[0]))

            conexion.commit()
        return True
    except Exception as e:
        st.error(f"Error al modificar la asistencia: {e}")
        return False

    
def horario_clase():
    st.header("Horario de Clases")
    horario = user.generar_horario()

    for i in range(len(horario)):
        for j in range(len(horario[i])):
            if isinstance(horario[i][j], (tuple, list)):
                horario[i][j] = horario[i][j][0]
            elif horario[i][j] is None:
                horario[i][j] = ""

    df_horario = pd.DataFrame(horario, columns=["7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"])
    df_horario.insert(0, "Día", ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"])

    df_horario = df_horario.transpose()
    st.table(df_horario)
    if st.button("Generar PDF de Horario"):
        generar_pdf(df_horario, "horario_clases.pdf")
    return

def horario_maestro():
    horario = user.generar_horario()
    if horario:
        for i in range(len(horario)):
            for j in range(len(horario[i])):
                if isinstance(horario[i][j], (tuple, list)):
                    horario[i][j] = horario[i][j][0]
                elif horario[i][j] is None:
                    horario[i][j] = ""

        df_horario = pd.DataFrame(horario, columns=["7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"])
        df_horario.insert(0, "Día", ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"])

        df_horario = df_horario.transpose()

        st.table(df_horario)
        if st.button("Generar PDF de Horario"):
            generar_pdf(df_horario, "horario_maestro.pdf")
    return

def asistencia_maestro():
    hoy = datetime.now().date()
    fecha_temporal = st.date_input("Seleccione el mes y año", hoy, min_value=hoy - timedelta(days=365), max_value=hoy)

    if user.horario is None:
        st.error("El horario no está disponible para este usuario.")
        return

    asistencia_data = []

    with sqlite3.connect("prueba4.db") as conexion:
        cursor = conexion.cursor()
        
        for dia in range(1, 32):
            try:
                fecha = datetime(fecha_temporal.year, fecha_temporal.month, dia)
                if fecha.weekday() < 5:
                    for materia in user.horario[fecha.weekday()]:
                        if isinstance(materia, (tuple, list)):
                            grupo = materia[0]
                        else:
                            grupo = materia

                        if grupo is not None:
                            cursor.execute('''SELECT id_asignatura FROM Asignaturas 
                                              WHERE nombre = ?''', (id_maestro(),))
                            id_asignatura = cursor.fetchone()

                            if id_asignatura is not None:
                                cursor.execute('''SELECT asistencia FROM Registro 
                                                  WHERE dia = ? AND id_mes = ? AND año = ? AND id_materia = ?''', (dia, fecha_temporal.month, fecha_temporal.year, id_asignatura[0]))
                                asistencia = cursor.fetchone()

                                if asistencia is not None:
                                    asistencia_valor = "A" if asistencia[0] == 1 else "I" if asistencia[0] == 0 else ""
                                else:
                                    asistencia_valor = ""

                            else:
                                asistencia_valor = ""

                            asistencia_data.append((grupo, dia, asistencia_valor))
            except ValueError:
                break

    df_asistencias = pd.DataFrame(asistencia_data, columns=["Grupo", "Día", "Asistencia"])
    st.table(df_asistencias)
    if st.button("Generar PDF de Asistencias"):
        generar_pdf(df_asistencias, "asistencias_maestro.pdf")
    return

def id_maestro():
    if user.id == 1:
        materia_nombre = "Orientación Educativa"
        return materia_nombre
    elif user.id == 2:
        materia_nombre = "Métodos Numéricos"
        return materia_nombre
    elif user.id == 3:
        materia_nombre = "Ecuaciones Diferenciales"
        return materia_nombre
    elif user.id == 4:
        materia_nombre = "Programación Funcional"
        return materia_nombre
    elif user.id == 5:
        materia_nombre = "Estructura de Datos"
        return materia_nombre
    elif user.id == 6:
        materia_nombre = "Interconexión de Redes"
        return materia_nombre
    elif user.id == 7:
        materia_nombre = "Sistemas Digitales y Embebidos"
        return materia_nombre 
    elif user.id == 8:
        materia_nombre = "Inglés III"
        return materia_nombre

def generar_pdf(dataframe, nombre_archivo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=22)
    pdf.cell(0, 10, "REPORTE", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    page_width = 190

    num_columns = len(dataframe.columns) + 1
    column_width = page_width / num_columns
    row_height = 10

    pdf.cell(column_width, row_height, "", 1, 0, 'C')
    for col in dataframe.columns:
        pdf.cell(column_width, row_height, str(col), 1, 0, 'C')
    pdf.ln()

    for index, row in dataframe.iterrows():
        hora_text = str(index)
        wrapped_texts = []
        max_lines = 1
        for col in dataframe.columns:
            item_text = str(row[col]) if pd.notna(row[col]) else ""
            wrapped_texts.append(item_text)
            num_lines = len(pdf.multi_cell(column_width, row_height, item_text, split_only=True))
            max_lines = max(max_lines, num_lines)

        final_row_height = max_lines * row_height

        pdf.cell(column_width, final_row_height, hora_text, 1, 0, 'C')

        for item_text in wrapped_texts:
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.multi_cell(column_width, row_height, item_text, border=1, align='C')
            pdf.set_xy(x + column_width, y)

        pdf.ln(final_row_height)

    pdf.output(nombre_archivo)
    st.success(f"PDF generado: {nombre_archivo}")


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

st.sidebar.header("Iniciar Sesión")
with st.sidebar.form(key='login_form'):
    username = st.text_input("Número de Cuenta", value="", key='username')
    password = st.text_input("Contraseña", type="password", key='password')
    submit_button = st.form_submit_button("Iniciar sesión")

    if submit_button:
        num, user = login(username, password)
        if num != 0:
            st.session_state.logged_in = True
            st.session_state.user = user
        else:
            st.error("Usuario o contraseña incorrectos")

if st.session_state.logged_in:
    user = st.session_state.user
    if isinstance(user, clase_alumno.Alumno):
        st.header("Interfaz de Alumno")
        st.success(f"Bienvenido {user.nombre}")

        horario_clase()

        st.header("Calendario de Asistencias")
        hoy = datetime.now().date()

        fecha_temporal = st.date_input("Seleccione la fecha", hoy, min_value=hoy - timedelta(days=365), max_value=hoy)

        if st.button("Aceptar"):
            if fecha_temporal.weekday() >= 5:
                st.error("No se pueden seleccionar sábados ni domingos.")
            else:
                st.session_state.selected_date = fecha_temporal
        
        if 'selected_date' in st.session_state:
            st.header(f"Materias del día {st.session_state.selected_date}")

            dia = st.session_state.selected_date.weekday()
            materias_del_dia = user.horario[dia]
            
            for index, materia in enumerate(materias_del_dia):
                if isinstance(materia, (tuple, list)):
                    materia_nombre = materia[0]
                else:
                    materia_nombre = materia

                if materia_nombre is None:
                    st.warning("")

                else:
                    with sqlite3.connect("prueba4.db") as conexion:
                        cursor = conexion.cursor()
                        cursor.execute('''SELECT id_asignatura FROM Asignaturas 
                                            WHERE nombre = ?''', (materia_nombre,))
                        id_asignatura = cursor.fetchone()

                        cursor.execute('''SELECT asistencia FROM Registro 
                                        WHERE dia = ? AND id_mes = ? AND año = ? AND id_materia = ?''', (fecha_temporal.day, fecha_temporal.month, fecha_temporal.year, materia_nombre))
                        asistencia = cursor.fetchone()

                    col1, col2, col3, col4 = st.columns(4)

                    if f"asistencia_{materia_nombre}" not in st.session_state:
                        st.session_state[f"asistencia_{materia_nombre}"] = asistencia[0] if asistencia else None

                    with col1:
                        if st.button(f"Marcar Asistencia para {materia_nombre}", key=f"{materia_nombre}-{index}"):
                            if modificar_asistencia(materia_nombre, fecha_temporal.day, fecha_temporal.month, fecha_temporal.year, True):
                                st.session_state[f"asistencia_{materia_nombre}"] = "A"
                                st.session_state.reload_maestro_data = True
                                with col2:
                                    if st.session_state.get(f"asistencia_{materia_nombre}") == "A":
                                        st.success(f"Asistencia marcada para {materia_nombre}")

                    with col3:
                        if st.button(f"Marcar Inasistencia para {materia_nombre}", key=f"quitar-{materia_nombre}-{index}"):
                            if modificar_asistencia(materia_nombre, fecha_temporal.day, fecha_temporal.month, fecha_temporal.year, False):
                                st.session_state[f"asistencia_{materia_nombre}"] = "I"
                                st.session_state.reload_maestro_data = True
                                with col4:
                                    pass
                                    if st.session_state.get(f"asistencia_{materia_nombre}") == "I":
                                        st.success(f"Inasistencia marcada para {materia_nombre}")

    elif isinstance(user, clase_maestro.Maestro):
        st.header("Interfaz de Maestro")
        st.success(f"Bienvenido {user.nombre}")

        if st.session_state.get('reload_maestro_data', False):
            st.session_state.reload_maestro_data = False

        st.header("Horario de Clases")
        horario_maestro()

        st.header("Asistencias del Mes")
        asistencia_maestro()

    elif isinstance(user, clase_admin.Admin):
        st.header("Interfaz de Admin")
        st.success(f"Bienvenido {user.nombre}")

        opciones_vista = ["Horario de Grupo", "Horario de Maestro", "Tabla de Asistencias por Maestro"]
        vista_seleccionada = st.selectbox("Seleccione lo que desea revisar:", opciones_vista)

        if vista_seleccionada == "Horario de Grupo":
            st.header("Horario de Grupo")

            with sqlite3.connect("prueba4.db") as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT id_usuario, nombre, apellido_paterno, apellido_materno FROM Usuarios WHERE rol = 'alumno'")
                alumnos = cursor.fetchall()

            lista_alumnos = [f"{alumno[1]} {alumno[2]} {alumno[3]}" for alumno in alumnos]

            if not lista_alumnos:
                st.warning("No hay alumnos disponibles.")
            else:
                grupo_seleccionado = st.selectbox("Seleccione el grupo:", ["3D"])
                alumno_seleccionado = st.selectbox("Seleccione el alumno:", lista_alumnos)
                user_id = alumnos[lista_alumnos.index(alumno_seleccionado)][0]
                user = clase_alumno.Alumno(user_id)
                horario_clase()

        elif vista_seleccionada == "Horario de Maestro":
            st.header("Horario de Maestro")
            with sqlite3.connect("prueba4.db") as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT id_usuario, nombre, apellido_paterno, apellido_materno FROM Usuarios WHERE rol = 'maestro'")
                maestros = cursor.fetchall()

            lista_maestros = [f"{maestro[1]} {maestro[2]} {maestro[3]}" for maestro in maestros]

            if not lista_maestros:
                st.warning("No hay maestros disponibles.")
            else:
                maestro_seleccionado = st.selectbox("Seleccione el maestro:", lista_maestros)
                user_id = maestros[lista_maestros.index(maestro_seleccionado)][0]
                user = clase_maestro.Maestro(user_id)
                horario_maestro()

        elif vista_seleccionada == "Tabla de Asistencias por Maestro":
            st.header("Tabla de Asistencias por Maestro")
            with sqlite3.connect("prueba4.db") as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT id_usuario, nombre, apellido_paterno, apellido_materno FROM Usuarios WHERE rol = 'maestro'")
                maestros = cursor.fetchall()

            lista_maestros = {f"{maestro[1]} {maestro[2]} {maestro[3]}": maestro[0] for maestro in maestros}

            if not lista_maestros:
                st.warning("No hay maestros disponibles.")
            else:
                maestro_seleccionado = st.selectbox("Seleccione el maestro:", list(lista_maestros.keys()))
                user_id = lista_maestros[maestro_seleccionado]
                user = clase_maestro.Maestro(user_id)
                if isinstance(user, clase_maestro.Maestro):
                    st.header("Asistencias del Mes")
                    asistencia_maestro()