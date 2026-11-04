import random
import re
import spacy

nlp = spacy.load("es_core_news_sm")

PATRONES_HECHO = [
    r"\bes\b", r"\bson\b", r"\bfue\b", r"\bfueron\b",
    r"\bse define como\b", r"\bconsiste en\b", r"\bsignifica\b",
    r"\bse caracteriza por\b", r"\btiene\b", r"\bpertenece a\b",
]

def _limpiar(oracion: str) -> str:
    return re.sub(r"\s+", " ", oracion).strip()

def _oraciones_candidatas(texto: str):
    doc = nlp(texto)
    candidatas = []
    for sent in doc.sents:
        s = _limpiar(sent.text)
        if 8 <= len(s.split()) <= 30 and any(re.search(p, s, re.I) for p in PATRONES_HECHO):
            candidatas.append(s)
    return candidatas

def _extraer_entidades(oracion: str):
    doc = nlp(oracion)
    return [ent.text for ent in doc.ents]

def _generar_distractores(correcta: str, pool: list[str], n: int = 2):
    opciones = [x for x in pool if x.lower() != correcta.lower()]
    random.shuffle(opciones)
    return opciones[:n]

def generar_preguntas(texto: str, max_preguntas: int = 8):
    oraciones = _oraciones_candidatas(texto)
    if len(oraciones) < 3:
        raise ValueError("El texto es muy corto o no tiene suficientes hechos. Pega un texto más largo.")

    random.shuffle(oraciones)
    oraciones = oraciones[:max_preguntas]

    todas_entidades = []
    for o in oraciones:
        todas_entidades.extend(_extraer_entidades(o))

    preguntas = []
    for oracion in oraciones:
        entidades = _extraer_entidades(oracion)
        if not entidades:
            continue

        objetivo = random.choice(entidades)
        enunciado = oracion.replace(objetivo, "_____", 1)
        if "_____" not in enunciado:
            continue

        distractores = _generar_distractores(objetivo, todas_entidades, n=2)
        if len(distractores) < 2:
            continue

        opciones = [objetivo] + distractores
        random.shuffle(opciones)
        correct_idx = opciones.index(objetivo)

        preguntas.append({
            "text": enunciado,
            "options": opciones,
            "correct_idx": correct_idx,
            "justification": oracion,
        })

    if len(preguntas) < 3:
        raise ValueError("No se pudieron generar suficientes preguntas. Pega un texto con más hechos/entidades.")

    return preguntas