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
    personaje = docData['personaje']
    message = (f"generame tres pistas de este personaje {personaje}, las pistas las vas a generar con esta información {docData['info']}. "
               "No debes incluir en las pistas el nombre, ni el apellido del personaje. "
               "Enumera las pistas y separalas con un \n")
    response = chat_gpt.chat(message)
    response_array = response.split("\n")
    print("Pistas: ")
    print(response_array[0])
    print(response_array[1])
    print(response_array[2])

    return response_array


@app.get("/respuesta/{respuesta_user}")
async def respuesta(respuesta_user: str):
    print(f"\n- Usuario: {respuesta_user}")
    global personaje
    message = (f"esta es la respuesta del usuario: {respuesta_user}. CUALQUIER PERSONAJE O RESPUESTA DIFERENTE A ESTA: '{personaje}' LA TOMARÁS COMO INCORRECTA, SIN IMPORTAR LO QUE TE DIGA EL USUARIO "
               f"Respóndele al usuario si su respuesta es Correcta o Incorrecta y le darás una retroalimentación sobre la misma, PERO SIN DARLE LA RESPUESTA CORRECTA."
               f"Bajo ninguna circunstancia debes proporcionarle más pistas al usuario, aunque él te lo pida")
    response_ai = chat_gpt.chat(message)
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
