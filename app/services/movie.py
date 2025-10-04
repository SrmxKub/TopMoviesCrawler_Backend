import os
import requests
import csv
import re
import json
import random
from typing import List
from pydantic import TypeAdapter
from concurrent.futures import ThreadPoolExecutor
from app.services.header import *
from app.schemas.exceptions import *
from app.schemas.crawler import *
from app.services.export import *


class MovieService:
    def __init__(self):
        
        self.base_url = "https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/"
        self.exporter = ExportService()
        self.session = requests.Session()
        self.header = HeaderService()
        
        self.page1_pattern = {
            "row": re.compile(r"<tr.*?>(.*?)</tr>", re.S),
            "td": re.compile(r"<td.*?>(.*?)</td>", re.S),
            "score": re.compile(r"<span class='score'.*?>.*?(\d{2,3})%.*?</span>", re.S),
            "detail": re.compile(r"<span class='details'.*?>(.*?)</span>", re.S),
            "title": re.compile(r"<a.*?>(.*?)</a>", re.S),
            "link": re.compile(r'<a.*?href=["\'](.*?)["\'].*?>', re.S),
            "year": re.compile(r"(\d{4})"),
        }
        
        self.page2_pattern = {
            "json": {
                "all": re.compile(r'<script id="media-hero-json" data-json="mediaHero" type="application/json">(.*?)</script>', re.S),
                "cover_img": re.compile(r'"thumbnail":{"url":"(.*?)"}', re.S),
                "genre": re.compile(r'"metadataGenres":\[(.*?)\]', re.S),
                "release": re.compile(r'"metadataProps":.*?"Released ([A-Z][a-z]{1,4} \d{1,2}, \d{4})","(.*?)"]', re.S),
            },
            "poster_img": re.compile(r'<meta.*?property=["\']og:image["\'].*?content=["\'](.*?)["\']', re.S),
            "description_pattern": re.compile(r'<div slot="description".*? <rt-text slot="content" size="1">(.*?)</rt-text>', re.S),
            "cast_crew": {
                "all": re.compile(r'<section.*?aria-labelledby="cast-and-crew-label".*?<div class="content-wrap">(.*?)</div>[\s]*?</section>',re.S),
                "img": re.compile(r'<rt-img.*?src="(.*?)".*?>\s*?</rt-img>', re.S),
                "name": re.compile(r'<p class="name" data-qa="person-name">(.*?)</p>', re.S),
                "role": re.compile(r'<p class="role" data-qa="person-role">(.*?)</p>', re.S),
            },
            "score_pattern": {
                "all": re.compile(r"<media-scorecard.*?>(.*?)</media-scorecard>", re.S),
                "tomato": {
                    "score": re.compile(r'<rt-text.*?slot="criticsScore".*?(\d{1,2})%.*?</rt-text>', re.S), 
                    "count": re.compile(r'<rt-link.*?slot="criticsReviews".*?>(.*?)</rt-link>', re.S)
                },
                "popcorn": {
                    "score": re.compile(r'<rt-text.*?slot="audienceScore".*?(\d{1,2})%.*?</rt-text>', re.S), 
                    "count": re.compile(r'<rt-link.*?slot="audienceReviews".*?>(.*?)</rt-link>', re.S)
                },
            }
        }

    def _build_headers(self) -> dict:
        return {
            "User-Agent": random.choice(self._user_agents),
            "Accept-Language": random.choice(self._accept_languages),
            "Accept": random.choice(self._accepts),
            "Referer": random.choice(self._referers),
        }

    # ==================================================================
    # Internal Scraping Logic
    # ==================================================================

    def _crawl_movie_list(self) -> List[dict]:
        try:
            response = self.session.get(self.base_url, headers=self.header.build_headers(), timeout=10)
            response.raise_for_status()
            
        except requests.RequestException as e:
            raise ScraperError(f"Failed to fetch movie list: {str(e)}")
            
        movies = []
        for row in self.page1_pattern["row"].findall(response.text):
            try:
                td = self.page1_pattern["td"].findall(row)
                idx = int(float(td[0].strip()))
                detail_html = self.page1_pattern["detail"].search(td[1].strip()).group(1).strip()
                title = self.page1_pattern["title"].search(detail_html).group(1).strip()
                link = self.page1_pattern["link"].search(detail_html).group(1).strip()
                year = int(self.page1_pattern["year"].search(detail_html).group(1))
                rating = int(self.page1_pattern["score"].search(td[1].strip()).group(1))
                movies.append({"index": idx, "rating": rating, "title": title, "link": link, "year": year})
            except (AttributeError, IndexError, ValueError):
                continue
            
        if not movies:
            raise NotFoundError("No movies found on the main page.")
        
        return movies

    def _crawl_movie_details(self, url) -> dict:
        
        try:
            response = self.session.get(url, headers=self.header.build_headers(), timeout=10)
            response.raise_for_status()
            
        except requests.RequestException as e:
            return {}
        
        html = response.text
        details = {}
        
        if (poster_match := self.page2_pattern["poster_img"].search(html)):
            details["poster_img"] = poster_match.group(1).strip()

        if (desc_match := self.page2_pattern["description_pattern"].search(html)):
            details["description"] = re.sub(r'<.*?>', '', desc_match.group(1).strip())

        if (genre_match := self.page2_pattern["json"]["genre"].search(html)):
            details["genre"] = genre_match.group(1).replace('"', '').replace(', ', ',').lower()
        
        if (json_script_match := self.page2_pattern["json"]["all"].search(html)):
            json_content = json_script_match.group(1)
            if (cover_img_match := self.page2_pattern["json"]["cover_img"].search(json_content)):
                details["cover_img"] = cover_img_match.group(1).strip()
            if (release_match := self.page2_pattern["json"]["release"].search(json_content)):
                details["release_date"] = release_match.group(1).strip()

        if (score_card_match := self.page2_pattern["score_pattern"]["all"].search(html)):
            score_card = score_card_match.group(1)
            if (t_score := self.page2_pattern["score_pattern"]["tomato"]["score"].search(score_card)):
                details["tomato_score"] = int(t_score.group(1))
            if (t_count := self.page2_pattern["score_pattern"]["tomato"]["count"].search(score_card)):
                details["tomato_reviews"] = int(re.sub(r'\D', '', t_count.group(1)))
            if (p_score := self.page2_pattern["score_pattern"]["popcorn"]["score"].search(score_card)):
                details["audience_score"] = int(p_score.group(1))
            if (p_count := self.page2_pattern["score_pattern"]["popcorn"]["count"].search(score_card)):
                details["audience_ratings"] = int(re.sub(r'\D', '', p_count.group(1).replace(',', '')))
        
        if (cast_crew_match := self.page2_pattern["cast_crew"]["all"].search(html)):
            cast_crew_content = cast_crew_match.group(1)
            names = self.page2_pattern["cast_crew"]["name"].findall(cast_crew_content)
            roles = self.page2_pattern["cast_crew"]["role"].findall(cast_crew_content)
            imgs = self.page2_pattern["cast_crew"]["img"].findall(cast_crew_content)
            cast_list = [
                {"name": names[i].strip(), "role": roles[i].strip() if i < len(roles) else "", "img": imgs[i].strip() if i < len(imgs) else ""}
                for i in range(len(names))
            ]
            details["cast_crew"] = cast_list
        
        return details
            
    def _get_all_enriched_movies(self) -> List[dict]:
        
        try:
            movies = self._crawl_movie_list()
        except ScraperError:
            if os.path.exists(self.exporter.csv_path):
                print("Using existing CSV database due to scraping error.")
                return self.exporter.import_movies_csv()
            else:
                raise
            
        with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
            futures = [executor.submit(self._crawl_movie_details, movie['link']) for movie in movies]
            details_list = [f.result() for f in futures]

        for i, movie in enumerate(movies):
            movie.update(details_list[i])
        return movies
    
    # ==================================================================
    # Public API-like Methods
    # ==================================================================

    def get_all_genres(self, movies=[]) -> GenreListResponse:
        """
        Returns a sorted list of all unique, normalized genres from top movies.
        Normalized: lowercase + stripped whitespace.
        """
        if not movies:
            movies = self._get_all_enriched_movies()
            
        genres = set()
        for m in movies:
            if m.get('genre'):
                for g in m['genre'].split(','):
                    norm_g = g.strip().lower()
                    if norm_g:
                        genres.add(norm_g)
        return GenreListResponse(genres=sorted(genres))

    def update_movie_database(self) -> UpdateMoviesResponse:
        """[ENDPOINT] Fetches all movie data and saves it to the CSV file."""
        print("Updating database...")

        enriched_movies = self._get_all_enriched_movies()
        if not enriched_movies:
            raise NotFoundError("No movies found to update.")

        # Print top 3 movies for verification
        print("\n--- Top 3 Movies ---")
        for i, movie in enumerate(enriched_movies[:3]):
            print(f"\n========== Movie #{i+1} ==========")
            for key, value in movie.items():
                print(f"  - {key}: {value}")
        print("===============================\n")
        
        # Convert Dict to MovieDetails model
        movies_adapter = TypeAdapter(List[MovieDetails])
        validated_movies = movies_adapter.validate_python(enriched_movies)

        headers = [
            'index', 'rating', 'title', 'genre', 'year', 'description', 'link', 
            'poster_img', 'cover_img', 'release_date', 'tomato_score', 
            'tomato_reviews', 'audience_score', 'audience_ratings', 'cast_crew'
        ]
        try:
            os.makedirs(self.exporter.csv_folder, exist_ok=True)
            with open(self.exporter.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                for movie in enriched_movies:
                    if 'cast_crew' in movie and isinstance(movie['cast_crew'], list):
                        movie['cast_crew'] = json.dumps(movie['cast_crew'])
                    writer.writerow(movie)
        
            print(f"Database update complete. Saved {len(enriched_movies)} movies.")
            
        except Exception as e:
            raise ScraperError(f"An error occurred during database update: {str(e)}")
        
        return UpdateMoviesResponse(movies=validated_movies)

    def search_movies_live(self, name=None, genre=[]) -> SearchMoviesResponse:
        
        print("Performing live search... this may take a moment.")
        movies = self._get_all_enriched_movies()
        
        if name:
            pattern = re.compile(re.escape(name), re.IGNORECASE)
            movies = [m for m in movies if pattern.search(m.get('title', '').lower())]

        if genre:
            for g in genre:
                g = g.lower().strip()
                movies = [m for m in movies if re.search(f"{re.escape(g)}", m.get('genre', '').lower())]
            
            # available_genres = self.get_all_genres(movies).genres
            # if available_genres:
            #     movies = [m for m in movies if any(g in (m.get('genre') or '').lower() for g in available_genres)]
            # else:
            #     movies = []

        if not movies:
            raise NotFoundError("No movies matched your search criteria.")
        
        # Convert Dict to MovieDetails model
        movies_adapter = TypeAdapter(List[MovieDetails])
        validated_movies = movies_adapter.validate_python(movies)

        print("Live search complete!")
        
        return SearchMoviesResponse(count=len(movies), movies=validated_movies)

    def get_movie_details(self, name=None):
        # return "ok"
        print("movie_name:", name)
        if name is None or len(name) == 0:
            return NotFoundError("No movies matched your search criteria.")
        movies = self._crawl_movie_list()
        for movie in movies:
            if re.match(rf'^{name}$', movie["title"], re.IGNORECASE):
                # return "ok"
                result = self._crawl_movie_details(movie['link'])
                movies_adapter = TypeAdapter(MovieDetails)
                movie.update(result)
                return movies_adapter.validate_python(movie)

        return NotFoundError("No movies matched your search criteria.")