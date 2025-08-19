import { useState } from "react";

function App() {
  const [formData, setFormData] = useState({
    link: "",
    seitnummer: "",
    interest: ""
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

const handleSubmit = async () => {
  try {
    const payload = {
      input_link: formData.link,
      input_seitnummer: formData.seitnummer,
      input_interest: formData.interest,
    };

    const response = await fetch("http://localhost:8000/data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    // Read response as text
    const data = await response.text();
    console.log("Response from server:", data);
    alert(`Server response: ${data}`);
  } catch (error) {
    console.error("Error sending data:", error);
    alert("Failed to send data. Check console for details.");
  }
};

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2 style={{ textAlign: "center" }}>Kleinenanzeigen Assistent</h2>

      <div style={{ marginBottom: "15px" }}>
        <label style={{ display: "block", marginBottom: "5px" }}>Link:</label>
        <input
          type="text"
          name="link"
          value={formData.link}
          onChange={handleChange}
          style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
        />
      </div>

      <div style={{ marginBottom: "15px" }}>
        <label style={{ display: "block", marginBottom: "5px" }}>Seitnummer:</label>
        <input
          type="text"
          name="seitnummer"
          value={formData.seitnummer}
          onChange={handleChange}
          style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
        />
      </div>

      <div style={{ marginBottom: "15px" }}>
        <label style={{ display: "block", marginBottom: "5px" }}>What is your interest:</label>
        <textarea
          name="interest"
          value={formData.interest}
          onChange={handleChange}
          maxLength={500}
          rows={5}
          style={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ccc", resize: "vertical" }}
        />
      </div>

      <button
        onClick={handleSubmit}
        style={{ width: "100%", padding: "12px", borderRadius: "5px", border: "none", backgroundColor: "#007BFF", color: "#fff", cursor: "pointer", fontSize: "16px" }}
      >
        Process
      </button>
    </div>
  );
}

export default App;
