#!/usr/bin/env python3
"""
Example FAL model wrapper using MixModel with fal-client.

This example demonstrates:
- Wrapping FAL models (fal.ai) in MixModel
- Using external FAL models (flux, stable-diffusion, etc.)
- Handling async FAL operations
- Working with image generation models
- Configuring FAL-specific parameters

FAL provides serverless inference for various AI models including:
- Text-to-image (FLUX, Stable Diffusion)
- Image-to-image
- Video generation
- And more

Requirements:
    pip install fal-client

Setup:
    Set FAL_KEY environment variable with your FAL API key
    export FAL_KEY="your-fal-api-key"
"""

from mixtrain import MixModel, mixparam
import os


class FalImageModel(MixModel):
    """
    Wrapper for FAL text-to-image models.

    This model wraps FAL's image generation models and can be used
    with various FAL models like FLUX Pro, Stable Diffusion, etc.

    Requirements:
        - fal-client
        - FAL_KEY environment variable
    """

    fal_model_id: str = mixparam(
        default="fal-ai/flux-pro",
        description="FAL model ID (e.g., 'fal-ai/flux-pro', 'fal-ai/stable-diffusion-v3-medium')"
    )

    image_size: str = mixparam(
        default="landscape_4_3",
        description="Image size preset (square, square_hd, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9)"
    )

    num_inference_steps: int = mixparam(
        default=28,
        description="Number of inference steps (more steps = higher quality, slower)"
    )

    guidance_scale: float = mixparam(
        default=3.5,
        description="Guidance scale for prompt adherence (higher = more faithful to prompt)"
    )

    num_images: int = mixparam(
        default=1,
        description="Number of images to generate"
    )

    enable_safety_checker: bool = mixparam(
        default=True,
        description="Enable safety checker to filter inappropriate content"
    )

    output_format: str = mixparam(
        default="jpeg",
        description="Output image format (jpeg or png)"
    )

    def __init__(self, **kwargs):
        """
        Initialize the FAL image model.

        Args:
            **kwargs: Configuration parameters
        """
        super().__init__(**kwargs)

        # Import fal client
        try:
            import fal_client
        except ImportError as e:
            raise ImportError(
                "This model requires fal-client. "
                "Install with: pip install fal-client"
            ) from e

        self.fal_client = fal_client

        # Check for FAL_KEY
        if not os.getenv("FAL_KEY"):
            raise ValueError(
                "FAL_KEY environment variable not set. "
                "Get your key from https://fal.ai/dashboard/keys"
            )

        print(f"FAL model initialized: {self.config.get('fal_model_id', 'fal-ai/flux-pro')}")

    def run(self, inputs=None):
        """
        Generate an image from a text prompt.

        Args:
            inputs: Dictionary with 'prompt' key
                   Example: {"prompt": "A beautiful sunset over mountains"}

        Returns:
            Dictionary with:
            {
                "images": [{"url": "...", "width": 1024, "height": 768}],
                "prompt": "original prompt",
                "model": "fal-ai/flux-pro",
                "seed": 12345,
                "has_nsfw_concepts": [False]
            }
        """
        if not inputs or 'prompt' not in inputs:
            raise ValueError("Input must contain 'prompt' key")

        prompt = inputs['prompt']

        # Get configuration
        fal_model_id = self.config.get('fal_model_id', 'fal-ai/flux-pro')

        # Build arguments for FAL API
        arguments = {
            "prompt": prompt,
            "image_size": self.config.get('image_size', 'landscape_4_3'),
            "num_inference_steps": self.config.get('num_inference_steps', 28),
            "guidance_scale": self.config.get('guidance_scale', 3.5),
            "num_images": self.config.get('num_images', 1),
            "enable_safety_checker": self.config.get('enable_safety_checker', True),
            "output_format": self.config.get('output_format', 'jpeg'),
        }

        # Add optional seed if provided
        if 'seed' in inputs:
            arguments['seed'] = inputs['seed']

        # Call FAL API
        result = self.fal_client.subscribe(
            fal_model_id,
            arguments=arguments
        )

        # Format response
        return {
            "images": result.get("images", []),
            "prompt": prompt,
            "model": fal_model_id,
            "seed": result.get("seed"),
            "has_nsfw_concepts": result.get("has_nsfw_concepts", []),
            "timings": result.get("timings", {}),
        }

    def run_batch(self, batch):
        """
        Generate images for multiple prompts.

        Args:
            batch: List of dictionaries with 'prompt' keys
                  Example: [{"prompt": "sunset"}, {"prompt": "mountains"}]

        Returns:
            List of image generation results
        """
        # Note: FAL supports batch processing, but for simplicity
        # we'll process sequentially. You could optimize this with
        # async operations.
        return [self.run(item) for item in batch]


