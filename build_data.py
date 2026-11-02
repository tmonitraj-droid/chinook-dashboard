"""Downloads the Chinook sample database, runs SQL queries, writes data.js for the dashboard."""
import json, os, sqlite3, urllib.request

URL = "https://github.com/lerocha/chinook-database/releases/download/v1.4.5/Chinook_Sqlite.sqlite"
DB = "chinook.db"

if not os.path.exists(DB):
    print("Downloading Chinook database...")
    urllib.request.urlretrieve(URL, DB)

con = sqlite3.connect(DB)

QUERIES = {
    "kpis": """
        SELECT ROUND(SUM(Total), 2) AS revenue,
               COUNT(*) AS orders,
               COUNT(DISTINCT CustomerId) AS customers,
               ROUND(AVG(Total), 2) AS avg_order
        FROM Invoice;""",
    "yearly": """
        SELECT strftime('%Y', InvoiceDate) AS year, ROUND(SUM(Total), 2) AS revenue
        FROM Invoice GROUP BY year ORDER BY year;""",
    "countries": """
        SELECT BillingCountry AS country, ROUND(SUM(Total), 2) AS revenue
        FROM Invoice GROUP BY country ORDER BY revenue DESC LIMIT 10;""",
    "genres": """
        SELECT g.Name AS genre, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue
        FROM InvoiceLine il
        JOIN Track t ON t.TrackId = il.TrackId
        JOIN Genre g ON g.GenreId = t.GenreId
        GROUP BY g.Name ORDER BY revenue DESC LIMIT 8;""",
    "artists": """
        SELECT ar.Name AS artist, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue
        FROM InvoiceLine il
        JOIN Track t ON t.TrackId = il.TrackId
        JOIN Album al ON al.AlbumId = t.AlbumId
        JOIN Artist ar ON ar.ArtistId = al.ArtistId
        GROUP BY ar.Name ORDER BY revenue DESC LIMIT 10;""",
    "customers": """
        SELECT c.FirstName || ' ' || c.LastName AS customer, ROUND(SUM(i.Total), 2) AS revenue
        FROM Invoice i JOIN Customer c ON c.CustomerId = i.CustomerId
        GROUP BY c.CustomerId ORDER BY revenue DESC LIMIT 10;""",
}

data = {}
for name, sql in QUERIES.items():
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    data[name] = rows[0] if name == "kpis" else rows

with open("data.js", "w", encoding="utf-8") as f:
    f.write("const DATA = " + json.dumps(data, indent=1) + ";")
print("Done: data.js created")
