from ChatGPT import ChatGPT

class Gaming:
    def __init__(self, chat_gpt: ChatGPT, personaje: str, info_personaje: str, instructions_game: str):
        self.chat_gpt = chat_gpt
        self.personaje = personaje
        self.info_personaje = info_personaje
        self.instructions_game = instructions_game