class FalImageToImageModel(MixModel):
    """
    Wrapper for FAL image-to-image models.

    This model takes an input image and transforms it based on a prompt.
    """

    fal_model_id: str = mixparam(
        default="fal-ai/flux-pro",
        description="FAL model ID for image-to-image"
    )

    strength: float = mixparam(
        default=0.75,
        description="How much to transform the image (0.0-1.0, higher = more change)"
    )

    num_inference_steps: int = mixparam(
        default=28,
        description="Number of inference steps"
    )

    guidance_scale: float = mixparam(
        default=3.5,
        description="Guidance scale for prompt adherence"
    )

    def __init__(self, **kwargs):
        """Initialize the FAL image-to-image model."""
        super().__init__(**kwargs)

        try:
            import fal_client
        except ImportError as e:
            raise ImportError(
                "This model requires fal-client. "
                "Install with: pip install fal-client"
            ) from e

        self.fal_client = fal_client

        if not os.getenv("FAL_KEY"):
            raise ValueError("FAL_KEY environment variable not set")

        print(f"FAL image-to-image model initialized: {self.config.get('fal_model_id')}")

    def run(self, inputs=None):
        """
        Transform an image based on a prompt.

        Args:
            inputs: Dictionary with 'prompt' and 'image_url' keys
                   Example: {
                       "prompt": "turn this into a watercolor painting",
                       "image_url": "https://example.com/image.jpg"
                   }

        Returns:
            Dictionary with transformed image results
        """
        if not inputs or 'prompt' not in inputs or 'image_url' not in inputs:
            raise ValueError("Input must contain 'prompt' and 'image_url' keys")

        prompt = inputs['prompt']
        image_url = inputs['image_url']

        fal_model_id = self.config.get('fal_model_id', 'fal-ai/flux-pro')

        arguments = {
            "prompt": prompt,
            "image_url": image_url,
            "strength": self.config.get('strength', 0.75),
            "num_inference_steps": self.config.get('num_inference_steps', 28),
            "guidance_scale": self.config.get('guidance_scale', 3.5),
        }

        if 'seed' in inputs:
            arguments['seed'] = inputs['seed']

        result = self.fal_client.subscribe(
            fal_model_id,
            arguments=arguments
        )

        return {
            "images": result.get("images", []),
            "prompt": prompt,
            "input_image": image_url,
            "model": fal_model_id,
            "seed": result.get("seed"),
            "timings": result.get("timings", {}),
        }

    def run_batch(self, batch):
        """Transform multiple images."""
        return [self.run(item) for item in batch]


class FalGenericModel(MixModel):
    """
    Generic FAL model wrapper that can work with any FAL model.

    This is a flexible wrapper that lets you specify any FAL model
    and pass arbitrary arguments.
    """

    fal_model_id: str = mixparam(
        default="fal-ai/flux-pro",
        description="FAL model ID (any model from fal.ai)"
    )

    def __init__(self, **kwargs):
        """Initialize the generic FAL model."""
        super().__init__(**kwargs)

        try:
            import fal_client
        except ImportError as e:
            raise ImportError(
                "This model requires fal-client. "
                "Install with: pip install fal-client"
            ) from e

        self.fal_client = fal_client

        if not os.getenv("FAL_KEY"):
            raise ValueError("FAL_KEY environment variable not set")

        print(f"FAL generic model initialized: {self.config.get('fal_model_id')}")

    def run(self, inputs=None):
        """
        Run any FAL model with arbitrary inputs.

        Args:
            inputs: Dictionary with model-specific parameters
                   The entire dictionary is passed to FAL as arguments

        Returns:
            Raw FAL model output
        """
        if not inputs:
            raise ValueError("Input dictionary is required")

        fal_model_id = self.config.get('fal_model_id', 'fal-ai/flux-pro')

        # Pass all inputs directly to FAL
        result = self.fal_client.subscribe(
            fal_model_id,
            arguments=inputs
        )

        return result

    def run_batch(self, batch):
        """Run model on multiple inputs."""
        return [self.run(item) for item in batch]


