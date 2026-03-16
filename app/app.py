import io
import os
import requests
import pandas as pd
import streamlit as st


def get_backend_url():
	# Prefer Streamlit secrets when available, then environment, then localhost default.
	try:
		if "BACKEND_URL" in st.secrets:
			return st.secrets["BACKEND_URL"]
	except Exception:
		pass

	return os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


BACKEND_URL = get_backend_url()


def render_styles():
	st.markdown(
		"""
		<style>
		@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

		:root {
			--bg-1: #f7f8fc;
			--bg-2: #dfe7ff;
			--panel: #ffffff;
			--text: #111827;
			--muted: #475569;
			--accent: #0f766e;
			--accent-2: #1d4ed8;
			--border: #d6dce7;
		}

		.stApp {
			background:
				radial-gradient(circle at 10% 10%, rgba(29, 78, 216, 0.10), transparent 34%),
				radial-gradient(circle at 90% 30%, rgba(15, 118, 110, 0.14), transparent 33%),
				linear-gradient(145deg, var(--bg-1), var(--bg-2));
			color: var(--text);
			font-family: 'Manrope', sans-serif;
		}

		h1, h2, h3, h4 {
			font-family: 'Space Grotesk', sans-serif;
			letter-spacing: -0.02em;
		}

		.stSidebar {
			background: linear-gradient(180deg, #ffffff 0%, #ecf6ff 100%);
		}

		.block-container {
			padding-top: 1.5rem;
			max-width: 1500px;
		}

		.hero {
			background: linear-gradient(130deg, #0f172a, #1d4ed8);
			color: #f8fafc;
			padding: 1.2rem 1.4rem;
			border-radius: 16px;
			border: 1px solid rgba(255,255,255,0.15);
			box-shadow: 0 12px 35px rgba(15, 23, 42, 0.22);
			margin-bottom: 1rem;
			animation: floatIn .5s ease-out;
		}

		@keyframes floatIn {
			from {opacity: 0; transform: translateY(8px);} 
			to {opacity: 1; transform: translateY(0);}
		}

		.muted {
			color: var(--muted);
		}
		</style>
		""",
		unsafe_allow_html=True,
	)


def clean_file(uploaded_file):
	files = {
		"file": (
			uploaded_file.name,
			uploaded_file.getvalue(),
			uploaded_file.type or "application/octet-stream",
		)
	}
	return requests.post(f"{BACKEND_URL}/clean-data", files=files, timeout=120)


def clean_api(api_url):
	payload = {"api_url": api_url}
	return requests.post(f"{BACKEND_URL}/clean-api", json=payload, timeout=120)


def clean_db(db_target):
	payload = {"db_target": db_target}
	return requests.post(f"{BACKEND_URL}/clean-db", json=payload, timeout=120)


def show_results(response):
	if response.status_code != 200:
		st.error(f"Backend error ({response.status_code}): {response.text}")
		return

	payload = response.json()
	records = payload.get("cleaned data", [])
	ai_summary = payload.get("ai_summary")

	df = pd.DataFrame(records)
	st.success("Cleaning completed successfully.")

	col1, col2 = st.columns([2, 1])
	with col1:
		st.subheader("Cleaned Dataset")
		st.dataframe(df, width="stretch", height=520)
	with col2:
		st.metric("Rows", len(df))
		st.metric("Columns", len(df.columns))

	csv_bytes = df.to_csv(index=False).encode("utf-8")
	st.download_button(
		"Download cleaned CSV",
		data=csv_bytes,
		file_name="cleaned_data.csv",
		mime="text/csv",
		width="stretch",
	)

	if ai_summary:
		with st.expander("AI Summary", expanded=False):
			st.write(ai_summary)


def main():
	st.set_page_config(page_title="Data Cleaner", page_icon="🧼", layout="wide")
	render_styles()

	st.markdown(
		"""
		<div class="hero">
			<h2 style="margin:0;">Data Cleaner Workspace</h2>
			<p style="margin:.4rem 0 0 0;">Upload from file, SQL Server, or API and get cleaned results fast.</p>
		</div>
		""",
		unsafe_allow_html=True,
	)

	st.sidebar.title("Pipeline")
	source = st.sidebar.radio("Choose source", ["FILE", "DB", "API"], index=0)

	st.markdown("<p class='muted'>Choose a source in the sidebar and start cleaning.</p>", unsafe_allow_html=True)

	if source == "FILE":
		st.subheader("Clean a File")
		uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
		if st.button("Clean File", type="primary", width="stretch"):
			if not uploaded_file:
				st.warning("Please upload a file first.")
			else:
				with st.spinner("Cleaning file..."):
					response = clean_file(uploaded_file)
				show_results(response)

	elif source == "DB":
		st.subheader("Clean SQL Server Table")
		db_target = st.text_input(
			"DB Target String",
			value="server=MY_SERVER;database=MY_DB;table=MY_TABLE;schema=dbo",
			help="Trusted connection is used by backend.",
		)
		st.caption("Format: server=...;database=...;table=...;schema=...")

		if st.button("Clean DB Table", type="primary", width="stretch"):
			with st.spinner("Reading and cleaning SQL Server table..."):
				response = clean_db(db_target)
			show_results(response)

	else:
		st.subheader("Clean API Data")
		api_url = st.text_input("API URL", value="https://jsonplaceholder.typicode.com/posts")

		if st.button("Clean API", type="primary", width="stretch"):
			with st.spinner("Fetching and cleaning API data..."):
				response = clean_api(api_url)
			show_results(response)


if __name__ == "__main__":
	main()
