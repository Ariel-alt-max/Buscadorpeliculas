from flask import Flask, render_template, request
import requests

app = Flask(__name__)

BASE_URL = "https://api.themoviedb.org/3"
TRENDING_URL = f"{BASE_URL}/trending/all/day"
SEARCH_URL = f"{BASE_URL}/search/multi"
GENRES_URL = f"{BASE_URL}/genre/movie/list"
TV_GENRES_URL = f"{BASE_URL}/genre/tv/list"

HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwZGY1ZGE1YzA3YzhjYTQzZDc5NzNiNGZmNGJkYzIwNiIsIm5iZiI6MTc2OTgyNTMzMS4xMTEsInN1YiI6IjY5N2Q2NDMzZmZkMTEyZTk0MWVhMGI1OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.il2hG9xMUebfFEkAT4etY9Hej3NUrut_uCf88yr2BHg"
}

def get_genres():
    movie_genres = requests.get(GENRES_URL, headers=HEADERS).json().get("genres", [])
    tv_genres = requests.get(TV_GENRES_URL, headers=HEADERS).json().get("genres", [])
    return movie_genres + tv_genres

@app.route("/")
def index():
    trends = requests.get(TRENDING_URL, headers=HEADERS).json().get("results", [])
    generos = get_genres()
    return render_template("index.html", trends=trends, genres=generos)

@app.route("/search")
def search():
    query = request.args.get("query")
    genero = request.args.get("genre")
    page = request.args.get("page", 1, type=int)

    generos = get_genres()
    if query:
        params = {
            "query": query,
            "page": page,
            "include_adult": False
        }

        response = requests.get(
            SEARCH_URL,
            headers=HEADERS,
            params=params
        ).json()

        results = response.get("results", [])

        if genero:
            results = [
                item for item in results
                if genero in map(str, item.get("genre_ids", []))
            ]

    elif genero:
        params = {
            "with_genres": genero,
            "page": page,
            "sort_by": "popularity.desc"
        }

        response = requests.get(
            f"{BASE_URL}/discover/movie",
            headers=HEADERS,
            params=params
        ).json()

        results = response.get("results", [])

        for r in results:
            r["media_type"] = "movie"
    else:
        results = []
        response = {"page": 1, "total_pages": 1}


    return render_template(
        "resultados.html",
        results=results,
        query=query,
        genre=genero,   
        page=response.get("page", 1),
        total_pages=response.get("total_pages", 1),
        genres=generos
    )



@app.route("/detail/<tipo>/<int:id>")
def detail(tipo, id):

    item = requests.get(
        f"{BASE_URL}/{tipo}/{id}",
        headers=HEADERS
    ).json()

    creditos = requests.get(
        f"{BASE_URL}/{tipo}/{id}/credits",
        headers=HEADERS
    ).json()

    cast = creditos.get("cast", [])[:12]  

    videos = requests.get(
        f"{BASE_URL}/{tipo}/{id}/videos",
        headers=HEADERS
    ).json().get("results", [])

    trailer_key = None
    for v in videos:
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            trailer_key = v["key"]
            break

    generos = get_genres()

    return render_template(
        "detalles.html",
        item=item,
        cast=cast,
        trailer_key=trailer_key,
        genres=generos
    )

if __name__ == "__main__":
    app.run(debug=True)