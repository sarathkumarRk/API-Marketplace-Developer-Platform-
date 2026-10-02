from sqlalchemy import text


MOST_USED_APIS = text("""
SELECT
    a.id,
    a.name,
    a.slug,
    COUNT(arl.id) AS total_requests
FROM apis a
JOIN api_request_logs arl
    ON a.id = arl.api_id
GROUP BY
    a.id,
    a.name,
    a.slug
ORDER BY total_requests DESC;
""")


MOST_USED_ENDPOINTS = text("""
SELECT
    ae.id,
    ae.method,
    ae.path,
    COUNT(arl.id) AS total_requests
FROM api_endpoints ae
JOIN api_request_logs arl
    ON ae.id = arl.endpoint_id
GROUP BY
    ae.id,
    ae.method,
    ae.path
ORDER BY total_requests DESC;
""")


TOP_DEVELOPERS_BY_USAGE = text("""
SELECT
    u.id,
    u.name,
    u.email,
    COUNT(arl.id) AS total_requests
FROM users u
JOIN api_request_logs arl
    ON u.id = arl.developer_id
WHERE u.role = 'developer'
GROUP BY
    u.id,
    u.name,
    u.email
ORDER BY total_requests DESC;
""")


API_REVENUE_BY_MONTH = text("""
SELECT
    DATE_FORMAT(s.started_at, '%Y-%m') AS revenue_month,
    SUM(ap.price) AS total_revenue
FROM subscriptions s
JOIN api_plans ap
    ON s.plan_id = ap.id
WHERE s.status IN ('active', 'cancelled')
GROUP BY
    DATE_FORMAT(s.started_at, '%Y-%m')
ORDER BY revenue_month;
""")


PROVIDER_WISE_REVENUE = text("""
SELECT
    u.id AS provider_id,
    u.name AS provider_name,
    SUM(ap.price) AS total_revenue
FROM users u
JOIN organizations o
    ON u.id = o.owner_id
JOIN apis a
    ON o.id = a.organization_id
JOIN subscriptions s
    ON a.id = s.api_id
JOIN api_plans ap
    ON s.plan_id = ap.id
WHERE u.role = 'api_provider'
  AND s.status IN ('active', 'cancelled')
GROUP BY
    u.id,
    u.name
ORDER BY total_revenue DESC;
""")


AVERAGE_API_RESPONSE_TIME = text("""
SELECT
    a.id,
    a.name,
    ROUND(AVG(arl.response_time_ms), 2) AS average_response_time_ms
FROM apis a
JOIN api_request_logs arl
    ON a.id = arl.api_id
GROUP BY
    a.id,
    a.name
ORDER BY average_response_time_ms DESC;
""")


APIS_WITH_HIGHEST_ERROR_RATE = text("""
SELECT
    a.id,
    a.name,
    COUNT(arl.id) AS total_requests,
    SUM(
        CASE
            WHEN arl.status_code >= 400 THEN 1
            ELSE 0
        END
    ) AS failed_requests,
    ROUND(
        (
            SUM(
                CASE
                    WHEN arl.status_code >= 400 THEN 1
                    ELSE 0
                END
            ) / COUNT(arl.id)
        ) * 100,
        2
    ) AS error_rate
FROM apis a
JOIN api_request_logs arl
    ON a.id = arl.api_id
GROUP BY
    a.id,
    a.name
HAVING COUNT(arl.id) > 0
ORDER BY error_rate DESC;
""")


DEVELOPERS_EXCEEDING_80_PERCENT_QUOTA = text("""
SELECT
    u.id,
    u.name,
    u.email,
    s.api_id,
    ap.requests_per_month AS monthly_quota,
    COUNT(arl.id) AS current_usage,
    ROUND(
        (COUNT(arl.id) / ap.requests_per_month) * 100,
        2
    ) AS usage_percentage
FROM users u
JOIN subscriptions s
    ON u.id = s.developer_id
JOIN api_plans ap
    ON s.plan_id = ap.id
LEFT JOIN api_request_logs arl
    ON arl.developer_id = u.id
    AND arl.api_id = s.api_id
    AND arl.request_timestamp >= s.started_at
WHERE u.role = 'developer'
  AND s.status = 'active'
  AND ap.requests_per_month > 0
GROUP BY
    u.id,
    u.name,
    u.email,
    s.api_id,
    ap.requests_per_month
HAVING
    COUNT(arl.id) >= ap.requests_per_month * 0.8
ORDER BY usage_percentage DESC;
""")


