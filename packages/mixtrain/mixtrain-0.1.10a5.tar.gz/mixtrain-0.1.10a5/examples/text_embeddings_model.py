#!/usr/bin/env python3
"""
Example text embeddings model using MixModel with external dependencies.

This example demonstrates:
- Using external libraries (transformers, torch) in a MixModel
- Loading pre-trained models
- Handling model initialization and caching
- Working with numpy/tensor outputs
- Batch processing optimization

The model generates text embeddings using a pre-trained sentence transformer,
which can be used for semantic search, clustering, and similarity tasks.
"""

from mixtrain import MixModel, mixparam


class TextEmbeddingsModel(MixModel):
    """
    Generate text embeddings using a pre-trained transformer model.

    This model loads a sentence-transformer model and generates dense
    vector embeddings for input text, useful for semantic search and
    similarity tasks.

    Requirements:
        - sentence-transformers
        - torch (or tensorflow)
        - numpy
    """

    model_name: str = mixparam(
        default="all-MiniLM-L6-v2",
        description="HuggingFace model name for embeddings (e.g., 'all-MiniLM-L6-v2', 'all-mpnet-base-v2')"
    )

    normalize: bool = mixparam(
        default=True,
        description="Whether to normalize embeddings to unit length"
    )

    return_numpy: bool = mixparam(
        default=True,
        description="Return embeddings as numpy arrays instead of lists"
    )

    max_length: int = mixparam(
        default=512,
        description="Maximum sequence length for input text"
    )

    def __init__(self, **kwargs):
        """
        Initialize the embeddings model.

        Args:
            **kwargs: Configuration parameters (model_name, normalize, etc.)
        """
        super().__init__(**kwargs)

        # Import dependencies (they should be installed in the environment)
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
        except ImportError as e:
            raise ImportError(
                "This model requires sentence-transformers and numpy. "
                "Install with: pip install sentence-transformers numpy"
            ) from e

        # Store numpy reference
        self.np = np

        # Load the model (this will cache it for subsequent runs)
        model_name = self.config.get('model_name', 'all-MiniLM-L6-v2')
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")

    def run(self, inputs=None):
        """
        Generate embeddings for a single text input.

        Args:
            inputs: Dictionary with 'text' key
                   Example: {"text": "This is a sentence to embed."}

        Returns:
            Dictionary with:
            {
                "embedding": [0.1, 0.2, ...],  # Vector of floats
                "dimension": 384,
                "text": "original text",
                "model": "all-MiniLM-L6-v2"
            }
        """
        if not inputs or 'text' not in inputs:
            raise ValueError("Input must contain 'text' key")

        text = inputs['text']

        # Generate embedding
        normalize = self.config.get('normalize', True)
        embedding = self.model.encode(
            text,
            normalize_embeddings=normalize,
            show_progress_bar=False
        )

        # Convert to appropriate format
        if self.config.get('return_numpy', True):
            # Keep as numpy array
            embedding_output = embedding.tolist()
        else:
            embedding_output = embedding.tolist()

        return {
            "embedding": embedding_output,
            "dimension": len(embedding_output),
            "text": text,
            "model": self.config.get('model_name', 'all-MiniLM-L6-v2')
        }

    def run_batch(self, batch):
        """
        Generate embeddings for a batch of texts (optimized).

        Args:
            batch: List of dictionaries with 'text' keys
                  Example: [{"text": "First text"}, {"text": "Second text"}]

        Returns:
            List of embedding results
        """
        if not batch:
            return []

        # Extract texts from batch
        texts = [item['text'] for item in batch]

        # Generate embeddings in batch (much faster than individual calls)
        normalize = self.config.get('normalize', True)
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=False,
            batch_size=len(texts)
        )

        # Format results
        results = []
        for text, embedding in zip(texts, embeddings):
            if self.config.get('return_numpy', True):
                embedding_output = embedding.tolist()
            else:
                embedding_output = embedding.tolist()

            results.append({
                "embedding": embedding_output,
                "dimension": len(embedding_output),
                "text": text,
                "model": self.config.get('model_name', 'all-MiniLM-L6-v2')
            })

        return results


