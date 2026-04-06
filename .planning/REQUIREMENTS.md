# Requirements

## ADMIN-01: Backend Foundation
- In-memory cache manager with configurable TTL per endpoint
- Cache entries expire correctly; TTL changes take effect without restart
- Jinja2 template rendering + static file serving from FastAPI
- Base HTML layout with sidebar navigation, Tailwind CSS, responsive design

## ADMIN-02: API Usage Statistics
- Aggregate user_usage data (total requests, success rates, avg response time)
- Breakdown by endpoint, by user, by time period (24h/7d/30d)
- Statistics API endpoints accessible to MASTER/ADMIN scopes
- Dashboard page with Chart.js visualizations (pie, bar, line charts)
- Stats cards: total users, active keys, expired keys, total requests, success rate

## ADMIN-03: User Management
- List all users in a table with name, email, scopes, key status, dates
- Create new user via modal form (name, email, description, scopes, key expiry)
- Edit existing user (name, email, description, scopes)
- Delete user with confirmation dialog
- Renew API key with expiration picker
- Copy API key to clipboard
- Color-coded scope badges

## ADMIN-04: Access Rights
- Matrix view: users × scopes with toggle checkboxes
- Bulk scope assignment
- Quick scope templates (Full Access, Read-only Bitcoin, All Data)

## ADMIN-05: Cache Management
- Per-endpoint TTL configuration UI
- Live reload: changes take effect immediately (no restart)
- View current cache entries and remaining TTL
- Flush cache button (per-endpoint or all)

## ADMIN-06: Request Logs
- Paginated table from user_usage data
- Filters: by user, endpoint, status code, date range
- CSV export functionality

## ADMIN-07: Settings & System Info
- Plugin status (active/failed Bitcoin processors)
- App version, uptime, TinyDB database size
- System health overview
