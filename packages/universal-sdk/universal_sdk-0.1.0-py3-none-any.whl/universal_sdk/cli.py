import argparse
from .client import Client

def main():
    parser = argparse.ArgumentParser(description="Universal SDK CLI for File Text Extractor API")
    parser.add_argument("file_path", help="Path to PDF or CSV file to upload")
    parser.add_argument("--url", default="http://localhost:8000", help="Base API URL")
    args = parser.parse_args()

    client = Client(base_url=args.url)
    response = client.upload_file(args.file_path)
    print(response)
