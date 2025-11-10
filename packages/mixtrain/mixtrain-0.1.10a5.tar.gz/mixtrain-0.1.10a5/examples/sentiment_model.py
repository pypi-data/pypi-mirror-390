#!/usr/bin/env python3
"""
Example sentiment analysis model using MixModel.

This example demonstrates how to create a native model that can be deployed
and managed through the Mixtrain platform. It shows:
- How to extend MixModel
- How to define configurable parameters with mixparam()
- How to implement run() for single inference
- How to implement run_batch() for batch inference
- How to use the model with the Mixtrain client

The model performs sentiment analysis on text inputs and returns
sentiment scores (positive, negative, neutral).
"""

from mixtrain import MixModel, mixparam


class SentimentAnalysisModel(MixModel):
    """
    A sentiment analysis model that classifies text as positive, negative, or neutral.

    This model demonstrates the MixModel pattern for creating deployable models
    that can be run through the Mixtrain platform.
    """

    # Define configurable parameters using mixparam()
    confidence_threshold: float = mixparam(
        default=0.5,
        description="Minimum confidence score to return a sentiment (0.0-1.0)"
    )

    return_scores: bool = mixparam(
        default=True,
        description="Whether to return confidence scores along with sentiment labels"
    )

    language: str = mixparam(
        default="en",
        description="Language code for text analysis (e.g., 'en', 'es', 'fr')"
    )

    def __init__(self, **kwargs):
        """
        Initialize the sentiment analysis model.

        Args:
            **kwargs: Configuration parameters (confidence_threshold, return_scores, language)
        """
        super().__init__(**kwargs)

        # In a real implementation, you would load your model here
        # For this example, we'll use a simple rule-based approach
        self.positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best'}
        self.negative_words = {'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'poor', 'disappointing'}

    def run(self, inputs=None):
        """
        Perform sentiment analysis on a single text input.

        Args:
            inputs: Dictionary with 'text' key containing the text to analyze
                   Example: {"text": "This is a great product!"}

        Returns:
            Dictionary with sentiment analysis results:
            {
                "sentiment": "positive" | "negative" | "neutral",
                "confidence": 0.85,  # Only if return_scores=True
                "text": "original text",
                "language": "en"
            }
        """
        if not inputs or 'text' not in inputs:
            raise ValueError("Input must contain 'text' key with text to analyze")

        text = inputs['text']

        # Simple sentiment analysis (in production, use a real model)
        words = set(text.lower().split())
        positive_count = len(words & self.positive_words)
        negative_count = len(words & self.negative_words)

        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.6 + (positive_count * 0.1), 0.99)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.6 + (negative_count * 0.1), 0.99)
        else:
            sentiment = "neutral"
            confidence = 0.5

        # Apply confidence threshold
        if confidence < self.config.get('confidence_threshold', 0.5):
            sentiment = "neutral"
            confidence = 0.5

        # Build response
        result = {
            "sentiment": sentiment,
            "text": text,
            "language": self.config.get('language', 'en')
        }

        if self.config.get('return_scores', True):
            result["confidence"] = round(confidence, 2)

        return result

    def run_batch(self, batch):
        """
        Perform sentiment analysis on a batch of text inputs.

        Args:
            batch: List of dictionaries, each with 'text' key
                  Example: [{"text": "Great!"}, {"text": "Terrible."}]

        Returns:
            List of sentiment analysis results, one per input
        """
        # Default implementation processes each item individually
        # In production, you might optimize batch processing
        return [self.run(inputs) for inputs in batch]


def example_usage():
    """Demonstrate how to use the SentimentAnalysisModel."""
    print("=== Sentiment Analysis Model Example ===\n")

    # Example 1: Basic usage with default parameters
    print("Example 1: Basic Usage")
    print("-" * 50)
    model = SentimentAnalysisModel()

    result = model.run({"text": "This is a great product! I love it!"})
    print(f"Input: {result['text']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence']}")
    print()

    # Example 2: Custom parameters
    print("Example 2: Custom Parameters")
    print("-" * 50)
    model = SentimentAnalysisModel(
        confidence_threshold=0.7,
        return_scores=True,
        language="en"
    )

    result = model.run({"text": "The service was okay."})
    print(f"Input: {result['text']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence']}")
    print()

    # Example 3: Batch processing
    print("Example 3: Batch Processing")
    print("-" * 50)
    model = SentimentAnalysisModel()

    batch = [
        {"text": "Excellent service and quality!"},
        {"text": "Terrible experience, very disappointing."},
        {"text": "It was okay, nothing special."}
    ]

    results = model.run_batch(batch)
    for i, result in enumerate(results, 1):
        print(f"{i}. '{result['text'][:40]}...'")
        print(f"   Sentiment: {result['sentiment']} (confidence: {result.get('confidence', 'N/A')})")
    print()

    # Example 4: Without scores
    print("Example 4: Without Confidence Scores")
    print("-" * 50)
    model = SentimentAnalysisModel(return_scores=False)

    result = model.run({"text": "This product is amazing!"})
    print(f"Input: {result['text']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Has confidence score: {'confidence' in result}")
    print()


def example_deployment():
    """
    Demonstrate how to deploy this model to the Mixtrain platform.

    To deploy this model:

    1. Save this file (sentiment_model.py) in your workspace

    2. Upload to Mixtrain via the UI or CLI:
       ```
       # Via CLI (from workspace directory)
       mixtrain model create sentiment-analysis --file sentiment_model.py

       # Via UI
       - Navigate to Models tab
       - Click "Create Model"
       - Upload sentiment_model.py
       - Name it "sentiment-analysis"
       ```

    3. Run the model via API:
       ```python
       from mixtrain import MixClient

       client = MixClient()

       # Run single inference
       result = client.run_model(
           "workspace-name/models/sentiment-analysis",
           inputs={"text": "This is great!"},
           config={
               "confidence_threshold": 0.6,
               "return_scores": True
           }
       )

       # Run batch inference
       results = client.run_model_batch(
           "workspace-name/models/sentiment-analysis",
           batch=[
               {"text": "Positive text"},
               {"text": "Negative text"}
           ]
       )
       ```

    4. View runs and logs in the Mixtrain UI:
       - Navigate to workspace/models/sentiment-analysis
       - View run history, parameters, and outputs
    """
    print("=== Deployment Instructions ===\n")
    print("See the docstring above for deployment instructions.")
    print("This model can be deployed to Mixtrain and run via API or UI.")
    print()


if __name__ == "__main__":
    # Run examples
    example_usage()
    example_deployment()

    print("✅ All examples completed successfully!")
    print("\nNext steps:")
    print("1. Modify this model for your use case")
    print("2. Deploy to Mixtrain platform")
    print("3. Run inference via API or UI")