MOST_POPULAR_SUBSCRIPTION_PLANS = text("""
SELECT
    ap.id,
    ap.name,
    ap.api_id,
    COUNT(s.id) AS subscription_count
FROM api_plans ap
JOIN subscriptions s
    ON ap.id = s.plan_id
GROUP BY
    ap.id,
    ap.name,
    ap.api_id
ORDER BY subscription_count DESC;
""")


CANCELLED_SUBSCRIPTIONS_PER_MONTH = text("""
SELECT
    DATE_FORMAT(s.expires_at, '%Y-%m') AS cancellation_month,
    COUNT(s.id) AS cancelled_subscriptions
FROM subscriptions s
WHERE s.status = 'cancelled'
  AND s.expires_at IS NOT NULL
GROUP BY
    DATE_FORMAT(s.expires_at, '%Y-%m')
ORDER BY cancellation_month;
""")


API_USAGE_BY_VERSION = text("""
SELECT
    av.id,
    av.version,
    av.api_id,
    COUNT(arl.id) AS total_requests
FROM api_versions av
JOIN api_request_logs arl
    ON av.id = arl.api_version_id
GROUP BY
    av.id,
    av.version,
    av.api_id
ORDER BY total_requests DESC;
""")


DEPRECATED_VERSIONS_RECEIVING_REQUESTS = text("""
SELECT
    av.id,
    av.version,
    av.api_id,
    COUNT(arl.id) AS total_requests
FROM api_versions av
JOIN api_request_logs arl
    ON av.id = arl.api_version_id
WHERE av.status = 'deprecated'
GROUP BY
    av.id,
    av.version,
    av.api_id
HAVING COUNT(arl.id) > 0
ORDER BY total_requests DESC;
""")


FAILED_WEBHOOK_DELIVERIES = text("""
SELECT
    w.id AS webhook_id,
    w.api_id,
    wd.event_id,
    wd.status,
    wd.response_code,
    wd.attempt_count,
    wd.delivered_at
FROM webhooks w
JOIN webhook_deliveries wd
    ON w.id = wd.webhook_id
WHERE wd.status = 'failed'
ORDER BY wd.delivered_at DESC;
""")


DAILY_API_REQUEST_STATISTICS = text("""
SELECT
    DATE(arl.request_timestamp) AS request_date,
    COUNT(arl.id) AS total_requests,
    SUM(
        CASE
            WHEN arl.status_code >= 200
             AND arl.status_code < 400
            THEN 1
            ELSE 0
        END
    ) AS successful_requests,
    SUM(
        CASE
            WHEN arl.status_code >= 400
            THEN 1
            ELSE 0
        END
    ) AS failed_requests,
    ROUND(
        AVG(arl.response_time_ms),
        2
    ) AS average_response_time_ms
FROM api_request_logs arl
GROUP BY
    DATE(arl.request_timestamp)
ORDER BY request_date;
""")


MONTHLY_PLATFORM_REVENUE = text("""
SELECT
    DATE_FORMAT(s.started_at, '%Y-%m') AS revenue_month,
    SUM(
        CASE
            WHEN s.status IN ('active', 'cancelled')
            THEN ap.price
            ELSE 0
        END
    ) AS platform_revenue
FROM subscriptions s
JOIN api_plans ap
    ON s.plan_id = ap.id
GROUP BY
    DATE_FORMAT(s.started_at, '%Y-%m')
ORDER BY revenue_month;
""")


ADVANCED_SQL_QUERIES = {
    "most_used_apis": MOST_USED_APIS,
    "most_used_endpoints": MOST_USED_ENDPOINTS,
    "top_developers_by_usage": TOP_DEVELOPERS_BY_USAGE,
    "api_revenue_by_month": API_REVENUE_BY_MONTH,
    "provider_wise_revenue": PROVIDER_WISE_REVENUE,
    "average_api_response_time": AVERAGE_API_RESPONSE_TIME,
    "apis_with_highest_error_rate": APIS_WITH_HIGHEST_ERROR_RATE,
    "developers_exceeding_80_percent_quota": DEVELOPERS_EXCEEDING_80_PERCENT_QUOTA,
    "most_popular_subscription_plans": MOST_POPULAR_SUBSCRIPTION_PLANS,
    "cancelled_subscriptions_per_month": CANCELLED_SUBSCRIPTIONS_PER_MONTH,
    "api_usage_by_version": API_USAGE_BY_VERSION,
    "deprecated_versions_receiving_requests": DEPRECATED_VERSIONS_RECEIVING_REQUESTS,
    "failed_webhook_deliveries": FAILED_WEBHOOK_DELIVERIES,
    "daily_api_request_statistics": DAILY_API_REQUEST_STATISTICS,
    "monthly_platform_revenue": MONTHLY_PLATFORM_REVENUE,
}