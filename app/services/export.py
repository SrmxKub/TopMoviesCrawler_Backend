import os
from fastapi.responses import FileResponse

class ExportService:
    def __init__(self, csv_folder="app/export", csv_filename="movies.csv"):
        self.csv_folder = csv_folder
        self.csv_filename = csv_filename
        self.csv_path = os.path.join(csv_folder, csv_filename)

    def export_csv(self) -> FileResponse:
        """
        Returns the CSV file as a downloadable response.
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"No CSV file found at {self.csv_path}. Please update the database first.")

        return FileResponse(
            path=self.csv_path,
            media_type="text/csv",
            filename=self.csv_filename
        )
