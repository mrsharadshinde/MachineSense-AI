import numpy as np  
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import  os

# fuction to create synthetic dataset 
def generate_synthetic_data(n_samples = 300):
    np.random.seed(42) # keep results reproducible
    data = {
        # document completness score between 60 to 100
        'document_completeness': np.random.uniform(60, 100, n_samples),

        # warning count between 0 to 8
        'warning_count': np.random.randint(0, 9, n_samples),

        # checklist items between 10 to 30
        'checklist_items': np.random.randint(10, 30, n_samples),

        #machine age 30 days to 5 years (days)
        'machine_age_days': np.random.randint(30, 365*5, n_samples),

        # operating hours between 100 to 5000
        'operating_hours': np.random.randint(100, 5001, n_samples),
    }

    #save to dataframe
    df = pd.DataFrame(data)

    #health score calculation
    # start with completeness score
    health = df['document_completeness'].copy()

    # penalize by warning, machine age and operating hours 
    health -= df['warning_count'] * 5
    health -= (df['machine_age_days'] /365) * 2
    health -= (df['operating_hours'] / 1000) * 3

    # clip health score between 0 and 100 
    health = health.clip(0, 100)

    df['health_score'] = health

    #function to lable health status 
    def label_from_health(score):
        if score >= 80:
            return 'Good'
        elif score >= 60:
            return 'Moderate'   
        else:
            return 'Poor'

    df['risk_label'] = df['health_score'].apply(label_from_health)

    return df

def main():
    print("Generating synthetic data...")
    df = generate_synthetic_data(n_samples=1000)

    print(df.head())

    #features and lables
    feature_cols = ['document_completeness', 'warning_count', 'checklist_items', 'machine_age_days', 'operating_hours']
    
    x = df[feature_cols]
    y = df['risk_label']

    # split data into train and test sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state=42)

    # define random forest classifirer model
    model = RandomForestClassifier(n_estimators=300, random_state=42, class_weight='balanced')
    
    # tain the model
    model.fit(x_train, y_train)

    #Eavaluate the mode
    y_pred = model.predict(x_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    #savethe mode
    os.makedirs('models', exist_ok = True)
    model_path = 'models/maintenance_risk_model.pkl'
    joblib.dump(model, model_path)

if  __name__ == "__main__":
    main()