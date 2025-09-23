import os
import csv
import json
from typing import List
from fastapi.responses import FileResponse
from app.schemas.exceptions import NotFoundError

class ExportService:
    def __init__(self, csv_folder="app/export", csv_filename="movies.csv"):
        self.csv_folder = csv_folder
        self.csv_filename = csv_filename
        self.csv_path = os.path.join(csv_folder, csv_filename)
        
    def import_movies_csv(self) -> List[dict]:
        movies = []
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'cast_crew' in row and row['cast_crew']:
                    row['cast_crew'] = json.loads(row['cast_crew'])
                    
                for key in ['index', 'rating', 'year', 'tomato_score', 'tomato_reviews', 'audience_score', 'audience_ratings']:
                    row[key] = int(row.get(key) or 0)
                movies.append(row)
        return movies

    def export_csv(self) -> FileResponse:
        """
        Returns the CSV file as a downloadable response.
        """
        if not os.path.exists(self.csv_path):
            raise NotFoundError(f"No CSV file found at {self.csv_path}. Please update the database first.")

        return FileResponse(
            path=self.csv_path,
            media_type="text/csv",
            filename=self.csv_filename
        )
