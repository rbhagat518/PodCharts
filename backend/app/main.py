from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.db import get_connection
from app.auth import get_current_user, require_auth, require_pro, check_api_quota, record_api_usage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PodCharts API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def api_usage_middleware(request: Request, call_next):
    """Track API usage for rate limiting."""
    response = await call_next(request)
    
    # Track API usage if authenticated
    api_key = request.headers.get("X-API-Key")
    if api_key and request.url.path.startswith("/api/"):
        try:
            user = await get_current_user(api_key=api_key)
            if user:
                user_id = UUID(user["id"]) if isinstance(user["id"], str) else user["id"]
                await record_api_usage(user_id, api_key, request.url.path)
        except Exception:
            # Ignore errors in middleware
            pass
    
    return response


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/leaderboard")
async def get_leaderboard(
    category: str | None = Query(None, description="Filter by category"),
    country: str | None = Query(None, description="Filter by country (e.g., 'us', 'global')"),
    interval: str = Query("daily", description="Time interval: daily, weekly, monthly"),
    sort_by: str = Query("rank", description="Sort by: rank, momentum, delta_7d, delta_30d"),
    limit: int = Query(100, description="Limit results"),
    search: str | None = Query(None, description="Search by title or publisher"),
):
    """Get leaderboard of podcasts with rankings and metrics."""
    from psycopg.rows import dict_row
    
    today = date.today()
    
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                # Determine date range based on interval
                if interval == "weekly":
                    start_date = today - timedelta(days=7)
                    query = """
                        SELECT 
                            p.id,
                            p.title,
                            p.publisher,
                            p.category,
                            p.country,
                            AVG(m.rank)::INTEGER as rank,
                            AVG(m.delta_7d)::INTEGER as delta_7d,
                            AVG(m.delta_30d)::INTEGER as delta_30d,
                            AVG(m.momentum_score) as momentum_score,
                            MAX(m.captured_on) as captured_on
                        FROM metrics_daily m
                        JOIN podcasts p ON p.id = m.podcast_id
                        WHERE m.captured_on >= %s AND m.captured_on <= %s
                    """
                    params: list[Any] = [start_date, today]
                elif interval == "monthly":
                    start_date = today - timedelta(days=30)
                    query = """
                        SELECT 
                            p.id,
                            p.title,
                            p.publisher,
                            p.category,
                            p.country,
                            AVG(m.rank)::INTEGER as rank,
                            AVG(m.delta_7d)::INTEGER as delta_7d,
                            AVG(m.delta_30d)::INTEGER as delta_30d,
                            AVG(m.momentum_score) as momentum_score,
                            MAX(m.captured_on) as captured_on
                        FROM metrics_daily m
                        JOIN podcasts p ON p.id = m.podcast_id
                        WHERE m.captured_on >= %s AND m.captured_on <= %s
                    """
                    params: list[Any] = [start_date, today]
                else:
                    query = """
                        SELECT 
                            p.id,
                            p.title,
                            p.publisher,
                            p.category,
                            p.country,
                            m.rank,
                            m.delta_7d,
                            m.delta_30d,
                            m.momentum_score,
                            m.captured_on
                        FROM metrics_daily m
                        JOIN podcasts p ON p.id = m.podcast_id
                        WHERE m.captured_on = %s
                    """
                    params: list[Any] = [today]
                
                if category:
                    query += " AND p.category = %s"
                    params.append(category)
                
                if country:
                    query += " AND p.country = %s"
                    params.append(country.lower())
                
                if search:
                    query += " AND (p.title ILIKE %s OR p.publisher ILIKE %s)"
                    search_term = f"%{search}%"
                    params.append(search_term)
                    params.append(search_term)
                
                if interval in ("weekly", "monthly"):
                    query += " GROUP BY p.id, p.title, p.publisher, p.category, p.country"
                
                # Sorting
                if interval in ("weekly", "monthly"):
                    sort_column = {
                        "rank": "AVG(m.rank)",
                        "momentum": "AVG(m.momentum_score)",
                        "delta_7d": "AVG(m.delta_7d)",
                        "delta_30d": "AVG(m.delta_30d)",
                    }.get(sort_by, "AVG(m.rank)")
                else:
                    sort_column = {
                        "rank": "m.rank",
                        "momentum": "m.momentum_score",
                        "delta_7d": "m.delta_7d",
                        "delta_30d": "m.delta_30d",
                    }.get(sort_by, "m.rank")
                
                query += f" ORDER BY {sort_column} ASC NULLS LAST LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "category": row["category"],
                        "country": row["country"],
                        "rank": row["rank"],
                        "delta_7d": row["delta_7d"],
                        "delta_30d": row["delta_30d"],
                        "momentum_score": float(row["momentum_score"]) if row["momentum_score"] is not None else None,
                    }
                    for row in rows
                ]
                
                return {
                    "category": category,
                    "country": country or "all",
                    "interval": interval,
                    "sort_by": sort_by,
                    "search": search,
                    "captured_on": today.isoformat(),
                    "items": items,
                }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trending")
