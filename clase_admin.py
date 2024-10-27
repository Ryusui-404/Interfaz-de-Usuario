import clase_base

class Admin(clase_base.Base):
    def __init__(self) -> None:
        self.lista_alumnos = None
        self.lista_maestros = None
        self.lista_materias = None
        self.lista_carreras = None        