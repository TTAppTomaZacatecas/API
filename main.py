import random

import firebase_admin
from fastapi import FastAPI
from firebase_admin import credentials
from firebase_admin import firestore
from openai import OpenAI

from ChatGPT import ChatGPT
from payload.Gaming import Gaming

cred = credentials.Certificate("utils/keys/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
chat_gpt = ChatGPT()
client = OpenAI()
db = firestore.client()
collect = "hlhtz_db"

gaming_list = []


@app.get("/")
async def root():
    return "Hola mundo"


@app.get("/saludo/{message}")
async def say_hello(message: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "Tú te llamarás Pancho y hablarás como un guia de turista."},
            {"role": "user", "content": message}
        ]
    )
    return completion.choices[0].message.content


@app.get("/chat/{message}")
async def chat(message: str):
    message += "*"
    print("\n- Usuario: ", message)
    response = chat_gpt.chat(message)
    print("- Bot: ", response)
    return response


@app.get("/create-new-game-instance")
async def create_new_game_instance():
    global gaming_list
    chat_gpt = ChatGPT()
    personaje = ""
    info_personaje = ""
    instructions_game = ""
    new_instance = Gaming(chat_gpt, personaje, info_personaje, instructions_game)
    gaming_list.append(new_instance)
    index_of_new_instance = len(gaming_list) - 1
    return index_of_new_instance


@app.get("/clear-all-instances")
async def clear_all_instances():
    global gaming_list
    gaming_list.clear()


@app.get("/{index_instance}/get-pistas")
async def get_pistas(index_instance: int):
    doc_data = get_random_document(collect)
    global gaming_list
    if 0 > index_instance >= len(gaming_list):
        return "Index out of range"
    gaming_list[index_instance].personaje = doc_data['personaje']
    gaming_list[index_instance].info_personaje = doc_data['info']
    message = "Genera 3 pistas del personaje {personaje}, las pistas las vas a generar con esta información: {info}. Las pistas deben ser entendibles para un niño de entre 10 a 12 años de edad. NO DEBES INCLUIR en las pistas el nombre, ni el apellido del personaje. Enumera las pistas y separalas con un \n"
    data = "\n\n{personaje}=" + f"{gaming_list[index_instance].personaje}" + "\n" + "{info}=" + f"{gaming_list[index_instance].info_personaje}"
    prompt = message + data
    response = gaming_list[index_instance].chat_gpt.chat(prompt)
    response_array = response.split("\n")
    # Remove empty and blank items
    cleaned_list = [s for s in response_array if s and s.strip()]
    print(f"Pistas del jugador {index_instance}: ")
    print(cleaned_list[0])
    print(cleaned_list[1])
    print(cleaned_list[2])
    set_start_game_instructions(index_instance)
    gaming_list[index_instance].chat_gpt.chat(
        gaming_list[index_instance].instructions_game
    )
    return cleaned_list


@app.get("/{index_instance}/procesar-respuesta-usuario/{respuesta_user}")
async def procesar_respuesta_usuario(index_instance: int, respuesta_user: str):
    global gaming_list
    if 0 > index_instance >= len(gaming_list):
        return "Index out of range"
    print(f"\n- Usuario {index_instance}: {respuesta_user}")
    response_ai = gaming_list[index_instance].chat_gpt.chat(respuesta_user)
    print(f"> Bot {index_instance}: {response_ai}")
    return response_ai


@app.get("/{index_instance}/nuevo_juego")
async def nuevo_juego(index_instance: int, ):
    global gaming_list
    if 0 > index_instance >= len(gaming_list):
        return "Index out of range"
    gaming_list[index_instance].chat_gpt = ChatGPT()
    doc_data = get_random_document(collect)
    gaming_list[index_instance].personaje = doc_data['personaje']
    gaming_list[index_instance].info_personaje = doc_data['info']
    message = "Genera 3 pistas del personaje {personaje}, las pistas las vas a generar con esta información: {info}. Las pistas deben ser entendibles para un niño de entre 10 a 12 años de edad. NO DEBES INCLUIR en las pistas el nombre, ni el apellido del personaje. Enumera las pistas y separalas con un \n"
    data = "\n\n{personaje}=" + f"{gaming_list[index_instance].personaje}" + "\n" + "{info}=" + f"{gaming_list[index_instance].info_personaje}"
    prompt = message + data
    response = gaming_list[index_instance].chat_gpt.chat(prompt)
    response_array = response.split("\n")
    # Remove empty and blank items
    cleaned_list = [s for s in response_array if s and s.strip()]
    print(f"\n\nJuguemos otra vez jugador {index_instance}!")
    print("Pistas: ")
    print(cleaned_list[0])
    print(cleaned_list[1])
    print(cleaned_list[2])
    set_start_game_instructions(index_instance)
    gaming_list[index_instance].chat_gpt.chat(
        gaming_list[index_instance].instructions_game
    )
    return cleaned_list