async def get_trending(
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(20, description="Limit results"),
):
    """Get trending podcasts based on momentum and recent growth."""
    from psycopg.rows import dict_row
    
    today = date.today()
    
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                query = """
                    SELECT 
                        p.id,
                        p.title,
                        p.publisher,
                        p.category,
                        p.country,
                        m.rank,
                        m.delta_7d,
                        m.delta_30d,
                        m.momentum_score,
                        m.captured_on
                    FROM metrics_daily m
                    JOIN podcasts p ON p.id = m.podcast_id
                    WHERE m.captured_on = %s
                    AND m.momentum_score IS NOT NULL
                    AND m.momentum_score > 0
                """
                params: list[Any] = [today]
                
                if category:
                    query += " AND p.category = %s"
                    params.append(category)
                
                query += " ORDER BY m.momentum_score DESC, m.delta_7d DESC NULLS LAST LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "category": row["category"],
                        "country": row["country"],
                        "rank": row["rank"],
                        "delta_7d": row["delta_7d"],
                        "delta_30d": row["delta_30d"],
                        "momentum_score": float(row["momentum_score"]),
                    }
                    for row in rows
                ]
                
                return {
                    "category": category,
                    "captured_on": today.isoformat(),
                    "items": items,
                }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/insights/monthly")
