import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  const handleSendOtp = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/forgot-password",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to send OTP"
        );
      }

      alert("OTP sent successfully");

      navigate("/reset-password", {
        state: { email },
      });
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Forgot Password</h1>

        <input
          type="email"
          placeholder="Enter Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <button
          className="submit-btn"
          onClick={handleSendOtp}
        >
          Send OTP
        </button>
      </div>
    </div>
  );
}

export default ForgotPassword;