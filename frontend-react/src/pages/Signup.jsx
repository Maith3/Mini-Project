import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles/style.css";

function Signup() {
  const navigate = useNavigate();

  const [userData, setUserData] = useState({
    username: "",
    email: "",
    password: "",
    role: "",
    hospitalName: "",
    HP_ID: "",
  });

  const handleChange = (e) => {
    setUserData({
      ...userData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSignup = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/signup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert("Signup Successful");

        // React Router Navigation
        navigate("/login");
      } else {
        alert(data.detail);
      }
    } catch (error) {
      alert("Backend not running");
      console.error(error);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>CardioPredict</h1>
        <h2>Signup Form</h2>

        <input
          type="text"
          id="username"
          placeholder="Username"
          value={userData.username}
          onChange={handleChange}
        />

        <input
          type="email"
          id="email"
          placeholder="Email Address"
          value={userData.email}
          onChange={handleChange}
        />

        <input
          type="password"
          id="password"
          placeholder="Password"
          value={userData.password}
          onChange={handleChange}
        />

        <input
          type="text"
          id="role"
          placeholder="Role (Doctor/Staff)"
          value={userData.role}
          onChange={handleChange}
        />

        <input
          type="text"
          id="hospitalName"
          placeholder="Hospital Name"
          value={userData.hospitalName}
          onChange={handleChange}
        />

        <input
          type="text"
          id="HP_ID"
          placeholder="Hospital Professional ID"
          value={userData.HP_ID}
          onChange={handleChange}
        />

        <button
          className="submit-btn"
          onClick={handleSignup}
        >
          Signup
        </button>

        <p className="signup-text">
          Already have an account?{" "}
          <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}

export default Signup;