async def get_monthly_insights(
    year: int = Query(..., description="Year (e.g., 2024)"),
    month: int = Query(..., description="Month (1-12, e.g., 10 for October)"),
    category: str | None = Query(None, description="Filter by category"),
    country: str | None = Query(None, description="Filter by country"),
    limit: int = Query(50, description="Limit results"),
):
    """Get monthly insights for top podcasts in a specific month."""
    from psycopg.rows import dict_row
    from calendar import monthrange
    
    try:
        # Validate month
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
        
        # Calculate date range for the month
        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                # Get top podcasts by average rank for the month
                query = """
                    SELECT 
                        p.id,
                        p.title,
                        p.publisher,
                        p.category,
                        p.country,
                        AVG(m.rank)::INTEGER as avg_rank,
                        MIN(m.rank)::INTEGER as best_rank,
                        MAX(m.rank)::INTEGER as worst_rank,
                        AVG(m.delta_7d)::INTEGER as avg_delta_7d,
                        AVG(m.delta_30d)::INTEGER as avg_delta_30d,
                        AVG(m.momentum_score) as avg_momentum,
                        MAX(m.momentum_score) as peak_momentum,
                        COUNT(m.captured_on) as days_tracked
                    FROM metrics_daily m
                    JOIN podcasts p ON p.id = m.podcast_id
                    WHERE m.captured_on >= %s AND m.captured_on <= %s
                """
                params: list[Any] = [start_date, end_date]
                
                if category:
                    query += " AND p.category = %s"
                    params.append(category)
                
                if country:
                    query += " AND p.country = %s"
                    params.append(country.lower())
                
                query += """
                    GROUP BY p.id, p.title, p.publisher, p.category, p.country
                    HAVING COUNT(m.captured_on) >= 5  -- At least 5 days of data
                    ORDER BY avg_rank ASC
                    LIMIT %s
                """
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "category": row["category"],
                        "country": row["country"],
                        "avg_rank": row["avg_rank"],
                        "best_rank": row["best_rank"],
                        "worst_rank": row["worst_rank"],
                        "avg_delta_7d": row["avg_delta_7d"],
                        "avg_delta_30d": row["avg_delta_30d"],
                        "avg_momentum": float(row["avg_momentum"]) if row["avg_momentum"] else None,
                        "peak_momentum": float(row["peak_momentum"]) if row["peak_momentum"] else None,
                        "days_tracked": row["days_tracked"],
                    }
                    for row in rows
                ]
                
                # Get additional insights
                cursor.execute(
                    """
                    SELECT 
                        p.id,
                        p.title,
                        p.publisher,
                        MAX(m.delta_30d) as max_delta_30d,
                        MAX(m.momentum_score) as max_momentum
                    FROM metrics_daily m
                    JOIN podcasts p ON p.id = m.podcast_id
                    WHERE m.captured_on >= %s AND m.captured_on <= %s
                    GROUP BY p.id, p.title, p.publisher
                    ORDER BY MAX(m.delta_30d) DESC
                    LIMIT 10
                    """,
                    (start_date, end_date),
                )
                biggest_gainers = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "max_delta_30d": row["max_delta_30d"],
                    }
                    for row in cursor.fetchall()
                ]
                
                return {
                    "year": year,
                    "month": month,
                    "month_name": start_date.strftime("%B"),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "top_podcasts": items,
                    "biggest_gainers": biggest_gainers,
                }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/insights/weekly")
