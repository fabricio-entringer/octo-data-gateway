import csv
import io
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional

from app.database.user_usage import user_usage as usage_table
from app.database import user_database
from .stats_schema import (
    DashboardStats,
    EndpointStats,
    TimeSeriesPoint,
    UserStats,
)


class StatsService:

    def get_dashboard_stats(self) -> DashboardStats:
        now = datetime.now()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_7d = now - timedelta(days=7)
        cutoff_30d = now - timedelta(days=30)

        all_records = usage_table.all()
        all_users = user_database.get_all_users()

        total_users = len(all_users)
        active_keys = sum(
            1 for u in all_users
            if u.api_key_expires_at is None or u.api_key_expires_at > now
        )
        expired_keys = total_users - active_keys

        records_24h = []
        records_7d = []
        records_30d = []

        for r in all_records:
            ts = _parse_timestamp(r.get("timestamp"))
            if ts is None:
                continue
            if ts >= cutoff_30d:
                records_30d.append(r)
            if ts >= cutoff_7d:
                records_7d.append(r)
            if ts >= cutoff_24h:
                records_24h.append(r)

        success_24h = sum(1 for r in records_24h if r.get("is_success", False))
        total_24h = len(records_24h)
        success_rate = (success_24h / total_24h * 100) if total_24h > 0 else 0.0

        response_times = [r.get("response_time_ms", 0) for r in records_24h if r.get("response_time_ms")]
        avg_rt = sum(response_times) / len(response_times) if response_times else 0.0

        endpoint_counter: dict[str, dict] = defaultdict(lambda: {
            "count": 0, "success": 0, "fail": 0, "rt_sum": 0.0,
        })
        for r in records_30d:
            ep = r.get("endpoint", "unknown")
            endpoint_counter[ep]["count"] += 1
            if r.get("is_success", False):
                endpoint_counter[ep]["success"] += 1
            else:
                endpoint_counter[ep]["fail"] += 1
            endpoint_counter[ep]["rt_sum"] += r.get("response_time_ms", 0)

        requests_per_endpoint = [
            EndpointStats(
                endpoint=ep,
                request_count=d["count"],
                success_count=d["success"],
                fail_count=d["fail"],
                avg_response_time_ms=round(d["rt_sum"] / d["count"], 2) if d["count"] else 0,
            )
            for ep, d in sorted(endpoint_counter.items(), key=lambda x: -x[1]["count"])
        ]

        user_map = {u.user_id: u.name for u in all_users}
        user_counter: dict[str, dict] = defaultdict(lambda: {"count": 0, "last": None})
        for r in records_30d:
            uid = r.get("user_id", "")
            user_counter[uid]["count"] += 1
            ts = r.get("timestamp")
            if ts and (user_counter[uid]["last"] is None or str(ts) > str(user_counter[uid]["last"])):
                user_counter[uid]["last"] = ts

        top_users = [
            UserStats(
                user_id=uid,
                user_name=user_map.get(uid, uid),
                request_count=d["count"],
                last_active=str(d["last"]) if d["last"] else None,
            )
            for uid, d in sorted(user_counter.items(), key=lambda x: -x[1]["count"])[:10]
        ]

        day_buckets: Counter = Counter()
        for r in records_7d:
            ts = _parse_timestamp(r.get("timestamp"))
            if ts:
                day_buckets[ts.strftime("%Y-%m-%d")] += 1
        base_date = now - timedelta(days=6)
        requests_over_time = []
        for i in range(7):
            day_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            requests_over_time.append(TimeSeriesPoint(timestamp=day_str, count=day_buckets.get(day_str, 0)))

        status_dist: Counter = Counter()
        for r in records_30d:
            code = str(r.get("status_code", "unknown"))
            status_dist[code] += 1

        return DashboardStats(
            total_users=total_users,
            active_api_keys=active_keys,
            expired_api_keys=expired_keys,
            total_requests_24h=total_24h,
            total_requests_7d=len(records_7d),
            total_requests_30d=len(records_30d),
            success_rate_24h=round(success_rate, 1),
            avg_response_time_ms=round(avg_rt, 2),
            requests_per_endpoint=requests_per_endpoint,
            top_users=top_users,
            requests_over_time=requests_over_time,
            status_code_distribution=dict(status_dist),
        )

    def get_usage_logs(
        self,
        page: int = 1,
        per_page: int = 50,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        records = usage_table.all()
        filtered = _apply_filters(records, user_id, endpoint, status_code, date_from, date_to)
        filtered.sort(key=lambda r: str(r.get("timestamp", "")), reverse=True)
        total = len(filtered)
        start = (page - 1) * per_page
        return filtered[start:start + per_page], total

    def export_logs_csv(
        self,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> str:
        records = usage_table.all()
        filtered = _apply_filters(records, user_id, endpoint, status_code, date_from, date_to)
        filtered.sort(key=lambda r: str(r.get("timestamp", "")), reverse=True)

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["timestamp", "user_id", "request_id", "endpoint", "method", "status_code", "response_time_ms", "is_success"])
        for r in filtered:
            writer.writerow([
                r.get("timestamp", ""),
                r.get("user_id", ""),
                r.get("request_id", ""),
                r.get("endpoint", ""),
                r.get("method", ""),
                r.get("status_code", ""),
                r.get("response_time_ms", ""),
                r.get("is_success", ""),
            ])
        return buf.getvalue()


def _parse_timestamp(ts) -> Optional[datetime]:
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    try:
        return datetime.fromisoformat(str(ts))
    except (ValueError, TypeError):
        return None


def _apply_filters(records, user_id, endpoint, status_code, date_from, date_to):
    filtered = list(records)
    if user_id:
        filtered = [r for r in filtered if r.get("user_id") == user_id]
    if endpoint:
        filtered = [r for r in filtered if endpoint in r.get("endpoint", "")]
    if status_code is not None:
        filtered = [r for r in filtered if r.get("status_code") == status_code]
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            filtered = [r for r in filtered if _parse_timestamp(r.get("timestamp")) and _parse_timestamp(r.get("timestamp")) >= dt_from]
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            filtered = [r for r in filtered if _parse_timestamp(r.get("timestamp")) and _parse_timestamp(r.get("timestamp")) <= dt_to]
        except ValueError:
            pass
    return filtered
