from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import BoxOfficeReport as R
from app.models import Movie

router = APIRouter(tags=["analytics"], dependencies=[Depends(get_current_user)])


def _roi(total_revenue: int, budget: int) -> float:
    return round((total_revenue - budget) / budget, 4)


@router.get("/movies/{movie_id}/summary")
def movie_summary(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(404, "Movie not found")
    total_revenue, total_tickets = db.execute(
        select(func.coalesce(func.sum(R.revenue_usd), 0), func.coalesce(func.sum(R.tickets_sold), 0))
        .where(R.movie_id == movie_id)
    ).one()
    by_region = db.execute(
        select(R.region, func.sum(R.revenue_usd).label("revenue"))
        .where(R.movie_id == movie_id)
        .group_by(R.region)
        .order_by(func.sum(R.revenue_usd).desc())
    ).all()
    return {
        "movie_id": movie.id,
        "title": movie.title,
        "budget_usd": movie.budget_usd,
        "total_revenue_usd": total_revenue,
        "total_tickets": total_tickets,
        "avg_ticket_price_usd": round(total_revenue / total_tickets, 2) if total_tickets else None,
        "roi": _roi(total_revenue, movie.budget_usd),
        "revenue_by_region": [{"region": r, "revenue_usd": rev} for r, rev in by_region],
    }


@router.get("/analytics/top")
def top_movies(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    total = func.sum(R.revenue_usd)
    rows = db.execute(
        select(Movie.id, Movie.title, Movie.budget_usd, total, func.sum(R.tickets_sold))
        .join(R, R.movie_id == Movie.id)
        .group_by(Movie.id)
        .order_by(total.desc())
        .limit(limit)
    ).all()
    return [
        {
            "movie_id": mid,
            "title": title,
            "total_revenue_usd": revenue,
            "total_tickets": tickets,
            "roi": _roi(revenue, budget),
        }
        for mid, title, budget, revenue, tickets in rows
    ]


@router.get("/analytics/regions")
def revenue_by_region(db: Session = Depends(get_db)):
    total = func.sum(R.revenue_usd)
    rows = db.execute(select(R.region, total).group_by(R.region).order_by(total.desc())).all()
    return [{"region": region, "revenue_usd": revenue} for region, revenue in rows]
