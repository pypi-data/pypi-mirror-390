# MixModel Examples

This directory contains example models demonstrating how to create native models using the `MixModel` class in Mixtrain.

## Overview

Native models in Mixtrain allow you to deploy custom ML models that can be:
- Run via API calls
- Managed through the Mixtrain UI
- Versioned and tracked
- Integrated with workflows and evaluations

## Example Models

### 1. Sentiment Analysis Model (`sentiment_model.py`)

A simple rule-based sentiment analysis model that demonstrates the basics of MixModel:

**Features:**
- Configurable parameters using `mixparam()`
- Single and batch inference
- Simple implementation without external dependencies

**Usage:**
```python
from sentiment_model import SentimentAnalysisModel

# Create model with default parameters
model = SentimentAnalysisModel()

# Run inference
result = model.run({"text": "This is a great product!"})
print(result)  # {"sentiment": "positive", "confidence": 0.7, ...}

# Batch inference
results = model.run_batch([
    {"text": "Excellent!"},
    {"text": "Terrible."}
])
```

**Parameters:**
- `confidence_threshold` (float, default=0.5): Minimum confidence score
- `return_scores` (bool, default=True): Include confidence scores in output
- `language` (str, default="en"): Language code for analysis

### 2. Text Embeddings Model (`text_embeddings_model.py`)

A more advanced example using pre-trained transformers for text embeddings:

**Features:**
- External dependencies (sentence-transformers, torch)
- Model loading and caching
- Optimized batch processing
- Semantic search capabilities

**Requirements:**
```bash
pip install sentence-transformers torch numpy
```

**Usage:**
```python
from text_embeddings_model import TextEmbeddingsModel

# Create embeddings model
model = TextEmbeddingsModel(model_name="all-MiniLM-L6-v2")

# Generate embedding
result = model.run({"text": "Machine learning is fascinating"})
print(result['embedding'][:5])  # [0.1, 0.2, 0.3, ...]
```

**Parameters:**
- `model_name` (str, default="all-MiniLM-L6-v2"): HuggingFace model name
- `normalize` (bool, default=True): Normalize embeddings to unit length
- `return_numpy` (bool, default=True): Return numpy arrays vs lists
- `max_length` (int, default=512): Maximum sequence length

### 3. FAL Model Wrapper (`fal_model.py`)

A wrapper for FAL.ai models (text-to-image, image-to-image, and more):

**Features:**
- Integration with FAL.ai platform
- Text-to-image generation (FLUX, Stable Diffusion)
- Image-to-image transformation
- Generic FAL model wrapper for any FAL model
- Configurable inference parameters

**Requirements:**
```bash
pip install fal-client
export FAL_KEY="your-fal-api-key"
```

**Usage:**
```python
from fal_model import FalImageModel

# Create FAL image generation model
model = FalImageModel(
    fal_model_id="fal-ai/flux-pro",
    image_size="landscape_16_9"
)

# Generate image from prompt
result = model.run({
    "prompt": "A serene landscape with mountains at sunset"
})
print(result['images'][0]['url'])
```

**Parameters:**
- `fal_model_id` (str, default="fal-ai/flux-pro"): FAL model ID
- `image_size` (str, default="landscape_4_3"): Image size preset
- `num_inference_steps` (int, default=28): Number of inference steps
- `guidance_scale` (float, default=3.5): Guidance scale for prompt adherence
- `num_images` (int, default=1): Number of images to generate
- `enable_safety_checker` (bool, default=True): Enable content filtering
- `output_format` (str, default="jpeg"): Output image format

**Available Models:**
- `FalImageModel`: Text-to-image generation
- `FalImageToImageModel`: Image transformation
- `FalGenericModel`: Generic wrapper for any FAL model

## Creating Your Own Model

### Basic Structure

```python
from mixtrain import MixModel, mixparam

class MyModel(MixModel):
    """Your model description."""

    # Define parameters
    param1 = mixparam(
        default=100,
        param_type=int,
        description="Description of parameter"
    )

    def __init__(self, **kwargs):
        """Initialize your model."""
        super().__init__(**kwargs)
        # Load your model, initialize resources, etc.

    def run(self, inputs=None):
        """Run inference on single input."""
        # Your inference logic
        return {"result": "..."}

    def run_batch(self, batch):
        """Run inference on batch of inputs."""
        return [self.run(item) for item in batch]
```

### Best Practices

1. **Parameter Definition**
   - Use `mixparam()` for all configurable parameters
   - Provide sensible defaults
   - Include clear descriptions

2. **Model Initialization**
   - Load models in `__init__`
   - Handle dependencies gracefully
   - Cache expensive operations

3. **Input/Output Format**
   - Accept dictionaries with clear key names
   - Return structured dictionaries
   - Include metadata in outputs

4. **Batch Processing**
   - Implement `run_batch()` for efficiency
   - Use vectorized operations when possible
   - Process multiple inputs at once

5. **Error Handling**
   - Validate inputs
   - Provide helpful error messages
   - Handle missing dependencies

## Deploying Models to Mixtrain

### Via Web UI

