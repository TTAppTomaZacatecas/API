from click import prompt
from fastapi import FastAPI
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random

from ChatGPT import ChatGPT

cred = credentials.Certificate("utils/keys/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
chat_gpt = ChatGPT()
client = OpenAI()
db = firestore.client()
collect = "hlhtz_db"

personaje = ""
info_personaje = ""


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
    print("- Bot: ",response)
    return response


@app.get("/pistas")
async def pistas():
    docData = get_random_document(collect)
    global personaje
    global info_personaje
    personaje = docData['personaje']
    info_personaje = docData['info']
    message = "Genera 3 pistas del personaje {personaje}, las pistas las vas a generar con esta información: {info}. NO DEBES INCLUIR en las pistas el nombre, ni el apellido del personaje. Enumera las pistas y separalas con un \n"
    data = "\n\n{personaje}=" + f"{personaje}" + "\n" + "{info}=" + f"{info_personaje}"
    prompt = message + data
    response = chat_gpt.chat(prompt)
    response_array = response.split("\n")
    print("Pistas: ")
    print(response_array[0])
    print(response_array[1])
    print(response_array[2])
    prompt_juego = (
        "Parámetros del juego:"
        f"Nombre del personaje: {personaje}"
        f"Información del personaje: {info_personaje}"
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
        "Nunca le proporciones el nombre del personaje, bajo ninguna circunstania. A menos que explícitamente te diga que se rinde."
    )
    chat_gpt.chat(prompt_juego)
    return response_array


@app.get("/respuesta/{respuesta_user}")
async def respuesta(respuesta_user: str):
    print(f"\n- Usuario: {respuesta_user}")
    response_ai = chat_gpt.chat(respuesta_user)
    print(f"> Bot: {response_ai}")
    return response_ai


@app.get("/nuevo_juego")
async def nuevo_juego():
    chat_gpt = ChatGPT()
    docData = get_random_document(collect)
    global personaje
    personaje = docData['personaje']
    message = (
        f"Generame tres pistas de este personaje {docData['personaje']}, las pistas las vas a generar con esta información {docData['info']}. "
        f"No debes incluir en las pistas el nombre, ni el apellido del personaje. "
        f"Enumera las pistas y separalas con un \\n")
    response = chat_gpt.chat(message)
    response_array = response.split("\n")
    print("\n\nJuguemos otra vez!")
    print("Pistas: ")
    print(response_array[0])
    print(response_array[1])
    print(response_array[2])

    return response_array


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
    docData = random_document_ref.get().to_dict()
    return docData
