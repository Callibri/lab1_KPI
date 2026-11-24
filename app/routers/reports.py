from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import BoxOfficeReport, Movie
from app.schemas import ReportIn, ReportOut, ReportUpdateIn
from app.validators import validate_amounts, validate_report

router = APIRouter(tags=["reports"], dependencies=[Depends(get_current_user)])


def _movie_or_404(db: Session, movie_id: int) -> Movie:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(404, "Movie not found")
    return movie


def _report_or_404(db: Session, report_id: int) -> BoxOfficeReport:
    report = db.get(BoxOfficeReport, report_id)
    if report is None:
        raise HTTPException(404, "Report not found")
    return report


@router.post("/movies/{movie_id}/reports", response_model=ReportOut, status_code=201)
def create_report(movie_id: int, data: ReportIn, db: Session = Depends(get_db)):
    movie = _movie_or_404(db, movie_id)
    region = validate_report(
        data.report_date, movie.release_date, data.region, data.revenue_usd, data.tickets_sold
    )
    duplicate = db.scalar(
        select(BoxOfficeReport).where(
            BoxOfficeReport.movie_id == movie_id,
            BoxOfficeReport.report_date == data.report_date,
            BoxOfficeReport.region == region,
        )
    )
    if duplicate:
        raise HTTPException(409, "Report for this movie, date and region already exists")
    report = BoxOfficeReport(
        movie_id=movie_id,
        report_date=data.report_date,
        region=region,
        revenue_usd=data.revenue_usd,
        tickets_sold=data.tickets_sold,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/movies/{movie_id}/reports", response_model=list[ReportOut])
def list_reports(
    movie_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
):
    _movie_or_404(db, movie_id)
    query = select(BoxOfficeReport).where(BoxOfficeReport.movie_id == movie_id)
    if date_from:
        query = query.where(BoxOfficeReport.report_date >= date_from)
    if date_to:
        query = query.where(BoxOfficeReport.report_date <= date_to)
    if region:
        query = query.where(BoxOfficeReport.region == region.upper())
    return db.scalars(query.order_by(BoxOfficeReport.report_date)).all()


@router.put("/reports/{report_id}", response_model=ReportOut)
def update_report(report_id: int, data: ReportUpdateIn, db: Session = Depends(get_db)):
    report = _report_or_404(db, report_id)
    validate_amounts(data.revenue_usd, data.tickets_sold)
    report.revenue_usd, report.tickets_sold = data.revenue_usd, data.tickets_sold
    db.commit()
    db.refresh(report)
    return report


@router.delete("/reports/{report_id}", status_code=204)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = _report_or_404(db, report_id)
    db.delete(report)
    db.commit()
    return Response(status_code=204)
