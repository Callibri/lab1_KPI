from datetime import date

from pydantic import BaseModel, ConfigDict


class RegisterIn(BaseModel):
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MovieIn(BaseModel):
    title: str
    genre: str
    release_date: date
    budget_usd: int


class MovieOut(MovieIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ReportIn(BaseModel):
    report_date: date
    region: str
    revenue_usd: int
    tickets_sold: int


class ReportUpdateIn(BaseModel):
    revenue_usd: int
    tickets_sold: int


class ReportOut(ReportIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    movie_id: int
