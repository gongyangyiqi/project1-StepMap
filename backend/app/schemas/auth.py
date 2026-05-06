from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        lowered = value.strip().lower()
        if "@" not in lowered or lowered.startswith("@") or lowered.endswith("@"):
            raise ValueError("Email format is invalid.")
        return lowered


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        lowered = value.strip().lower()
        if "@" not in lowered or lowered.startswith("@") or lowered.endswith("@"):
            raise ValueError("Email format is invalid.")
        return lowered


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
