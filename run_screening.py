"""CLI runner for screening every supported resume in a folder."""
import argparse
from pathlib import Path
from app.service import screen_folder, write_outputs

def main() -> None:
    parser = argparse.ArgumentParser(description="Rank resumes against a job description.")
    parser.add_argument("--jd", required=True, type=Path, help="Path to a .txt job description")
    parser.add_argument("--resumes", required=True, type=Path, help="Folder containing PDF, DOCX, or TXT resumes")
    parser.add_argument("--output", default=Path("outputs"), type=Path, help="Output directory")
    args = parser.parse_args()
    result = screen_folder(args.jd, args.resumes)
    json_path, csv_path = write_outputs(result, args.output)
    print(f"Ranked {result['total_candidates']} candidates.")
    print(f"JSON: {json_path}\nCSV: {csv_path}")

if __name__ == "__main__":
    main()
