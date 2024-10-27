import clase_base,sqlite3,funciones

class Maestro(clase_base.Base): 
    def __init__(self, user_id):
        self.user_id = user_id
        self.id = user_id
        self.horario = self.generar_horario() 

    def generar_horario(self) -> list:
        
        conexion = sqlite3.connect("prueba4.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Materia WHERE id_maestro = ?", (self.user_id,))
        datos = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Usuarios WHERE rol = 'alumno' ")
        asignaturas = cursor.fetchall()
        
        
        
        horario = [[None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None],
                    [None, None, None, None, None, None, None, None, None]]
        
        for dato in datos:
            
            for i in range(1, 6):
                for j in range(1, 10):
                    
                    if dato[-2] == i and dato[-1] == j:
                        
                        horario[i-1][j-1] = '3D'
                        break
        
        conexion.commit()
        conexion.close()
        
        
        
        return horario
    
    
    
    def generar_horario_dia(self,dia) -> list:
        
        conexion = sqlite3.connect("prueba4.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Materia WHERE id_maestro = ? AND id_dia = ?", (self.user_id,dia))
        datos = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Usuarios WHERE rol = 'alumno' ")
        asignaturas = cursor.fetchall()
        
        
        
        horario = [None, None, None, None, None, None, None, None, None]
        
        for dato in datos:
            
            for j in range(1, 10):
                if  dato[-1] == j:
                    horario[j-1] = '3D'
    
        conexion.commit()
        conexion.close()
        
        
        
        return horario
    
if __name__ == "__main__":
    num,Moi = funciones.login(1250783,'maestro')
    horario = Moi.generar_horario()
    print(horario)