async def get_weekly_insights(
    year: int = Query(..., description="Year (e.g., 2024)"),
    week: int = Query(..., description="Week number (1-53)"),
    category: str | None = Query(None, description="Filter by category"),
    country: str | None = Query(None, description="Filter by country"),
    limit: int = Query(50, description="Limit results"),
):
    """Get weekly insights for top podcasts in a specific week."""
    from psycopg.rows import dict_row
    from datetime import datetime, timedelta
    
    try:
        # Validate week
        if week < 1 or week > 53:
            raise HTTPException(status_code=400, detail="Week must be between 1 and 53")
        
        # Calculate date range for the week (ISO week)
        # Get the first day of the year
        jan1 = date(year, 1, 1)
        # Get the Monday of the week containing Jan 1
        days_offset = (jan1.weekday() - 0) % 7  # 0 = Monday
        first_monday = jan1 - timedelta(days=days_offset)
        
        # Calculate the start date of the requested week
        week_start = first_monday + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6)
        
        # Ensure we don't go beyond the year
        if week_start.year != year:
            raise HTTPException(status_code=400, detail=f"Week {week} doesn't exist in year {year}")
        
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                # Get top podcasts by average rank for the week
                query = """
                    SELECT 
                        p.id,
                        p.title,
                        p.publisher,
                        p.category,
                        p.country,
                        AVG(m.rank)::INTEGER as avg_rank,
                        MIN(m.rank)::INTEGER as best_rank,
                        MAX(m.rank)::INTEGER as worst_rank,
                        AVG(m.delta_7d)::INTEGER as avg_delta_7d,
                        AVG(m.delta_30d)::INTEGER as avg_delta_30d,
                        AVG(m.momentum_score) as avg_momentum,
                        MAX(m.momentum_score) as peak_momentum,
                        COUNT(m.captured_on) as days_tracked
                    FROM metrics_daily m
                    JOIN podcasts p ON p.id = m.podcast_id
                    WHERE m.captured_on >= %s AND m.captured_on <= %s
                """
                params: list[Any] = [week_start, week_end]
                
                if category:
                    query += " AND p.category = %s"
                    params.append(category)
                
                if country:
                    query += " AND p.country = %s"
                    params.append(country.lower())
                
                query += """
                    GROUP BY p.id, p.title, p.publisher, p.category, p.country
                    HAVING COUNT(m.captured_on) >= 3  -- At least 3 days of data
                    ORDER BY avg_rank ASC
                    LIMIT %s
                """
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "category": row["category"],
                        "country": row["country"],
                        "avg_rank": row["avg_rank"],
                        "best_rank": row["best_rank"],
                        "worst_rank": row["worst_rank"],
                        "avg_delta_7d": row["avg_delta_7d"],
                        "avg_delta_30d": row["avg_delta_30d"],
                        "avg_momentum": float(row["avg_momentum"]) if row["avg_momentum"] else None,
                        "peak_momentum": float(row["peak_momentum"]) if row["peak_momentum"] else None,
                        "days_tracked": row["days_tracked"],
                    }
                    for row in rows
                ]
                
                # Get biggest gainers for the week
                cursor.execute(
                    """
                    SELECT 
                        p.id,
                        p.title,
                        p.publisher,
                        MAX(m.delta_7d) as max_delta_7d,
                        MAX(m.momentum_score) as max_momentum
                    FROM metrics_daily m
                    JOIN podcasts p ON p.id = m.podcast_id
                    WHERE m.captured_on >= %s AND m.captured_on <= %s
                    GROUP BY p.id, p.title, p.publisher
                    ORDER BY MAX(m.delta_7d) DESC
                    LIMIT 10
                    """,
                    (week_start, week_end),
                )
                biggest_gainers = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "max_delta_7d": row["max_delta_7d"],
                    }
                    for row in cursor.fetchall()
                ]
                
                return {
                    "year": year,
                    "week": week,
                    "start_date": week_start.isoformat(),
                    "end_date": week_end.isoformat(),
                    "top_podcasts": items,
                    "biggest_gainers": biggest_gainers,
                }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/most-watched")
