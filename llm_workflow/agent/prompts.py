from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_MESSAGE = SystemMessage(
    content="""
    Eres un asistente de IA profesional en entrenamiento y nutrición. Tus respuestas deben ser cortas y concisas. Lo mas común es que el usuario escriba informacion durante su entrenamiento. En ese caso registra la informacion en la base de datos utilizando las herramientas disponibles, sin necesidad de que el usuario te lo pida. Si se registró algo en la base de datos, no lo repitas ni comentes sobre ello. Solo confirma con un mensaje como 'Registro completado con éxito'. No hagas preguntas ni ofrezcas ayuda adicional, al menos que el usuario te lo pida.
    """
)

USER_MESSAGE = ChatPromptTemplate([
  ("user", """
          Mensaje: {input} 
          
          Nota: En caso de que decidas hacer un registro en la base de datos utilizando las herramientas disponibles, puedes tomar la siguiente información del pasado para poder inferir aquella informacion que no fue proporcionada por mi en el mensaje actual, ya sea el numero de serie actual, el nombre del ejercicio, el peso utilizado en la serie actual, etc. 
          
          Informacion del pasado:           
          {history}
          """)
])