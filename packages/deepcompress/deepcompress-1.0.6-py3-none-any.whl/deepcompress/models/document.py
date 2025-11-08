"""
Document data models representing OCR extraction results.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class Entity(BaseModel):
    """
    Extracted entity from document (e.g., bank_name, SSN, date).

    Attributes:
        type: Entity type (bank_name, account_holder, ssn, etc.)
        text: Extracted text value
        bbox: Bounding box [x1, y1, x2, y2] (optional)
        confidence: OCR confidence score (0.0-1.0)
        metadata: Additional metadata
    """

    type: str = Field(..., description="Entity type identifier")
    text: str = Field(..., description="Extracted text value")
    bbox: list[int]  or None = Field(None, description="Bounding box [x1, y1, x2, y2]")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, v: list[int]  or None) -> list[int]  or None:
        if v is not None and len(v) != 4:
            raise ValueError("bbox must contain exactly 4 values: [x1, y1, x2, y2]")
        return v


class Table(BaseModel):
    """
    Extracted table with headers and rows.

    Attributes:
        headers: Column headers
        rows: Table rows (list of lists)
        bbox: Bounding box [x1, y1, x2, y2] (optional)
        confidence: OCR confidence score (0.0-1.0)
        metadata: Additional metadata
    """

    headers: list[str] = Field(..., description="Column headers")
    rows: list[list[str]] = Field(..., description="Table rows")
    bbox: list[int]  or None = Field(None, description="Bounding box [x1, y1, x2, y2]")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, v: list[int]  or None) -> list[int]  or None:
        if v is not None and len(v) != 4:
            raise ValueError("bbox must contain exactly 4 values: [x1, y1, x2, y2]")
        return v

    @field_validator("rows")
    @classmethod
    def validate_rows(cls, v: list[list[str]], info: Any) -> list[list[str]]:
        if not v:
            return v
        headers_len = len(info.data.get("headers", []))
        for i, row in enumerate(v):
            if len(row) != headers_len:
                raise ValueError(
                    f"Row {i} has {len(row)} columns but headers have {headers_len}"
                )
        return v


class Page(BaseModel):
    """
    Single page from a document with extracted entities and tables.

    Attributes:
        page_number: 1-indexed page number
        layout: Layout type (single_column, multi_column, form, etc.)
        entities: Extracted entities
        tables: Extracted tables
        raw_text: Raw OCR text (optional)
        metadata: Additional metadata
    """

    page_number: int = Field(..., ge=1, description="Page number (1-indexed)")
    layout: str = Field(default="single_column", description="Page layout type")
    entities: list[Entity] = Field(default_factory=list, description="Extracted entities")
    tables: list[Table] = Field(default_factory=list, description="Extracted tables")
    raw_text: str  or None = Field(None, description="Raw OCR text")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ExtractedDocument(BaseModel):
    """
    Complete extracted document with all pages.

    Attributes:
        document_id: Unique document identifier
        page_count: Total number of pages
        mode: OCR mode used (small, base, large)
        pages: List of extracted pages
        metadata: Additional metadata
    """

    document_id: str = Field(..., description="Unique document identifier")
    page_count: int = Field(..., ge=1, description="Total number of pages")
    mode: str = Field(default="small", description="OCR mode (small, base, large)")
    pages: list[Page] = Field(..., description="Extracted pages")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("pages")
    @classmethod
    def validate_pages(cls, v: list[Page], info: Any) -> list[Page]:
        page_count = info.data.get("page_count", 0)
        if len(v) != page_count:
            raise ValueError(f"Expected {page_count} pages but got {len(v)}")
        return v

    def to_json(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "ExtractedDocument":
        """Create from JSON dictionary."""
        return cls.model_validate(data)