async def get_most_watched(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    category: str | None = Query(None, description="Filter by category"),
    country: str | None = Query(None, description="Filter by country"),
    limit: int = Query(50, description="Limit results"),
    sort_by: str = Query("listen_time", description="Sort by: listen_time, listeners, engagement_score, new_episodes"),
):
    """Get most watched podcasts for a specific time period based on listen time metrics."""
    from psycopg.rows import dict_row
    
    try:
        # Validate sort_by
        valid_sorts = ["listen_time", "listeners", "engagement_score", "new_episodes"]
        if sort_by not in valid_sorts:
            raise HTTPException(status_code=400, detail=f"sort_by must be one of: {', '.join(valid_sorts)}")
        
        # Map sort_by to column
        sort_column_map = {
            "listen_time": "plm.total_listen_time_seconds",
            "listeners": "plm.total_unique_listeners",
            "engagement_score": "plm.engagement_score",
            "new_episodes": "plm.new_episodes_count",
        }
        sort_column = sort_column_map[sort_by]
        
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                query = """
                    SELECT 
                        p.id,
                        p.title,
                        p.publisher,
                        p.category,
                        p.country,
                        SUM(plm.total_listen_time_seconds) as total_listen_time_seconds,
                        SUM(plm.total_unique_listeners) as total_unique_listeners,
                        AVG(plm.average_completion_rate) as avg_completion_rate,
                        SUM(plm.new_episodes_count) as total_new_episodes,
                        SUM(plm.active_episodes_count) as total_active_episodes,
                        AVG(plm.engagement_score) as avg_engagement_score,
                        COUNT(DISTINCT plm.captured_on) as days_tracked
                    FROM podcast_listen_metrics_daily plm
                    JOIN podcasts p ON p.id = plm.podcast_id
                    WHERE plm.captured_on >= %s AND plm.captured_on <= %s
                """
                params: list[Any] = [start_date, end_date]
                
                if category:
                    query += " AND p.category = %s"
                    params.append(category)
                
                if country:
                    query += " AND p.country = %s"
                    params.append(country.lower())
                
                # Map sort_by to aggregate function
                sort_aggregate_map = {
                    "listen_time": "SUM(plm.total_listen_time_seconds)",
                    "listeners": "SUM(plm.total_unique_listeners)",
                    "engagement_score": "AVG(plm.engagement_score)",
                    "new_episodes": "SUM(plm.new_episodes_count)",
                }
                sort_aggregate = sort_aggregate_map[sort_by]
                
                query += f"""
                    GROUP BY p.id, p.title, p.publisher, p.category, p.country
                    HAVING COUNT(DISTINCT plm.captured_on) >= 3  -- At least 3 days of data
                    ORDER BY {sort_aggregate} DESC
                    LIMIT %s
                """
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "category": row["category"],
                        "country": row["country"],
                        "total_listen_time_seconds": int(row["total_listen_time_seconds"]) if row["total_listen_time_seconds"] else 0,
                        "total_listen_time_hours": round(int(row["total_listen_time_seconds"]) / 3600, 2) if row["total_listen_time_seconds"] else 0,
                        "total_unique_listeners": int(row["total_unique_listeners"]) if row["total_unique_listeners"] else 0,
                        "avg_completion_rate": float(row["avg_completion_rate"]) if row["avg_completion_rate"] else None,
                        "total_new_episodes": int(row["total_new_episodes"]) if row["total_new_episodes"] else 0,
                        "total_active_episodes": int(row["total_active_episodes"]) if row["total_active_episodes"] else 0,
                        "avg_engagement_score": float(row["avg_engagement_score"]) if row["avg_engagement_score"] else None,
                        "days_tracked": row["days_tracked"],
                    }
                    for row in rows
                ]
                
                return {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "sort_by": sort_by,
                    "category": category,
                    "country": country,
                    "items": items,
                }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/podcast/{podcast_id}")
