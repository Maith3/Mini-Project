document.addEventListener("DOMContentLoaded", () => {

    const loginBtn = document.querySelector(".submit-btn");

    if (loginBtn) {

        loginBtn.addEventListener("click", async (e) => {

            e.preventDefault();

            const username =
                document.getElementById("username").value;

            const password =
                document.getElementById("password").value;

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
                                "application/x-www-form-urlencoded"
                        },
                        body: formData
                    }
                );

                const data = await response.json();

                if (response.ok) {

                    localStorage.setItem(
                        "token",
                        data.access_token
                    );

                    alert("Login Successful");

                    window.location.href =
                        "index.html";

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

        });

    }

});