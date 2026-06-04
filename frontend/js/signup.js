document
.getElementById("signupBtn")
.addEventListener("click", async () => {

    const userData = {

        username:
        document.getElementById("username").value,

        email:
        document.getElementById("email").value,

        password:
        document.getElementById("password").value,

        role:
        document.getElementById("role").value,

        hospitalName:
        document.getElementById("hospitalName").value,

        HP_ID:
        document.getElementById("HP_ID").value

    };

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/signup",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                    "application/json"
                },

                body:
                JSON.stringify(userData)
            }
        );

        const data =
        await response.json();

        if(response.ok){

            alert(
                "Signup Successful"
            );

            window.location.href =
            "login.html";

        }
        else{

            alert(
                data.detail
            );
        }

    }
    catch(error){

        alert(
            "Backend not running"
        );

        console.error(error);
    }

});