async def get_podcast(podcast_id: str):
    """Get podcast details and historical rank data."""
    from psycopg.rows import dict_row
    
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT id, title, publisher, category, rss_url, country, created_at
                    FROM podcasts
                    WHERE id = %s
                    """,
                    (podcast_id,),
                )
                podcast = cursor.fetchone()
                
                if not podcast:
                    raise HTTPException(status_code=404, detail="Podcast not found")
                
                cutoff = date.today() - timedelta(days=90)
                cursor.execute(
                    """
                    SELECT captured_on, rank, delta_7d, delta_30d, momentum_score
                    FROM metrics_daily
                    WHERE podcast_id = %s AND captured_on >= %s
                    ORDER BY captured_on ASC
                    """,
                    (podcast_id, cutoff),
                )
                history_rows = cursor.fetchall()
                
                history = [
                    {
                        "date": row["captured_on"].isoformat(),
                        "rank": row["rank"],
                        "delta_7d": row["delta_7d"],
                        "delta_30d": row["delta_30d"],
                        "momentum_score": float(row["momentum_score"]) if row["momentum_score"] is not None else None,
                    }
                    for row in history_rows
                ]
                
                return {
                    "id": podcast["id"],
                    "title": podcast["title"],
                    "publisher": podcast["publisher"],
                    "category": podcast["category"],
                    "rss_url": podcast["rss_url"],
                    "country": podcast["country"],
                    "created_at": podcast["created_at"].isoformat() if podcast["created_at"] else None,
                    "history": history,
                }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare")
async def compare_podcasts(
    id1: str = Query(..., description="First podcast ID"),
    id2: str = Query(..., description="Second podcast ID"),
):
    """Compare two podcasts side-by-side with historical data."""
    from psycopg.rows import dict_row
    
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT id, title, publisher, category
                    FROM podcasts
                    WHERE id IN (%s, %s)
                    """,
                    (id1, id2),
                )
                podcasts = {row["id"]: row for row in cursor.fetchall()}
                
                if id1 not in podcasts:
                    raise HTTPException(status_code=404, detail=f"Podcast {id1} not found")
                if id2 not in podcasts:
                    raise HTTPException(status_code=404, detail=f"Podcast {id2} not found")
                
                cutoff = date.today() - timedelta(days=90)
                cursor.execute(
                    """
                    SELECT podcast_id, captured_on, rank, delta_7d, delta_30d, momentum_score
                    FROM metrics_daily
                    WHERE podcast_id IN (%s, %s) AND captured_on >= %s
                    ORDER BY captured_on ASC, podcast_id
                    """,
                    (id1, id2, cutoff),
                )
                rows = cursor.fetchall()
                
                series1: list[dict[str, Any]] = []
                series2: list[dict[str, Any]] = []
                
                for row in rows:
                    point = {
                        "date": row["captured_on"].isoformat(),
                        "rank": row["rank"],
                        "delta_7d": row["delta_7d"],
                        "delta_30d": row["delta_30d"],
                        "momentum_score": float(row["momentum_score"]) if row["momentum_score"] is not None else None,
                    }
                    if row["podcast_id"] == id1:
                        series1.append(point)
                    else:
                        series2.append(point)
                
                return {
                    "id1": id1,
                    "id2": id2,
                    "podcast1": {
                        "id": podcasts[id1]["id"],
                        "title": podcasts[id1]["title"],
                        "publisher": podcasts[id1]["publisher"],
                        "category": podcasts[id1]["category"],
                    },
                    "podcast2": {
                        "id": podcasts[id2]["id"],
                        "title": podcasts[id2]["title"],
                        "publisher": podcasts[id2]["publisher"],
                        "category": podcasts[id2]["category"],
                    },
                    "series": [
                        {"podcast_id": id1, "data": series1},
                        {"podcast_id": id2, "data": series2},
                    ],
                }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ========== AUTHENTICATED ENDPOINTS ==========

