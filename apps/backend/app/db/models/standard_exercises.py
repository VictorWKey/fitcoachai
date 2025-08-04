from sqlalchemy import Column, Integer, String, Enum
from db.base import Base
import enum
from sqlalchemy.orm import relationship

class MuscleGroupEnum(str, enum.Enum):
    pectoral = "pectoral"
    espalda = "espalda"
    biceps = "biceps"
    triceps = "triceps"
    abdomen = "abdomen"
    gluteo = "gluteo"
    cuadriceps = "cuadriceps"
    aductor = "aductor"
    isquiotibiales = "isquiotibiales"
    pantorrilla = "pantorrilla"
    trapecio = "trapecio"
    deltoides_posterior = "hombro_posterior"
    deltoides_medio = "hombro_lateral"
    deltoides_frontal = "hombro_frontal"
    antebrazo = "antebrazo"
    core = "core"
    oblicuos = "oblicuos"
    zona_lumbar = "zona_lumbar"
    cuello = "cuello"

class EquipmentEnum(str, enum.Enum):
    barra = "barra"
    mancuernas = "mancuernas"
    maquina = "maquina"
    poleas = "poleas"
    peso_corporal = "peso_corporal"
    discos = "discos"

class StandardExerciseType(str, enum.Enum):
    compuesto = "compuesto"
    aislado = "aislado"

class StandardExercise(Base):
    __tablename__ = "standard_exercise"
    __table_args__ = {'extend_existing': True}  # Add this line to handle multiple imports
    
    id = Column(Integer, primary_key=True)  # Removed index=True as primary keys are automatically indexed
    standard_name = Column(String(100), unique=True, nullable=False)
    main_muscle_group = Column(Enum(MuscleGroupEnum), nullable=False)
    equipment = Column(Enum(EquipmentEnum), nullable=False)
    type = Column(Enum(StandardExerciseType), nullable=False)
    
    programmed_exercises = relationship("ProgrammedExercise", back_populates="standard_exercise")
    exercise_logs = relationship("StrengthLog", back_populates="standard_exercise")