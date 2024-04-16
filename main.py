from fastapi import FastAPI
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random

cred = credentials.Certificate("utils/keys/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
client = OpenAI()
db = firestore.client()

personaje = ""


@app.get("/")
async def root():
    return "Hola mundo"


@app.get("/saludo/{mensaje}")
async def say_hello(mensaje: str):
    return f"Tu mensaje: {mensaje}"


@app.get("/chat/{message}")
async def chat(message: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "Tú te llamarás Pancho y hablarás como un guia de turista."},
            {"role": "user", "content": message}
        ]
    )
    return completion.choices[0].message.content


@app.get("/specificdb/{collection}/{document}")
async def say_hello(collection: str, document: str):
    return get_document(collection, document)


@app.get("/size/{collection}")
async def get_size(collection: str):
    return size_collection(collection)


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
