import streamlit as st
import pandas as pd
import zipfile
import io

st.set_page_config(layout="wide")

st.title("CSV SKU Filter App")

st.write(
    "This app filters a large 'old.csv' file based on the SKUs present in an 'updated.csv' file. "
    "Please upload the 'old.csv' file as a zip archive."
)

# --- File Uploaders ---
updated_file = st.file_uploader("Upload the updated.csv file", type=["csv"])
old_zip_file = st.file_uploader("Upload the old.csv as a zip file", type=["zip"])


def process_files(updated_df, old_df):
    """Filters the old DataFrame based on SKUs from the updated DataFrame."""
    if 'SKU' not in updated_df.columns or 'SKU' not in old_df.columns:
        st.error("Both CSV files must contain a 'SKU' column.")
        return None

    updated_skus = updated_df['sku'].unique()
    filtered_df = old_df[old_df['sku'].isin(updated_skus)]
    return filtered_df


if updated_file and old_zip_file:
    try:
        # Read the updated.csv
        updated_df = pd.read_csv(updated_file)

        # Handle the zipped old.csv
        with zipfile.ZipFile(old_zip_file, 'r') as z:
            # Find the csv file inside the zip
            csv_files_in_zip = [f for f in z.namelist() if f.endswith('.csv')]
            if not csv_files_in_zip:
                st.error("No CSV file found in the uploaded zip archive.")
            else:
                # Assuming the first CSV file is the one we want
                old_csv_filename = csv_files_in_zip[0]
                with z.open(old_csv_filename) as f:
                    # To avoid issues with different line endings, read the file into a buffer
                    # and then let pandas read from the buffer.
                    csv_buffer = io.StringIO(f.read().decode('utf-8'))
                    old_df = pd.read_csv(csv_buffer)

                st.success("Files uploaded and read successfully.")

                # --- Processing and Display ---
                with st.spinner('Filtering the data...'):
                    filtered_df = process_files(updated_df, old_df)

                if filtered_df is not None:
                    st.success(f"Filtering complete. {len(filtered_df)} rows matched.")

                    st.subheader("Preview of the Filtered Data")
                    st.dataframe(filtered_df.head())

                    # --- Download Button ---
                    @st.cache_data
                    def convert_df_to_csv(df):
                        # IMPORTANT: Cache the conversion to prevent computation on every rerun
                        return df.to_csv(index=False).encode('utf-8')

                    csv_to_download = convert_df_to_csv(filtered_df)

                    st.download_button(
                        label="Download Filtered Data as CSV",
                        data=csv_to_download,
                        file_name="filtered_data.csv",
                        mime="text/csv",
                    )

    except Exception as e:
        st.error(f"An error occurred: {e}")
