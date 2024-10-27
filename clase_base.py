class Base:
    def __init__(self) -> None:
        self.nombre = None
        self.apellidop = None
        self.apellidom = None
        self.id = None
        self. horario = None
    def generar_horario():
        pass
    def generar_horario_dia(dia:int,mes:int,año:int ) -> list | bool: #Si no es un dia hábil regresa False
        pass
    def estadisticas(tipo,periodo,arg) -> list: #arg viene definido segun la clase, no tocar
        '''
        |D1     |D2     |D3     |
        |True   |False  |True   |
        
        
        '''
        pass
    def modificar_asistencia(id_clase:int, dia:int, mes: int, año:int) -> bool : #regresa True o False si se puede modificar
        pass