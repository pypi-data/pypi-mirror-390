import numpy as np
import torch
from transformers import LongformerTokenizer, LongformerModel
from tqdm import tqdm


class LongformerEmbedder:
    """
    A wrapper class for the Longformer model to easily generate text embeddings.
    """

    def __init__(self, model_name="allenai/longformer-base-4096", device=None):
        """
        Initializes and loads the tokenizer and model.

        Args:
            model_name (str): Hugging Face model name.
            device (str): 'cuda', 'cpu', or None (auto-detect).
        """
        print(f"Loading model: {model_name}...")
        self.tokenizer = LongformerTokenizer.from_pretrained(model_name)
        self.model = LongformerModel.from_pretrained(model_name)
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model.to(self.device)
        self.model.eval()
        print(f"Model loaded successfully on device: {self.device}")

    def get_embedding(self, text):
        """
        Generates a single 768-dimension embedding for a given text string.

        Args:
            text (str): The input text.

        Returns:
            np.ndarray: A 1D numpy array of shape (768,).
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding="longest",
            max_length=4096,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

    def generate_embeddings(self, text_list, show_progress=True):
        """
        Generates embeddings for a list of text strings.

        Args:
            text_list (list[str]): A list of text strings.
            show_progress (bool): Whether to display a tqdm progress bar.

        Returns:
            np.ndarray: A 2D numpy array of shape (n_texts, 768).
        """
        iterator = tqdm(text_list, desc="Generating Embeddings") if show_progress else text_list
        embeddings = [self._get_embedding_no_grad(t) for t in iterator]
        return np.array(embeddings)

    @torch.no_grad()
    def _get_embedding_no_grad(self, text):
        """Internal helper ensuring no_grad is active."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding="longest",
            max_length=4096,
        ).to(self.device)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()