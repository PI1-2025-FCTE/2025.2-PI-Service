from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import trajetos
import os
import asyncio
import json
import aio_pika

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import engine
    import app.models as models
    consumer_task = asyncio.create_task(start_rabbitmq_consumer())
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="ESP32 Car Control API", version="1.0.0", lifespan=lifespan, docs_url="/docs")
app.include_router(trajetos.router)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }

async def ESPResponse(data: str):
    print(f" [db] Processando dados recebidos: {data}")
    try:
        payload = json.loads(data)

        novo_trajeto = models.Trajeto(
            latitude=payload.get("latitude"),
            longitude=payload.get("longitude")
        )

        async with async_sessionmaker() as session:
            async with session.begin():
                session.add(novo_trajeto)
            await session.commit()
        
        print(f" [db] Dados salvos com sucesso: {novo_trajeto.id}")

    except json.JSONDecodeError:
        print(f" [!] Erro: A mensagem recebida não é um JSON válido: {data}")
    except Exception as e:
        print(f" [!] Erro ao salvar no banco de dados: {e}")

async def start_rabbitmq_consumer():
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "password")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq") 
    
    connection_string = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"
    QUEUE_NAME = "esp32_data_queue"
    TOPIC_NAME = "esp32.data"

    print("Iniciando consumidor RabbitMQ...")

    while True: 
        try:
            connection = await aio_pika.connect_robust(connection_string)
            print("Conectado ao RabbitMQ!")

            async with connection:
                channel = await connection.channel()
                
                await channel.declare_exchange('amq.topic', type='topic', durable=True)
                
                queue = await channel.declare_queue(QUEUE_NAME, durable=True)
                
                await queue.bind(exchange='amq.topic', routing_key=TOPIC_NAME)
                
                print(f"[*] Consumidor pronto. Esperando por mensagens no tópico '{TOPIC_NAME}'...")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process(): 
                            data = message.body.decode()
                            print(f" [x] Recebido do RabbitMQ: '{data}'")
                            
                            await ESPResponse(data)

        except aio_pika.exceptions.AMQPConnectionError as e:
            print(f"Erro de conexão com RabbitMQ: {e}. Tentando novamente em 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Erro inesperado no consumidor RabbitMQ: {e}. Reiniciando...")
            await asyncio.sleep(5)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async for data in websocket.iter_text():
        await websocket.send_text(f"Message text was: {data}")
