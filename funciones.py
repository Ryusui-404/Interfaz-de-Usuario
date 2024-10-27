import sqlite3,clase_alumno,clase_maestro,clase_admin

def login(user,password) -> int:
    '''
    0. error
    1. admin
    2. maestro
    3. alumno
    '''
    conexion = sqlite3.connect("prueba4.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE no_cuenta = ? AND contraseña = ?", (user, password))
    
    user = cursor.fetchone()

    if not user:
        return 0
    else:
        
        
        match user[-1]:
            case 'admin':
                usuario = clase_admin()
                code = 1
            case 'maestro':
                usuario = clase_maestro()    
                code = 2            
            case 'alumno' : 
                usuario = clase_alumno()
                code = 3
            
        usuario.nombre = user[1]
        usuario.apellidop = user[2]
        usuario.apellidom = user[3]
        usuario.id = user[0]
        if usuario.__class__.__name__ == 'Maestro' or usuario.__class__.__name__ == 'Alumno':
            usuario.horario = usuario.generar_horario()
            
        
    conexion.commit()
    conexion.close()
        
    return (code,usuario)