class SemanticSearchModel(MixModel):
    """
    Semantic search model that finds similar texts using embeddings.

    This example shows how to build a more complex model that maintains
    state (a corpus of documents) and performs semantic search.
    """

    model_name: str = mixparam(
        default="all-MiniLM-L6-v2",
        description="HuggingFace model for embeddings"
    )

    top_k: int = mixparam(
        default=5,
        description="Number of top results to return"
    )

    def __init__(self, corpus=None, **kwargs):
        """
        Initialize semantic search model with a corpus.

        Args:
            corpus: List of documents to search (optional, can be added later)
            **kwargs: Configuration parameters
        """
        super().__init__(**kwargs)

        try:
            from sentence_transformers import SentenceTransformer, util
            import numpy as np
        except ImportError as e:
            raise ImportError(
                "This model requires sentence-transformers and numpy."
            ) from e

        self.util = util
        self.np = np

        # Load model
        model_name = self.config.get('model_name', 'all-MiniLM-L6-v2')
        self.model = SentenceTransformer(model_name)

        # Initialize corpus
        self.corpus = corpus or []
        self.corpus_embeddings = None
        if self.corpus:
            self._encode_corpus()

    def _encode_corpus(self):
        """Encode the corpus documents into embeddings."""
        if not self.corpus:
            return

        print(f"Encoding corpus of {len(self.corpus)} documents...")
        self.corpus_embeddings = self.model.encode(
            self.corpus,
            convert_to_tensor=True,
            show_progress_bar=False
        )
        print("Corpus encoded successfully.")

    def add_documents(self, documents):
        """Add documents to the corpus."""
        self.corpus.extend(documents)
        self._encode_corpus()

    def run(self, inputs=None):
        """
        Perform semantic search on the corpus.

        Args:
            inputs: Dictionary with 'query' key
                   Example: {"query": "machine learning algorithms"}

        Returns:
            Dictionary with top matching documents:
            {
                "query": "machine learning algorithms",
                "results": [
                    {"text": "...", "score": 0.85, "rank": 1},
                    ...
                ]
            }
        """
        if not inputs or 'query' not in inputs:
            raise ValueError("Input must contain 'query' key")

        if not self.corpus:
            raise ValueError("No documents in corpus. Add documents first.")

        query = inputs['query']
        top_k = self.config.get('top_k', 5)

        # Encode query
        query_embedding = self.model.encode(
            query,
            convert_to_tensor=True,
            show_progress_bar=False
        )

        # Compute similarity scores
        scores = self.util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)[0]
        scores = scores.cpu().numpy()

        # Get top-k results
        top_indices = self.np.argsort(scores)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            results.append({
                "text": self.corpus[idx],
                "score": float(scores[idx]),
                "rank": rank
            })

        return {
            "query": query,
            "results": results,
            "total_corpus_size": len(self.corpus)
        }

    def run_batch(self, batch):
        """Search multiple queries."""
        return [self.run(item) for item in batch]


def example_embeddings():
    """Example usage of TextEmbeddingsModel."""
    print("=== Text Embeddings Model Example ===\n")

    # Initialize model
    print("Initializing embeddings model...")
    model = TextEmbeddingsModel(
        model_name="all-MiniLM-L6-v2",
        normalize=True
    )

    # Single inference
    print("\nExample 1: Single Embedding")
    print("-" * 50)
    result = model.run({"text": "Machine learning is fascinating"})
    print(f"Text: {result['text']}")
    print(f"Embedding dimension: {result['dimension']}")
    print(f"Embedding (first 5 values): {result['embedding'][:5]}")
    print()

    # Batch inference
    print("Example 2: Batch Embeddings")
    print("-" * 50)
    batch = [
        {"text": "Deep learning with neural networks"},
        {"text": "Natural language processing"},
        {"text": "Computer vision applications"}
    ]
    results = model.run_batch(batch)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text'][:40]}...")
        print(f"   Dimension: {result['dimension']}")
    print()


def example_semantic_search():
    """Example usage of SemanticSearchModel."""
    print("=== Semantic Search Model Example ===\n")

    # Create a corpus of documents
    corpus = [
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks with multiple layers",
        "Natural language processing helps computers understand text",
        "Computer vision enables machines to interpret images",
        "Reinforcement learning trains agents through trial and error",
        "Python is a popular programming language for data science",
        "TensorFlow and PyTorch are deep learning frameworks",
    ]

    # Initialize model with corpus
    print("Initializing semantic search model...")
    model = SemanticSearchModel(corpus=corpus, top_k=3)

    # Search queries
    queries = [
        "neural networks and deep learning",
        "understanding human language",
        "programming tools for AI"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        result = model.run({"query": query})

        for item in result['results']:
            print(f"{item['rank']}. [{item['score']:.3f}] {item['text']}")
    print()


if __name__ == "__main__":
    print("=" * 70)
    print("Text Embeddings and Semantic Search Examples")
    print("=" * 70)
    print()

    # Note: These examples require sentence-transformers to be installed
    print("NOTE: This example requires additional dependencies:")
    print("  pip install sentence-transformers torch numpy")
    print()

    try:
        example_embeddings()
        example_semantic_search()

        print("✅ All examples completed successfully!")

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nInstall with: pip install sentence-transformers torch numpy")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
