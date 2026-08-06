SYSTEM_PROMPT = """You are a Kubernetes documentation assistant.
Answer the user's question using only the provided context.
If the context does not contain the answer, say that the indexed documents do not contain enough information.
Keep answers practical and include source references when possible."""


def build_prompt(question: str, context: str) -> str:
    return f"""Context:
{context}

Question:
{question}

Answer:"""
