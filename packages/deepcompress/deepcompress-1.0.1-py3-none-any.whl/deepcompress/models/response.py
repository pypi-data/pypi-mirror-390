"""
Response models for API results.
"""

from typing import Any

from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """
    Response from LLM query.

    Attributes:
        text: Generated response text
        tokens_used: Total tokens used (input + output)
        processing_time_ms: Processing time in milliseconds
        model: Model used for generation
        metadata: Additional metadata
    """

    text: str = Field(..., description="Generated response text")
    tokens_used: int = Field(..., ge=0, description="Total tokens used")
    processing_time_ms: float = Field(..., ge=0, description="Processing time in ms")
    model: str = Field(..., description="Model identifier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CompressionResult(BaseModel):
    """
    Result of document compression and optional LLM analysis.

    Attributes:
        document_id: Unique document identifier
        original_tokens: Original token count before compression
        compressed_tokens: Token count after compression
        compression_ratio: Compression ratio (original / compressed)
        optimized_text: D-TOON optimized text
        answer: LLM answer (if query provided)
        processing_time_ms: Total processing time in milliseconds
        tokens_saved: Number of tokens saved
        cost_saved_usd: Cost saved in USD (based on GPT-4o pricing)
        cache_hit: Whether result was served from cache
        metadata: Additional metadata
    """

    document_id: str = Field(..., description="Unique document identifier")
    original_tokens: int = Field(..., ge=0, description="Original token count")
    compressed_tokens: int = Field(..., ge=0, description="Compressed token count")
    compression_ratio: float = Field(..., ge=1.0, description="Compression ratio")
    optimized_text: str = Field(..., description="D-TOON optimized text")
    answer: str  or None = Field(None, description="LLM answer")
    processing_time_ms: float = Field(..., ge=0, description="Processing time in ms")
    tokens_saved: int = Field(..., ge=0, description="Tokens saved")
    cost_saved_usd: float = Field(..., ge=0, description="Cost saved in USD")
    cache_hit: bool = Field(default=False, description="Whether cached")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def to_json(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "CompressionResult":
        """Create from JSON dictionary."""
        return cls.model_validate(data)


class BatchResult(BaseModel):
    """
    Result of batch processing operation.

    Attributes:
        total_documents: Total documents processed
        successful: Number of successful documents
        failed: Number of failed documents
        total_tokens_saved: Total tokens saved across all documents
        total_cost_saved_usd: Total cost saved in USD
        total_processing_time_ms: Total processing time in ms
        throughput_pages_per_sec: Processing throughput
        cache_hit_rate: Cache hit rate (0.0-1.0)
        errors: List of error messages for failed documents
        metadata: Additional metadata
    """

    total_documents: int = Field(..., ge=0, description="Total documents")
    successful: int = Field(..., ge=0, description="Successful documents")
    failed: int = Field(..., ge=0, description="Failed documents")
    total_tokens_saved: int = Field(..., ge=0, description="Total tokens saved")
    total_cost_saved_usd: float = Field(..., ge=0, description="Total cost saved")
    total_processing_time_ms: float = Field(..., ge=0, description="Total processing time")
    throughput_pages_per_sec: float = Field(..., ge=0, description="Pages per second")
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0, description="Cache hit rate")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

