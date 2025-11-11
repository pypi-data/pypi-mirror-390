from bearish.database.crud import BearishDb  # type: ignore

from mysec.models import SecData


def new_entries(bearish_db: BearishDb) -> SecData:
    query = """
            WITH max_periods AS (SELECT company_name, MAX(period) AS max_period \
                                 FROM sec \
                                 GROUP BY company_name),
                 latest_only AS (SELECT s.company_name, s.name, s.value, s.ticker, s.shares \
                                 FROM sec s \
                                          JOIN max_periods mp \
                                               ON mp.company_name = s.company_name \
                                                   AND mp.max_period = s.period \
                                 WHERE s.value IS NOT NULL \
                                   AND NOT EXISTS (SELECT 1 \
                                                   FROM sec s2 \
                                                   WHERE s2.company_name = s.company_name \
                                                     AND s2.name = s.name \
                                                     AND s2.period < mp.max_period))
            SELECT name, \
                   ticker, \
                   COUNT(DISTINCT company_name)     AS occurrences, \
                   GROUP_CONCAT(company_name, ', ') AS companies, \
                   SUM(value)                       AS total_value, \
                   SUM(shares)                      AS total_shares
            FROM latest_only
            GROUP BY name, ticker
            ORDER BY total_value DESC, occurrences DESC; \
            """
    data = bearish_db._read_query(query)
    return SecData(data=data, color="green")


def exited_positions(bearish_db: BearishDb) -> SecData:
    query = """WITH max_periods AS (
  SELECT company_name, MAX(period) AS max_period
  FROM sec
  GROUP BY company_name
),
-- last row BEFORE the company's max period, per (company, name)
prev_latest AS (
  SELECT s.company_name, s.name, s.ticker, s.value, s.shares
  FROM sec s
  JOIN max_periods mp
    ON mp.company_name = s.company_name
  WHERE s.period = (
          SELECT MAX(s2.period)
          FROM sec s2
          WHERE s2.company_name = s.company_name
            AND s2.name        = s.name
            AND s2.period      < mp.max_period
        )
    AND s.value IS NOT NULL
    -- ensure it does NOT exist at the latest period
    AND NOT EXISTS (
          SELECT 1
          FROM sec sl
          WHERE sl.company_name = s.company_name
            AND sl.name         = s.name
            AND sl.period       = mp.max_period
        )
)
SELECT
  name,
  ticker,
  COUNT(DISTINCT company_name)      AS occurrences,
  GROUP_CONCAT(company_name, ', ')  AS companies,
  SUM(value)                        AS total_value,
  SUM(shares)                       AS total_shares
FROM prev_latest
GROUP BY name, ticker
ORDER BY total_value DESC, occurrences DESC;
"""
    data = bearish_db._read_query(query)
    return SecData(data=data, color="red", coefficient=-1)


def _increase_decrease_template(sign: str) -> str:
    query = f""" 
    WITH max_periods AS (
  SELECT company_name, MAX(period) AS max_period
  FROM sec
  GROUP BY company_name
),
prev_latest AS (
  SELECT
      s.company_name,
      s.name,
      s.ticker  AS prev_ticker,
      s.value   AS prev_value,
      s.shares  AS prev_shares
  FROM sec s
  JOIN max_periods mp
    ON mp.company_name = s.company_name
  WHERE s.period = (
          SELECT MAX(s2.period)
          FROM sec s2
          WHERE s2.company_name = s.company_name
            AND s2.name        = s.name
            AND s2.period      < mp.max_period
        )
    AND s.value IS NOT NULL
),
curr_latest AS (
  SELECT
      s.company_name,
      s.name,
      s.ticker,
      s.value,
      s.shares
  FROM sec s
  JOIN max_periods mp
    ON mp.company_name = s.company_name
   AND mp.max_period   = s.period
  WHERE s.value IS NOT NULL
)
SELECT
  c.name,
  c.ticker,
  COUNT(DISTINCT c.company_name)               AS occurrences,
  GROUP_CONCAT( c.company_name, ', ')  AS companies,
  SUM(p.prev_value)                            AS prev_total_value,
  SUM(c.value)                                 AS total_value,
  SUM(c.value - p.prev_value)                  AS total_increase,
  SUM(p.prev_shares)                           AS prev_total_shares,
  SUM(c.shares)                                AS total_shares,
  SUM(c.shares - p.prev_shares)                AS shares_increase
FROM curr_latest c
JOIN prev_latest p
  ON p.company_name = c.company_name
 AND p.name         = c.name            -- ensures presence in both periods
GROUP BY c.name, c.ticker
HAVING SUM(c.value - p.prev_value) {sign} 0   -- keep only positive total increase
ORDER BY total_increase DESC, occurrences DESC;

    """  # noqa: S608
    return query


def total_increase(bearish_db: BearishDb) -> SecData:
    query = _increase_decrease_template(">")
    data = bearish_db._read_query(query)
    return SecData(data=data, color="green")


def total_decrease(bearish_db: BearishDb) -> SecData:
    query = _increase_decrease_template("<")
    data = bearish_db._read_query(query)
    return SecData(data=data, color="red", coefficient=-1)
