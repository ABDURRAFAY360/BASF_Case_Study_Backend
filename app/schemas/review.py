from pydantic import BaseModel, Field, conint

class ReviewUpsertRequest(BaseModel):
    rating: conint(ge=1, le=5)
    review_text: str = Field(default=None, max_length=2048)

class ReviewRead(BaseModel):
    id: int
    book_id: int
    username: str
    rating: int
    review_text: str
    model_config = {"from_attributes": True}