@app.get("/specific/{collection}/{document}")
async def say_hello(collection: str, document: str):
    return get_document(collection, document)


@app.get("/size/{collection}")
async def get_size(collection: str):
    return size_collection(collection)


@app.get("/random/{collection}")
async def get_random(collection: str):
    return get_random_between_collection(collection)


@app.get("/random_document/{collection}")
async def get_random_doc(collection: str):
    return get_random_document(collection)


def set_start_game_instructions(index_instance: int):
    global gaming_list
    gaming_list[index_instance].instructions_game = (
        "Parámetros del juego:"
        f"Nombre del personaje: {gaming_list[index_instance].personaje}"
        f"Información del personaje: {gaming_list[index_instance].info_personaje}"
        "Ejemplo de cómo funcionarría el juego:"
        "Información del personaje:"
        "Este personaje es un detective muy famoso, conocido por su aguda observación y habilidades deductivas. Vive en Londres y tiene un amigo llamado Watson."
        "Respuesta del usuario:"
        "'¿Es un detective de Londres?'"
        "IA:"
        "¡Sí! Estás en el camino correcto. La probabilidad de acierto es del 40%. ¿Tienes más pistas o te atreves a dar una respuesta más específica?"
        "Respuesta del usuario:"
        "'¿Es Sherlock Holmes?'"
        "IA:"
        "¡Correcto! Has adivinado el personaje. La probabilidad de acierto es del 100%."
        "Instrucciones para la IA:"
        "Probabilidad de acierto: Si el usuario da una respuesta general o relacionada con la información, la IA debe responder con una probabilidad de acierto que aumente progresivamente (ejemplo: 40%, 60%, 80%)."
        "Cuando el usuario menciona el nombre del personaje correctamente, la IA debe responder con un 100% y considerar la respuesta como correcta."
        "Si el usuario responde incorrectamente, la IA debe guiarlo con más pistas sin revelar directamente el nombre del personaje hasta que el usuario lo adivine correctamente."
        "Criterios para determinar la probabilidad de acierto:"
        "0%: Respuesta completamente irrelevante."
        "40% - 60%: Respuesta general o indirecta, pero vinculada a la información proporcionada."
        "80%: Respuesta muy cercana o precisa, pero no el nombre del personaje."
        "100%: Respuesta correcta con el nombre exacto del personaje."
        "\n"
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
        "Nunca le proporciones el nombre del personaje, su pseudónimo, su apellido, o la forma como lo llamaban, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
    )


def get_all_docs(collectionName):
    docs = (
        db.collection(collectionName)
        .stream()
    )
    documents_list = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        doc_data['docData'] = doc._data
        documents_list.append(doc_data)
    for doc_data in documents_list:
        print(f"Document ID: {doc_data['id']}")
        print(f"Document Data: {doc_data['docData']}")
        print()
    return documents_list


def get_document(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    print(doc_ref)
    doc = doc_ref.get()
    print(doc)
    if doc.exists:
        return doc.to_dict()
    else:
        print(f"Document '{document_id}' not found in collection '{collection_name}'")
        return None


def size_collection(collection_name):
    collection_ref = db.collection(collection_name)
    # Get the query snapshot
    query_snapshot = collection_ref.get()
    # Get the total count from the snapshot
    total_count = len(query_snapshot)  # Use len() for collection size
    return total_count


def get_random_between_collection(collection_name):
    # Get a random number between the first element of the array and the array size
    random_num = (random.randint(1, size_collection(collection_name))) - 1
    return random_num


def get_random_document(collection_name):
    # Step 1: Get a list of all document IDs in the collection
    collection = db.collection(collection_name)
    document_ids = [doc.id for doc in collection.stream()]
    # Step 2: Get a random index from the list
    random_index = random.randint(0, len(document_ids) - 1)
    # Step 3: Use the random index to get the corresponding document
    random_document_ref = collection.document(document_ids[random_index])
    doc_data = random_document_ref.get().to_dict()
    return doc_data
