import React, { useState } from "react";
import "../styles/style.css";

function Prediction() {
  const [patientData, setPatientData] = useState({
    Name: "",
    PID: "",
    Age: "",
    BMI: "",
    Systolic_BP: "",
    Diabetes_Status: "",
    Estimated_LDL: "",
    Total_Cholesterol: "",
    HDL: "",
  });

  const [result, setResult] = useState("");

  const handleChange = (e) => {
    setPatientData({
      ...patientData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePredict = async () => {
    const payload = {
      Name: patientData.Name,
      PID: parseInt(patientData.PID),
      Age: parseInt(patientData.Age),
      BMI: parseFloat(patientData.BMI),
      Systolic_BP: parseFloat(patientData.Systolic_BP),
      Diabetes_Status: parseInt(patientData.Diabetes_Status),
      Estimated_LDL: parseFloat(patientData.Estimated_LDL),
      Total_Cholesterol: parseFloat(patientData.Total_Cholesterol),
      HDL: parseFloat(patientData.HDL),
    };

    try {
      const token = localStorage.getItem("token");

      const response = await fetch(
        "http://127.0.0.1:8000/predict",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error("Prediction Failed");
      }

      // Receive PDF
      const pdfBlob = await response.blob();

      // Create download link
      const pdfUrl = window.URL.createObjectURL(pdfBlob);

      const link = document.createElement("a");
      link.href = pdfUrl;
      link.download = `Prediction_Report_${patientData.PID}.pdf`;

      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(pdfUrl);

      setResult("Prediction Generated & PDF Downloaded Successfully");
    } catch (error) {
      console.error(error);
      setResult("Prediction Failed");
      alert("Prediction Failed");
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>CardioPredict</h1>

        <h2>CVD Risk Prediction</h2>

        <input
          type="text"
          name="Name"
          placeholder="Patient Name"
          value={patientData.Name}
          onChange={handleChange}
        />

        <input
          type="number"
          name="PID"
          placeholder="Patient ID"
          value={patientData.PID}
          onChange={handleChange}
        />

        <input
          type="number"
          name="Age"
          placeholder="Age"
          value={patientData.Age}
          onChange={handleChange}
        />

        <input
          type="number"
          name="BMI"
          placeholder="BMI"
          value={patientData.BMI}
          onChange={handleChange}
        />

        <input
          type="number"
          name="Systolic_BP"
          placeholder="Systolic BP"
          value={patientData.Systolic_BP}
          onChange={handleChange}
        />

        <input
          type="number"
          name="Diabetes_Status"
          placeholder="Diabetes Status (0/1)"
          value={patientData.Diabetes_Status}
          onChange={handleChange}
        />

        <input
          type="number"
          name="Estimated_LDL"
          placeholder="Estimated LDL"
          value={patientData.Estimated_LDL}
          onChange={handleChange}
        />

        <input
          type="number"
          name="Total_Cholesterol"
          placeholder="Total Cholesterol"
          value={patientData.Total_Cholesterol}
          onChange={handleChange}
        />

        <input
          type="number"
          name="HDL"
          placeholder="HDL"
          value={patientData.HDL}
          onChange={handleChange}
        />

        <button
          className="submit-btn"
          onClick={handlePredict}
        >
          Predict Risk
        </button>

        {result && (
          <div
            id="result"
            style={{
              marginTop: "15px",
              fontWeight: "bold",
            }}
          >
            {result}
          </div>
        )}
      </div>
    </div>
  );
}

export default Prediction;