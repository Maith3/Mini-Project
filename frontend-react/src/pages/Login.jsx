import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/style.css";

function Login() {
  const navigate = useNavigate();

  const [loginData, setLoginData] = useState({
    username: "",
    password: "",
  });

  const handleChange = (e) => {
    setLoginData({
      ...loginData,
      [e.target.name]: e.target.value,
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    const { username, password } = loginData;

    if (!username || !password) {
      alert("Please fill all fields");
      return;
    }

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/token",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem(
          "token",
          data.access_token
        );

        alert("Login Successful");

        navigate("/prediction");
      } else {
        alert(
          data.detail ||
            "Invalid username or password"
        );
      }
    } catch (error) {
      console.error(error);

      alert(
        "Cannot connect to backend server"
      );
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>CardioPredict</h1>

        <h2>Login Form</h2>

        <div className="switch">
          <button className="active">
            Login
          </button>

          <button
            onClick={() => navigate("/signup")}
          >
            Signup
          </button>
        </div>

        <input
          type="text"
          name="username"
          placeholder="Username"
          value={loginData.username}
          onChange={handleChange}
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={loginData.password}
          onChange={handleChange}
        />

        <a href="#">
          Forgot Password?
        </a>

        <button
          className="submit-btn"
          onClick={handleLogin}
        >
          Login
        </button>

        <p className="signup-text">
          Not a member?{" "}
          <Link to="/signup">
            Signup Now
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;