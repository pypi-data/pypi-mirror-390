from pydantic import BaseModel, Field
from typing import Optional, Any


class FormField(BaseModel):
    """
    Simple configuration for data collection fields.
    AI handles all validation - no regex or type constraints.
    """
    field_name: str = Field(description="Unique identifier for the field (e.g., 'email', 'budget')")
    description: str = Field(
        description="Description of what information this field aims to collect"
    )
    question_example: Optional[str] = Field(
        default=None,
        description="Example of how AI should ask for this information"
    )
    required: bool = Field(
        default=False,
        description="Whether this field is required"
    )

    @classmethod
    def example_email(cls) -> dict:
        """Example email field"""
        return {
            "field_name": "email",
            "description": "Customer's email address for communication",
            "question_example": "Could you share your email so I can send you more information?",
            "required": True
        }

    @classmethod
    def example_budget(cls) -> dict:
        """Example budget field"""
        return {
            "field_name": "budget",
            "description": "Customer's budget allocation for the project",
            "question_example": "What's your budget range for this project?",
            "required": False
        }


class CollectedData(BaseModel):
    """
    Data collected from customer during conversation.
    AI validates format - we just store strings.
    """
    name: Optional[str] = Field(default=None, description="Customer's name")
    email: Optional[str] = Field(default=None, description="Customer's email address")
    phone: Optional[str] = Field(default=None, description="Customer's phone number")
    document_id: Optional[str] = Field(default=None, description="Customer's DNI/ID number")

    # Generic key-value store for any other collected fields
    additional_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional collected fields as key-value pairs"
    )


    @classmethod
    def example(cls) -> dict:
        """Example collected data"""
        return {
            "email": "customer@example.com",
            "phone": "+5491123456789",
            "dni": "12345678",
            "additional_fields": {
                "budget": "10000-50000",
                "timeline": "this_month",
                "company_size": "25"
            }
        }

    @classmethod
    def get_json_schema_property(cls) -> dict:
        """Returns JSON schema for OpenAI structured output"""
        return {
            "type": "object",
            "properties": {
                "email": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": "Customer's email address if provided"
                },
                "phone": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": "Customer's phone number if provided"
                },
                "dni": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "description": "Customer's DNI/ID number if provided"
                },
                "additional_fields": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Other collected fields as key-value pairs (e.g., budget, timeline)"
                }
            },
            "required": ["email", "phone", "dni", "additional_fields"],
            "additionalProperties": False
        }