def example_text_to_image():
    """Example usage of FalImageModel for text-to-image generation."""
    print("=== FAL Text-to-Image Example ===\n")

    print("Note: Set FAL_KEY environment variable before running")
    print("export FAL_KEY='your-fal-api-key'\n")

    if not os.getenv("FAL_KEY"):
        print("⚠️  FAL_KEY not set. Skipping examples.")
        return

    # Initialize model
    print("Initializing FAL FLUX Pro model...")
    model = FalImageModel(
        fal_model_id="fal-ai/flux-pro",
        image_size="landscape_16_9",
        num_inference_steps=28,
        guidance_scale=3.5
    )

    # Single image generation
    print("\nExample 1: Single Image Generation")
    print("-" * 50)
    result = model.run({
        "prompt": "A serene landscape with mountains at sunset, highly detailed, cinematic lighting"
    })
    print(f"Prompt: {result['prompt']}")
    print(f"Generated {len(result['images'])} image(s)")
    if result['images']:
        print(f"Image URL: {result['images'][0]['url']}")
        print(f"Dimensions: {result['images'][0]['width']}x{result['images'][0]['height']}")
    print(f"Seed: {result['seed']}")
    print()

    # Batch generation
    print("Example 2: Batch Image Generation")
    print("-" * 50)
    batch = [
        {"prompt": "A futuristic city at night"},
        {"prompt": "An abstract painting with vibrant colors"},
        {"prompt": "A cozy coffee shop interior"}
    ]
    results = model.run_batch(batch)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['prompt'][:40]}...")
        print(f"   Images generated: {len(result['images'])}")
    print()


def example_image_to_image():
    """Example usage of FalImageToImageModel."""
    print("=== FAL Image-to-Image Example ===\n")

    if not os.getenv("FAL_KEY"):
        print("⚠️  FAL_KEY not set. Skipping examples.")
        return

    print("Initializing FAL image-to-image model...")
    model = FalImageToImageModel(
        fal_model_id="fal-ai/flux-pro",
        strength=0.8,
        num_inference_steps=28
    )

    print("\nExample: Transform Image")
    print("-" * 50)
    result = model.run({
        "prompt": "turn this into a watercolor painting style",
        "image_url": "https://example.com/input-image.jpg"
    })
    print(f"Prompt: {result['prompt']}")
    print(f"Input image: {result['input_image']}")
    print(f"Output images: {len(result['images'])}")
    print()


def example_generic_model():
    """Example usage of FalGenericModel for any FAL model."""
    print("=== FAL Generic Model Example ===\n")

    if not os.getenv("FAL_KEY"):
        print("⚠️  FAL_KEY not set. Skipping examples.")
        return

    print("Initializing generic FAL model...")
    model = FalGenericModel(
        fal_model_id="fal-ai/flux-pro"
    )

    print("\nExample: Custom FAL Model Call")
    print("-" * 50)
    result = model.run({
        "prompt": "A beautiful galaxy with stars and nebulas",
        "image_size": "square_hd",
        "num_inference_steps": 40,
        "guidance_scale": 4.0,
        "num_images": 2
    })
    print(f"Model: {model.config['fal_model_id']}")
    print(f"Images generated: {len(result.get('images', []))}")
    print()


def example_deployment():
    """
    Example of deploying FAL models to Mixtrain platform.
    """
    print("=== Deployment Instructions ===\n")
    print("To deploy a FAL model wrapper to Mixtrain:\n")
    print("1. Save this file (fal_model.py) in your workspace")
    print()
    print("2. Set FAL_KEY as an environment variable in Mixtrain:")
    print("   - In workspace settings, add FAL_KEY to environment variables")
    print()
    print("3. Upload to Mixtrain via UI or CLI:")
    print("   mixtrain model create fal-flux-pro --file fal_model.py")
    print()
    print("4. Run the model via API:")
    print("""
   from mixtrain import MixClient

   client = MixClient()

   result = client.run_model(
       "workspace-name/models/fal-flux-pro",
       inputs={
           "prompt": "A beautiful landscape"
       },
       config={
           "fal_model_id": "fal-ai/flux-pro",
           "image_size": "landscape_16_9",
           "num_inference_steps": 28
       }
   )

   print(result["images"][0]["url"])
   """)
    print()


if __name__ == "__main__":
    print("=" * 70)
    print("FAL Model Wrapper Examples")
    print("=" * 70)
    print()

    print("NOTE: These examples require:")
    print("  1. pip install fal-client")
    print("  2. FAL_KEY environment variable set")
    print("  3. Get your key from: https://fal.ai/dashboard/keys")
    print()

    try:
        example_text_to_image()
        example_image_to_image()
        example_generic_model()
        example_deployment()

        print("✅ All examples completed!")
        print("\nNext steps:")
        print("1. Get your FAL API key from https://fal.ai/dashboard/keys")
        print("2. Set FAL_KEY environment variable")
        print("3. Deploy to Mixtrain platform")
        print("4. Use in your workflows and routers")

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nInstall with: pip install fal-client")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
