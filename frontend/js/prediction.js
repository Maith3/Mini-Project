document
.getElementById("predictBtn")
.addEventListener("click", async () => {

    const patientData = {

        Name:
        document.getElementById("Name").value,

        PID:
        parseInt(
            document.getElementById("PID").value
        ),

        Age:
        parseInt(
            document.getElementById("Age").value
        ),

        BMI:
        parseFloat(
            document.getElementById("BMI").value
        ),

        Systolic_BP:
        parseFloat(
            document.getElementById("Systolic_BP").value
        ),

        Diabetes_Status:
        parseInt(
            document.getElementById("Diabetes_Status").value
        ),

        Estimated_LDL:
        parseFloat(
            document.getElementById("Estimated_LDL").value
        ),

        Total_Cholesterol:
        parseFloat(
            document.getElementById("Total_Cholesterol").value
        ),

        HDL:
        parseFloat(
            document.getElementById("HDL").value
        )
    };

    try {

        const token =
        localStorage.getItem("token");

        const response =
        await fetch(
            "http://127.0.0.1:8000/predict",
            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json",
                    "Authorization":
                    "Bearer " + token
                },

                body:
                JSON.stringify(patientData)
            }
        );

        const result =
        await response.json();

        document.getElementById(
            "result"
        ).innerHTML =
        "<h3>Prediction Generated</h3>";

        console.log(result);

    }
    catch(error){

        alert(
            "Prediction Failed"
        );

        console.log(error);
    }

});