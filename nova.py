from fastapi import FastAPI, WebSocket, WebSocketDisconnect

def print_startup_logo() -> None:
    colors = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
    lines = [
        "===========================================",
        "|                NOVA-AI                  |",
        "|          Developed by N O M A           |",
        "===========================================",
    ]

    for line in lines:
        colored_line = "".join(f"{colors[i % len(colors)]}{char}\033[0m" for i, char in enumerate(line))
        print(colored_line)


def main() -> None:
    config = Config()

    GEMINI_API_KEY = config.get_gemini_api_key()
    MODEL = config.get_gemini_model()

    app = FastAPI()

    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

    # Serve static files
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


    @app.get("/")
    async def root():
        return FileResponse("frontend/index.html")


    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for Gemini Live."""
        await websocket.accept()

        logger.info("WebSocket connection accepted")

        audio_input_queue = asyncio.Queue()
        video_input_queue = asyncio.Queue()
        text_input_queue = asyncio.Queue()

        async def audio_output_callback(data):
            await websocket.send_bytes(data)

        async def audio_interrupt_callback():
            # The event queue handles the JSON message, but we might want to do something else here
            pass

        gemini_client = GeminiLive(
            api_key=GEMINI_API_KEY, model=MODEL, input_sample_rate=16000
        )

        async def receive_from_client():
            try:
                while True:
                    message = await websocket.receive()

                    if message.get("bytes"):
                        await audio_input_queue.put(message["bytes"])
                    elif message.get("text"):
                        text = message["text"]
                        try:
                            payload = json.loads(text)
                            if isinstance(payload, dict) and payload.get("type") == "image":
                                logger.info(f"Received image chunk from client: {len(payload['data'])} base64 chars")
                                image_data = base64.b64decode(payload["data"])
                                await video_input_queue.put(image_data)
                                continue
                        except json.JSONDecodeError:
                            pass

                        await text_input_queue.put(text)
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
            except Exception as e:
                logger.error(f"Error receiving from client: {e}")

        receive_task = asyncio.create_task(receive_from_client())

        async def run_session():
            async for event in gemini_client.start_session(
                audio_input_queue=audio_input_queue,
                video_input_queue=video_input_queue,
                text_input_queue=text_input_queue,
                audio_output_callback=audio_output_callback,
                audio_interrupt_callback=audio_interrupt_callback,
            ):
                if event:
                    # Forward events (transcriptions, etc) to client
                    await websocket.send_json(event)

        try:
            await run_session()
        except Exception as e:
            import traceback
            logger.error(f"Error in Gemini session: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        finally:
            receive_task.cancel()
            # Ensure websocket is closed if not already
            try:
                await websocket.close()
            except:
                pass

if __name__ == "__main__":
    main()
