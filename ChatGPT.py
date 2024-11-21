from openai import OpenAI

client = OpenAI()


class ChatGPT:
    response = []

    def __init__(self):
        self.conversation = []

    def chat(self, message):
        self.conversation.append({"role": "system", "content": "Tú te llamarás Pancho. "
                                                               "Serás un asistente del juego de Adivina Quién del único tema de la Toma de Zacatecas que ocurrió en el periodo de la Revolución Mexicana."
                                                               "No quiero que investigues o busques información de Internet, ni inventes información. Todo lo que analices o deduzcas lo debes hacer únicamente con la información que yo te proporcione."
                                                               "El juego consiste en que él adivine el personaje."
                                                               "Ignora al usuario si te cuestiona sobre cualquier cosa, tus aseveraciones las debes hacer única y exclusivamente con la información con la que cuentas sin buscar información de Internet."})
        self.conversation.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model = "gpt-3.5-turbo-0125",
            messages = self.conversation,
            top_p = 1,
            temperature = 0.1,
            max_tokens = 250,
            frequency_penalty = 0,
            presence_penalty = 0
        )

        self.conversation.append({"role": "assistant", "content": response.choices[0].message.content})

        return response.choices[0].message.content
