from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import extract, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Movie
from app.schemas import MovieIn, MovieOut
from app.validators import validate_movie

router = APIRouter(prefix="/movies", tags=["movies"], dependencies=[Depends(get_current_user)])


def _get_or_404(db: Session, movie_id: int) -> Movie:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(404, "Movie not found")
    return movie


def _ensure_unique(db: Session, title: str, release_date, exclude_id: int | None = None):
    query = select(Movie).where(Movie.title == title, Movie.release_date == release_date)
    existing = db.scalar(query)
    if existing is not None and existing.id != exclude_id:
        raise HTTPException(409, "Movie with this title and release date already exists")


@router.post("", response_model=MovieOut, status_code=201)
def create_movie(data: MovieIn, db: Session = Depends(get_db)):
    title, genre = validate_movie(data.title, data.genre, data.budget_usd)
    _ensure_unique(db, title, data.release_date)
    movie = Movie(title=title, genre=genre, release_date=data.release_date, budget_usd=data.budget_usd)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.get("", response_model=list[MovieOut])
def list_movies(
    genre: str | None = None,
    year: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(Movie).order_by(Movie.id)
    if genre:
        query = query.where(Movie.genre == genre)
    if year:
        query = query.where(extract("year", Movie.release_date) == year)
    return db.scalars(query.limit(limit).offset(offset)).all()


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, movie_id)


@router.put("/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, data: MovieIn, db: Session = Depends(get_db)):
    movie = _get_or_404(db, movie_id)
    title, genre = validate_movie(data.title, data.genre, data.budget_usd)
    _ensure_unique(db, title, data.release_date, exclude_id=movie_id)
    movie.title, movie.genre = title, genre
    movie.release_date, movie.budget_usd = data.release_date, data.budget_usd
    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = _get_or_404(db, movie_id)
    db.delete(movie)
    db.commit()
    return Response(status_code=204)
