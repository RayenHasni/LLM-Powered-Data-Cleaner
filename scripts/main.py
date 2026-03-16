import argparse
import os

from scripts.data_cleaning import DataCleaning
from scripts.data_ingestion import DataIngestion


def run_pipeline(df, use_ai=False):
	cleaner = DataCleaning()
	cleaned_df = cleaner.clean_data(df)

	ai_summary = None
	if use_ai:
		try:
			from scripts.agent import Ai_agent
			agent = Ai_agent()
			ai_summary = agent.process_data(cleaned_df)
		except Exception as e:
			ai_summary = f"AI cleaning skipped: {e}"

	return cleaned_df, ai_summary


def parse_args():
	parser = argparse.ArgumentParser(description="Data Cleaner CLI")
	parser.add_argument(
		"--source",
		required=True,
		choices=["file", "api", "db"],
		help="Data source type",
	)
	parser.add_argument("--path", help="File path for source=file")
	parser.add_argument("--api-url", help="API endpoint for source=api")
	parser.add_argument(
		"--db-target",
		help="DB target string for source=db (server=...;database=...;table=...;schema=...)",
	)
	parser.add_argument("--sheet", type=int, default=0, help="Excel sheet index")
	parser.add_argument(
		"--output",
		help="Optional output CSV path. Defaults to ./data/cleaned_output.csv",
	)
	parser.add_argument(
		"--with-ai",
		action="store_true",
		help="Generate AI summary using Gemini",
	)
	return parser.parse_args()


def main():
	args = parse_args()
	ingestion = DataIngestion()

	if args.source == "file":
		if not args.path:
			raise ValueError("--path is required when --source file")
		ext = os.path.splitext(args.path)[1].lower()
		if ext == ".csv":
			df = ingestion.load_csv(args.path)
		elif ext in [".xlsx", ".xls"]:
			df = ingestion.load_excel(args.path, sheetname=args.sheet)
		else:
			raise ValueError("Unsupported file extension. Use .csv, .xlsx or .xls")

	elif args.source == "api":
		if not args.api_url:
			raise ValueError("--api-url is required when --source api")
		df = ingestion.fetch_api(args.api_url)

	else:
		if not args.db_target:
			raise ValueError("--db-target is required when --source db")
		df = ingestion.load_sql_server_trusted(args.db_target)

	if df is None:
		raise RuntimeError("Failed to load data from source")

	cleaned_df, ai_summary = run_pipeline(df, use_ai=args.with_ai)

	print("Cleaning completed.")
	print(f"Rows: {len(df)} -> {len(cleaned_df)}")
	print(cleaned_df.head(10).to_string(index=False))

	output_path = args.output or os.path.join("data", "cleaned_output.csv")
	os.makedirs(os.path.dirname(output_path), exist_ok=True)
	cleaned_df.to_csv(output_path, index=False)
	print(f"Saved cleaned output to: {output_path}")

	if ai_summary:
		print("\nAI Summary:\n")
		print(ai_summary)


if __name__ == "__main__":
	main()
