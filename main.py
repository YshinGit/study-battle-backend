from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from generator import generar_preguntas

app = FastAPI(title="Study Battle Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://study-battle-frontend-alpha.vercel.app",  # 👈 tu URL de Vercel
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    text: str
    max_questions: int = 8

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        preguntas = generar_preguntas(req.text, req.max_questions)
        return {"questions": preguntas}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))