import math, sqlite3, json, os
from foundry_local_sdk import Configuration, FoundryLocalManager

# --- Ayarlar ---
CHAT_MODEL_NAME = "phi-3.5-mini"
EMBEDDING_MODEL_NAME = "qwen3-embedding-0.6b"


# Knowledge base — each string represents a document
# documents = [
#     "Foundry Local runs AI models directly on your device without cloud connectivity.",
#     "The Foundry Local SDK supports Python, C#, JavaScript, and Rust.",
#     "Embedding models convert text into numerical vectors for similarity search.",
#     "Foundry Local uses ONNX Runtime for efficient model inference on CPUs and GPUs.",
#     "The model catalog provides pre-optimized models that you can download and run locally.",
#     "Retrieval-augmented generation grounds model responses in your own data.",
#     "Vector similarity search finds documents that are semantically close to a query.",
#     "Chat completions generate natural language responses from a prompt and context.",
# ]



def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0



def find_relevant(query_embedding, doc_embeddings, top_k=2):
    """Return the indices and scores of the top-k most similar documents."""
    scores = []
    for i, doc_emb in enumerate(doc_embeddings):
        score = cosine_similarity(query_embedding, doc_emb)
        scores.append((i, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def embed_in_batches(embedding_client, texts, batch_size=10):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = embedding_client.generate_embeddings(batch)
        all_embeddings.extend(item.embedding for item in response.data)
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)}")
    return all_embeddings


def load_and_chunk_documents(folder="docs"):
    chunks = []
    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            path = os.path.join(folder, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            chunks.extend(paragraphs)
    return chunks


def main():
    print("Starting Foundry Client...")

    # Initialize the SDK
    config = Configuration(app_name="foundry_local_rag") 
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    conn = sqlite3.connect("knowledge_base.db")
    conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    embedding TEXT
                )
            """)

    print("Registering execution providers...")
    manager.download_and_register_eps(progress_callback=lambda name, pct: print(f"\r  {name}: {pct:.1f}%", end="", flush=True))
    print()

    # Load the embedding model
    print(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
    embedding_model = manager.catalog.get_model(EMBEDDING_MODEL_NAME)
    if not getattr(embedding_model, "is_cached", False):
        embedding_model.download(lambda pct: print(f"\r  {pct:.1f}%", end="", flush=True))
        print()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    documents = load_and_chunk_documents("docs")
    print(f"Loaded {len(documents)} chunks from docs/ folder.")

    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]

    if count == len(documents) and count > 0:
        print("Using cached embeddings from SQLite.")
        rows = conn.execute("SELECT content, embedding FROM documents").fetchall()
        documents = [row[0] for row in rows]
        doc_embeddings = [json.loads(row[1]) for row in rows]

    else:
        print("Cache miss or empty — generating embeddings.")
        doc_embeddings = embed_in_batches(embedding_client, documents, batch_size=10)

        conn.execute("DELETE FROM documents")
        for content, embedding in zip(documents, doc_embeddings):
            conn.execute(
                "INSERT INTO documents (content, embedding) VALUES (?, ?)",
                (content, json.dumps(embedding))
            )
        conn.commit()

    print(f"Indexed {len(doc_embeddings)} documents.")

    # Embed all documents in a single batch call
    # response = embedding_client.generate_embeddings(documents)
    # print(f"Indexed {len(doc_embeddings)} documents.")

    # conn.execute("DELETE FROM documents")

    # for content, embedding in zip(documents, doc_embeddings):
    #     conn.execute(
    #         "INSERT INTO documents (content, embedding) VALUES (?, ?)",
    #         (content, json.dumps(embedding))
    # )
    # conn.commit()

    # To see if the documents are deleted and inserted correctly
    # count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    # print(f"Tabloda {count} satır var.")

    # Load the chat model
    print(f"Loading chat model '{CHAT_MODEL_NAME}'...")
    chat_model = manager.catalog.get_model(CHAT_MODEL_NAME)
    if not getattr(chat_model, "is_cached", False):
        chat_model.download(lambda pct: print(f"\r  {pct:.1f}%", end="", flush=True))
        print()
    chat_model.load()
    chat_client = chat_model.get_chat_client()

    print("\nModels loaded. Ready for questions.")
    print('Type "quit" to exit.\n')

    # Interactive query loop (retrieve -> augment -> generate)
    try:
        while True:
            query = input("Question: ").strip()
            if not query or query.lower() == "quit":
                break

            # Embed the query
            query_embedding = embedding_client.generate_embedding(query).data[0].embedding

            # Retrieve the most relevant documents
            results = find_relevant(query_embedding, doc_embeddings, top_k=2)
            context = "\n".join(f"- {documents[i]}" for i, _ in results)

            # Build the prompt with retrieved context
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Answer the user's question using only the provided context. "
                        "Respond in 1-2 sentences, directly and factually. "
                        "Do NOT say things like 'refer to the knowledge base', 'I can provide more details if needed', "
                        "or offer to elaborate further — just give the answer and stop. "
                        "If the context doesn't contain enough information, say so in one sentence.\n\n"
                        f"Context:\n{context}"
                    ),
                },
                {"role": "user", "content": query},
            ]

            # Stream the response
            response = chat_client.complete_chat(messages)
            print("Answer:", response.choices[0].message.content, "\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")

    finally:
        # Clean up
        embedding_model.unload()
        chat_model.unload()
        print("Models unloaded. Done!")


if __name__ == "__main__":
    main()