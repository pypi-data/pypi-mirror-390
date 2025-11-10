from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class Condition(BaseModel):
    """Single condition update schema"""

    condition: str = Field(description="Test condition to update")
    is_verified: bool = Field(
        default=False, description="Whether condition is verified (true/false)"
    )
    evidence: str | None = Field(
        default=None,
        description="Evidence for the verification, or null if no evidence",
    )
    step_number: SkipJsonSchema[int | None] = Field(
        default=None, description="Step number where evidence was found, or null"
    )
    confidence: int | None = Field(
        default=None, ge=0, le=100, description="Confidence of the evidence (0-100)"
    )

    def __str__(self):
        status = "✅" if self.is_verified else "❌"
        return f"{status}({self.confidence or 0}%) {self.condition} ({self.evidence})"
