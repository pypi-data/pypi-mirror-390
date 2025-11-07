import os
import json
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List
import numpy as np

class EmpoorioEmbedder:
    def __init__(self, model_path: str = "models/foundation/empoorio_lm"):
        # Load tokenizer and model from specified path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path)
        self.model.eval()

    def embed_text(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Compute embeddings for a list of texts, optionally normalizing them."""
        try:
            with torch.no_grad():
                # Tokenize input texts and compute embeddings using the model
                inputs = self.tokenizer(
                    texts,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                )
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state[:, 0, :].numpy()

                if normalize:
                    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                    embeddings = embeddings / norms

                return embeddings
        except Exception as e:
            print(f"[ERROR] Failed to compute embeddings: {e}")
            return np.zeros((len(texts), self.model.config.hidden_size))

    def save_embeddings(self, texts: List[str], output_path: str):
        """Save embeddings of given texts to a .npy file."""
        embeddings = self.embed_text(texts)
        np.save(output_path, embeddings)
        print(f"[INFO] Saved embeddings to {output_path}")

    def save_embeddings_with_metadata(self, texts: List[str], output_path: str, metadata_path: str):
        """Save embeddings and associated metadata to specified files."""
        embeddings = self.embed_text(texts)
        np.save(output_path, embeddings)
        
        metadata = {
            "vector_format": "numpy",
            "dimension": embeddings.shape[1],
            "count": len(texts),
            "schema": "models/foundation/embedding_generator/vector_schema.json",
            "source": "EmpoorioEmbedder",
            "normalized": True,
            "model_path": self.model.name_or_path
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        print(f"[INFO] Saved embeddings to {output_path}")
        print(f"[INFO] Saved metadata to {metadata_path}")

    def load_embeddings(self, path: str) -> np.ndarray:
        """Load embeddings from a .npy file."""
        print(f"[INFO] Loaded embeddings from {path}")
        return np.load(path)

if __name__ == "__main__":
    embedder = EmpoorioEmbedder()
    sample_texts = [
        "EmpoorioChain is a modular blockchain infrastructure.",
        "DracmaS is the native token used across the Empoorio ecosystem."
    ]
    output_embeddings_path = "models/foundation/embedding_generator/sample_embeddings.npy"
    output_metadata_path = "models/foundation/embedding_generator/sample_metadata.json"

    embedder.save_embeddings_with_metadata(sample_texts, output_embeddings_path, output_metadata_path)
    print(f"Embeddings saved to {output_embeddings_path}")
    print(f"Metadata saved to {output_metadata_path}")