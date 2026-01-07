from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    username: str
    role: str
    company: str | None = None
    level: str | None = None  # 级别：SECTION_CHIEF(科长), DIRECTOR(处长), BUREAU_CHIEF(局长)