@app.get("/api/user/me")
async def get_user_profile(user: dict = Depends(require_auth)):
    """Get current user profile."""
    from psycopg.rows import dict_row
    
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, email, subscription_tier, subscription_status, 
                       subscription_expires_at, api_quota_monthly, api_calls_used, api_reset_date
                FROM users
                WHERE id = %s
                """,
                (user["id"],),
            )
            user_data = cursor.fetchone()
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "id": str(user_data["id"]),
                "email": user_data["email"],
                "subscription_tier": user_data["subscription_tier"],
                "subscription_status": user_data["subscription_status"],
                "subscription_expires_at": user_data["subscription_expires_at"].isoformat() if user_data["subscription_expires_at"] else None,
                "api_quota": {
                    "monthly": user_data["api_quota_monthly"],
                    "used": user_data["api_calls_used"],
                    "remaining": user_data["api_quota_monthly"] - user_data["api_calls_used"],
                },
            }


@app.get("/api/user/watchlist")
async def get_watchlist(user: dict = Depends(require_auth)):
    """Get user's watchlist."""
    from psycopg.rows import dict_row
    
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT p.id, p.title, p.publisher, p.category, p.country,
                       m.rank, m.delta_7d, m.delta_30d, m.momentum_score
                FROM user_watchlists w
                JOIN podcasts p ON p.id = w.podcast_id
                LEFT JOIN metrics_daily m ON m.podcast_id = p.id AND m.captured_on = CURRENT_DATE
                WHERE w.user_id = %s
                ORDER BY w.created_at DESC
                """,
                (user["id"],),
            )
            rows = cursor.fetchall()
            
            return {
                "items": [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "publisher": row["publisher"],
                        "category": row["category"],
                        "country": row["country"],
                        "rank": row["rank"],
                        "delta_7d": row["delta_7d"],
                        "delta_30d": row["delta_30d"],
                        "momentum_score": float(row["momentum_score"]) if row["momentum_score"] is not None else None,
                    }
                    for row in rows
                ],
            }


@app.post("/api/user/watchlist/{podcast_id}")
async def add_to_watchlist(podcast_id: str, user: dict = Depends(require_auth)):
    """Add podcast to user's watchlist."""
    from psycopg.rows import dict_row
    
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Verify podcast exists
            cursor.execute("SELECT id FROM podcasts WHERE id = %s", (podcast_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Podcast not found")
            
            # Add to watchlist
            try:
                cursor.execute(
                    """
                    INSERT INTO user_watchlists (user_id, podcast_id)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id, podcast_id) DO NOTHING
                    """,
                    (user["id"], podcast_id),
                )
                conn.commit()
                return {"status": "added", "podcast_id": podcast_id}
            except Exception as e:
                conn.rollback()
                raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/user/watchlist/{podcast_id}")
async def remove_from_watchlist(podcast_id: str, user: dict = Depends(require_auth)):
    """Remove podcast from user's watchlist."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_watchlists WHERE user_id = %s AND podcast_id = %s",
                (user["id"], podcast_id),
            )
            conn.commit()
            return {"status": "removed", "podcast_id": podcast_id}


@app.get("/api/user/api-key")
async def get_api_key(user: dict = Depends(require_auth)):
    """Get or generate API key for user."""
    from psycopg.rows import dict_row
    import secrets
    
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT api_key FROM users WHERE id = %s", (user["id"],))
            user_data = cursor.fetchone()
            
            if user_data and user_data["api_key"]:
                return {"api_key": user_data["api_key"]}
            
            # Generate new API key
            api_key = f"pk_{secrets.token_urlsafe(32)}"
            cursor.execute(
                "UPDATE users SET api_key = %s WHERE id = %s",
                (api_key, user["id"]),
            )
            conn.commit()
            return {"api_key": api_key}


@app.post("/api/subscriptions/checkout")
async def create_checkout_session(user: dict = Depends(require_auth), tier: str = Query("pro")):
    """Create Stripe checkout session for subscription."""
    from app.subscriptions import create_checkout_session
    
    try:
        session = create_checkout_session(UUID(user["id"]), tier)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/subscriptions/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    from app.subscriptions import handle_webhook, update_user_subscription
    from app.db import get_connection
    from fastapi.responses import JSONResponse
    import json
    
    event = None
    event_type = None
    
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        logger.info(f"Received webhook request, signature: {signature[:20] if signature else 'None'}...")
        
        # Handle webhook signature verification
        if not signature:
            logger.warning("Missing stripe-signature header")
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        logger.info(f"Processing webhook with signature: {signature[:20]}...")
        try:
            event = handle_webhook(payload, signature)
            event_type = event.get("type", "unknown")
            logger.info(f"Webhook event type: {event_type}")
        except ValueError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {str(e)}")
        
        # Checkout completed - new subscription created
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            # Only process if client_reference_id exists (real checkout, not test)
            if session.get("client_reference_id"):
                try:
                    user_id = UUID(session["client_reference_id"])
                    tier = session.get("metadata", {}).get("tier", "pro")
                    subscription_id = session.get("subscription")
                    if subscription_id:
                        update_user_subscription(user_id, subscription_id, tier, "active")
                except (ValueError, KeyError) as e:
                    # Skip if user_id is invalid or missing
                    pass
        
        # Subscription created/updated
        elif event_type == "customer.subscription.created":
            subscription = event["data"]["object"]
            # Get user from customer metadata or subscription metadata
            # For now, we'll handle this via checkout.session.completed
            pass
        
        # Subscription updated (plan change, renewal, etc.)
        elif event_type == "customer.subscription.updated":
            subscription = event["data"]["object"]
            subscription_id = subscription.get("id")
            # Find user by subscription_id stored in database
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get tier from subscription metadata or price
                    tier = subscription.get("metadata", {}).get("tier", "pro")
                    status = subscription.get("status", "active")
                    
                    # Update user subscription
                    from datetime import datetime
                    expires_at = datetime.fromtimestamp(subscription.get("current_period_end", 0))
                    quota = {"free": 1000, "pro": 10000, "enterprise": 100000}.get(tier, 1000)
                    
                    cursor.execute(
                        """
                        UPDATE users
                        SET subscription_tier = %s,
                            subscription_status = %s,
                            subscription_expires_at = %s,
                            api_quota_monthly = %s,
                            updated_at = now()
                        WHERE subscription_id = %s
                        """,
                        (tier, status, expires_at, quota, subscription_id),
                    )
                    conn.commit()
        
        # Subscription deleted/cancelled
        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            subscription_id = subscription.get("id")
            # Downgrade user to free tier
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE users
                        SET subscription_tier = 'free',
                            subscription_status = 'cancelled',
                            subscription_id = NULL,
                            subscription_expires_at = NULL,
                            api_quota_monthly = 1000,
                            updated_at = now()
                        WHERE subscription_id = %s
                        """,
                        (subscription_id,),
                    )
                    conn.commit()
        
        # Payment succeeded - subscription renewed
        elif event_type == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            if subscription_id:
                # Subscription payment succeeded, ensure it's active
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE users
                            SET subscription_status = 'active',
                                updated_at = now()
                            WHERE subscription_id = %s
                            """,
                            (subscription_id,),
                        )
                        conn.commit()
        
        # Payment failed - subscription at risk
        elif event_type == "invoice.payment_failed":
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            if subscription_id:
                # Mark subscription as past_due
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE users
                            SET subscription_status = 'past_due',
                                updated_at = now()
                            WHERE subscription_id = %s
                            """,
                            (subscription_id,),
                        )
                        conn.commit()
        
        # Customer updated
        elif event_type == "customer.updated":
            customer = event["data"]["object"]
            # Handle customer updates if needed
            pass
        
        # Return 200 OK for all events (even if we don't handle them)
        # This prevents Stripe from retrying
        return JSONResponse(content={"status": "success", "event": event_type}, status_code=200)
    except ValueError as e:
        # Invalid webhook signature or payload
        logger.error(f"ValueError in webhook handler: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for missing signature)
        raise
    except Exception as e:
        # Log other errors but still return 200 to prevent retries
        logger.error(f"Exception in webhook handler: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return 200 OK even on error to prevent Stripe retries
        # Log the error for debugging
        try:
            event_type_str = event_type or (event.get("type") if event else "unknown")
        except:
            event_type_str = "unknown"
        
        return JSONResponse(
            content={"status": "error", "event": event_type_str, "error": str(e)},
            status_code=200
        )


# ========== ADMIN ENDPOINTS ==========

@app.get("/api/admin/stats")
async def get_admin_stats(user: dict = Depends(require_pro)):
    """Get admin statistics (Pro/Enterprise only)."""
    from psycopg.rows import dict_row
    
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Total podcasts
            cursor.execute("SELECT COUNT(*) as count FROM podcasts")
            total_podcasts = cursor.fetchone()["count"]
            
            # Total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()["count"]
            
            # Active subscriptions
            cursor.execute(
                "SELECT COUNT(*) as count FROM users WHERE subscription_tier IN ('pro', 'enterprise') AND subscription_status = 'active'"
            )
            active_subscriptions = cursor.fetchone()["count"]
            
            # API usage today
            cursor.execute(
                "SELECT COUNT(*) as count FROM api_usage WHERE called_at >= CURRENT_DATE"
            )
            api_calls_today = cursor.fetchone()["count"]
            
            return {
                "total_podcasts": total_podcasts,
                "total_users": total_users,
                "active_subscriptions": active_subscriptions,
                "api_calls_today": api_calls_today,
            }
