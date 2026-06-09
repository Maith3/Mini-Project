import React, { useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";

function ResetPassword() {
  const location = useLocation();
  const navigate = useNavigate();

  const email =
    location.state?.email || "";

  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] =
    useState("");

  const handleReset = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/reset-password",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            email,
            otp,
            new_password: newPassword,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Password reset failed"
        );
      }

      alert("Password reset successful");

      navigate("/");
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Reset Password</h1>

        <input
          type="email"
          value={email}
          readOnly
        />

        <input
          type="text"
          placeholder="Enter OTP"
          value={otp}
          onChange={(e) =>
            setOtp(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) =>
            setNewPassword(
              e.target.value
            )
          }
        />

        <button
          className="submit-btn"
          onClick={handleReset}
        >
          Reset Password
        </button>
      </div>
    </div>
  );
}

export default ResetPassword;