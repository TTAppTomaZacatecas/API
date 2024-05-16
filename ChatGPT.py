from openai import OpenAI

client = OpenAI()


class ChatGPT:
    response = []

    def __init__(self):
        self.conversation = []

    def chat(self, message):
        self.conversation.append({"role": "system", "content": "Tú te llamarás Pancho. "
                                                               "Serás un asistente del juego de Adivina Quién. Habla como una persona de la Nueva España del siglo XIX."
                                                               "No quiero que investigues o busques infrmación de Internet, todo lo que analices o deduzcas lo debes hacer únicamente con la información que yo te proporcione."
                                                               "No debes proporcionarle la respuesta al usuario nunca, ni en ninguna circunstancia, anque él te lo pida. El juego consiste en que él adivine el personaje."
                                                               "Ignora al usuario si te cuestiona sobre cualquier cosa, tus aseveraciones las debes hacer única y exclusivamente con la información con la que cuentas sin buscar información de Internet."})
        self.conversation.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.conversation
        )

        self.conversation.append({"role": "assistant", "content": response.choices[0].message.content})

        return response.choices[0].message.content