1. Navigate to your workspace in the Mixtrain UI
2. Go to the **Models** tab
3. Click **"Create Model"**
4. Upload your Python file(s)
5. Name your model (e.g., "sentiment-analysis")
6. Click **"Create Model"**

### Via CLI

```bash
# Create a new model
mixtrain model create sentiment-analysis --file sentiment_model.py

# List models
mixtrain model list

# Run inference
mixtrain model run sentiment-analysis --input '{"text": "Great product!"}'

# Run batch inference
mixtrain model run sentiment-analysis --batch batch_inputs.json
```

### Via Python Client

```python
from mixtrain import MixClient

client = MixClient()

# Run model
result = client.run_model(
    "workspace-name/models/sentiment-analysis",
    inputs={"text": "This is great!"},
    config={"confidence_threshold": 0.6}
)

# Run batch
results = client.run_model_batch(
    "workspace-name/models/sentiment-analysis",
    batch=[
        {"text": "Positive text"},
        {"text": "Negative text"}
    ]
)
```

## Running Examples Locally

### Sentiment Analysis Model

```bash
# No additional dependencies needed
python sentiment_model.py
```

Expected output:
```
=== Sentiment Analysis Model Example ===

Example 1: Basic Usage
--------------------------------------------------
Input: This is a great product! I love it!
Sentiment: positive
Confidence: 0.8
...
```

### Text Embeddings Model

```bash
# Install dependencies first
pip install sentence-transformers torch numpy

# Run example
python text_embeddings_model.py
```

Expected output:
```
=== Text Embeddings Model Example ===

Initializing embeddings model...
Loading model: all-MiniLM-L6-v2...
Model loaded successfully. Embedding dimension: 384

Example 1: Single Embedding
--------------------------------------------------
Text: Machine learning is fascinating
Embedding dimension: 384
Embedding (first 5 values): [0.1234, -0.5678, ...]
...
```

### FAL Model Wrapper

```bash
# Install dependencies first
pip install fal-client

# Set FAL API key
export FAL_KEY="your-fal-api-key"

# Run example
python fal_model.py
```

Expected output:
```
=== FAL Text-to-Image Example ===

Initializing FAL FLUX Pro model...
FAL model initialized: fal-ai/flux-pro

Example 1: Single Image Generation
--------------------------------------------------
Prompt: A serene landscape with mountains at sunset...
Generated 1 image(s)
Image URL: https://fal.media/files/...
Dimensions: 1920x1080
Seed: 123456
...
```

**Note:** Get your FAL API key from https://fal.ai/dashboard/keys

## Model Configuration

When running deployed models, you can override parameters:

```python
# Override parameters at runtime
result = client.run_model(
    "workspace/models/my-model",
    inputs={"text": "input"},
    config={
        "param1": custom_value,
        "param2": custom_value
    }
)
```

## Monitoring and Debugging

### View Model Runs

1. Navigate to your workspace
2. Go to Models tab → Select your model
3. View run history with:
   - Input/output data
   - Configuration used
   - Execution time
   - Logs and errors

### Check Logs

```python
# Get recent runs
runs = client.get_model_runs("workspace/models/my-model")

# Get specific run details
run_details = client.get_model_run("workspace/models/my-model", run_number=1)

# View logs
logs = client.get_model_run_logs("workspace/models/my-model", run_number=1)
```

## Advanced Topics

### Using External Dependencies

List all dependencies in a `requirements.txt` file:

```txt
sentence-transformers>=2.0.0
torch>=2.0.0
numpy>=1.24.0
```

Upload it along with your model file when creating the model.

### Model Versioning

Models are versioned automatically. Each update creates a new version:

```python
# Update model
client.update_model(
    "workspace/models/my-model",
    files=["updated_model.py"]
)

# List versions
versions = client.get_model_versions("workspace/models/my-model")
```

### Using Models in Workflows

Models can be called from workflows:

```python
from mixtrain import MixFlow

class MyWorkflow(MixFlow):
    def run(self):
        # Call a model
        result = self.client.run_model(
            "workspace/models/sentiment-analysis",
            inputs={"text": "some text"}
        )
        return result
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution:** Install dependencies:
```bash
pip install sentence-transformers
```

### Model Not Found

**Problem:** `404: Model not found`

**Solution:**
- Check model name is correct
- Ensure model is deployed to the workspace
- Verify you have access to the workspace

### Performance Issues

**Problem:** Model runs slowly

**Solution:**
- Implement `run_batch()` for batch processing
- Use GPU if available
- Cache model loading in `__init__`
- Optimize preprocessing steps

## Additional Resources

- [Mixtrain Documentation](https://docs.mixtrain.ai)
- [MixModel API Reference](https://docs.mixtrain.ai/models)
- [HuggingFace Models](https://huggingface.co/models)
- [Sentence Transformers](https://www.sbert.net/)
- [FAL.ai Platform](https://fal.ai) - Serverless AI inference
- [FAL.ai Models](https://fal.ai/models) - Browse available models

## Contributing

Have a great example model? Submit a PR with:
1. Model implementation
2. Example usage
3. Documentation
4. Requirements (if any)
