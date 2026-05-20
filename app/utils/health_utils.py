def get_parameter_table(data):
    table = [['Parameter','Patient Value', 'Normal Range', 'Status']]
    status={}
    
    #BMI
    if data.BMI < 18.5:
        status['BMI'] = 'Underweight'
    elif data.BMI < 25:
        status['BMI'] = 'Normal'
    elif data.BMI <30:
        status['BMI'] = 'Overweight'
    elif data.BMI>=30:
        status['BMI'] = 'Obese'
        
    #Systolic BP
    if data.Systolic_BP<90:
        status['Systolic_BP'] = 'Low'
    elif data.Systolic_BP<=120:
        status['Systolic_BP'] = 'Normal'
    elif data.Systolic_BP<=139:
        status['Systolic_BP'] = 'Elevated'
    elif data.Systolic_BP>=140:
        status['Systolic_BP'] = 'High'
        
    #Diabetes Status
    if data.Diabetes_Status == 0:
        status['Diabetes_Status'] = 'Non-Diabetic'
    elif data.Diabetes_Status == 1:
        status['Diabetes_Status'] = 'Diabetic'
        
    #Estimated LDL
    if data.Estimated_LDL < 100:
        status['Estimated_LDL'] = 'Optimal'
    elif data.Estimated_LDL < 130:
        status['Estimated_LDL'] = 'Near Optimal'
    elif data.Estimated_LDL < 160:
        status['Estimated_LDL'] = 'Borderline High'
    elif data.Estimated_LDL < 190:
        status['Estimated_LDL'] = 'High'
    elif data.Estimated_LDL >= 190:
        status['Estimated_LDL'] = 'Very High'
    
    #Total Cholesterol
    if data.Total_Cholesterol < 200:
        status['Total_Cholesterol'] = 'Desirable'
    elif data.Total_Cholesterol < 240:
        status['Total_Cholesterol'] = 'BorderLine High'
    elif data.Total_Cholesterol >= 240:
        status['Total_Cholesterol'] = 'High'
    
    #HDL
    if data.HDL < 40:
        status['HDL'] = 'Low'
    elif data.HDL < 60:
        status['HDL'] = 'Normal'
    elif int(data.HDL) in range(60,90):
        status['HDL'] = 'Protective'
    elif data.HDL >= 90:
        status['HDL'] = 'High'
    
    table.append([
        'BMI',
        data.BMI,
        '18.5 - 24.9',
        status['BMI']
    ])
    
    table.append([
        'Systolic BP',
        data.Systolic_BP,
        '90 - 120 mmHg',
        status['Systolic_BP']
    ])
    
    table.append([
        'Diabetes Status',
        data.Diabetes_Status,
        '0 = Non-Diabetic',
        status['Diabetes_Status']
    ])
    
    table.append([
        'Estimated LDL',
        data.Estimated_LDL,
        '< 100 mg/dL',
        status['Estimated_LDL']
    ])
    
    table.append([
        'Total Cholesterol',
        data.Total_Cholesterol,
        '< 200 mg/dL',
        status['Total_Cholesterol']
    ])
    
    table.append([
        'HDL',
        data.HDL,
        '> 60 mg/dL',
        status['HDL']
    ])
    
    return table