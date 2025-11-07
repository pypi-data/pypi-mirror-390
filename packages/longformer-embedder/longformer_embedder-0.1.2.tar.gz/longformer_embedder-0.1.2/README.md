# Longformer Embedder

A lightweight wrapper around Hugging Face Longformer to easily generate mean-pooled embeddings.

## Installation

```bash
pip install longformer-embedder
```

## Usage

```python
from longformer_embedder import LongformerEmbedder

embedder = LongformerEmbedder(model_name="allenai/longformer-base-4096")
vec = embedder.get_embedding("This is a test sentence.")
print(vec.shape)  # (768,)
```

### Batch Mode

```python
texts = ["Text one", "Text two", "Text three"]
embeddings = embedder.generate_embeddings(texts)
print(embeddings.shape)  # (3, 768)
```

## Notes
- Model weights are downloaded from Hugging Face automatically.
- Ensure `torch` is installed and compatible with your device (CPU/GPU).
- For GPU acceleration, install CUDA-enabled PyTorch.

## License
MIT License
