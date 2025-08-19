from flask import Flask, request, jsonify
import os
import subprocess
import pandas as pd

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allows all origins by default

@app.route('/data', methods=['POST'])
def receive_data():
    # Get JSON body from POST request
    data = request.get_json()

    # Extract fields from JSON
    input_link = data.get("input_link")
    input_seitnummer = data.get("input_seitnummer")
    input_interest = data.get("input_interest")

    # Set environment variables
    if input_link:
        os.environ["INPUT_LINK"] = input_link
    if input_seitnummer:
        os.environ["INPUT_SEITNUMMER"] = str(input_seitnummer)
    if input_interest:
        os.environ["INPUT_INTEREST"] = input_interest

    # Expand ~ to the full home directory path
    workdir = os.path.expanduser("~/backend/purchase_copilot")

    # Run the process and wait for it to finish
    result = subprocess.run(
        ["crewai", "flow", "kickoff"],
        cwd=workdir,
        capture_output=True,
        text=True
    )

    print("Process finished with code:", result.returncode)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    # Path to the CSV file
    csv_path = os.path.join(workdir, "retrieved_data.csv")

    # Read the CSV if it exists
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return jsonify({"status": "success", "received": df.to_dict(orient="records")}), 200
    else:
        print("⚠️ CSV file not found:", csv_path)
        return jsonify({"status": "error", "message": "CSV file not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
