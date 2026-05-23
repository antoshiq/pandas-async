import pandas as pd
dayfirst = True

# date normalize
def date_normalize(df):
    date_columns = ['install_date', 'warranty_until', 'last_calibration_date', 'last_service_date']
    for column in date_columns:
        df[column] = pd.to_datetime(df[column], errors='coerce')
    return df

# status normalize
def status_normalize(df):
    statuses = {
        'operational' : 'operational', 'ok': 'operational', 'op' : 'operational', 'working' : 'operational',
        'planned_installation' : 'planned_installation', 'planned' : 'planned_installation', 'to_install' : 'planned_installation', 'scheduled_install' : 'planned_installation',
        'maintenance_scheduled' : 'maintenance_scheduled', 'service_scheduled' : 'maintenance_scheduled', 'maintenance' : 'maintenance_scheduled', 'needs_repair' : 'maintenance_scheduled', 'maint_sched' : 'maintenance_scheduled',
        'faulty' : 'faulty', 'broken' : 'faulty', 'error': 'faulty'
    }

    df['status'] = df['status'].astype(str).str.lower().str.strip().map(statuses)
    return df

# invalid calibration date normalize
def invalid_calibration_date_normalize(df):
    invalid_calinration_date = df['last_calibration_date'] < df['install_date']
    df.loc[invalid_calinration_date, 'last_calibration_date'] = pd.NaT
    return df

# warranity
def get_active_warranty(df):
    active_warranty = df[df['warranty_until'] >= pd.Timestamp.today()].copy()
    return active_warranty

# issues
def get_clinics_with_most_issues(df):
    clinics_with_most_issues = df.groupby(['clinic_id', 'clinic_name', 'issues_text'])['issues_reported_12mo'].sum()
    clinics_with_most_issues = clinics_with_most_issues.reset_index().sort_values('issues_reported_12mo', ascending=False)
    clinics_with_most_issues = clinics_with_most_issues[ ['clinic_id', 'clinic_name','issues_reported_12mo', 'issues_text' ] ]
    return clinics_with_most_issues

# needs calibration
def get_needs_calibration_models(df):
    df['needs_calibration'] = (df['last_calibration_date'].isna()) | (df['last_calibration_date'] < (pd.Timestamp.today() - pd.DateOffset(years=1)))
    
    calibration_report = df[df['status'] == 'operational'][
        ['device_id', 'clinic_name', 'model', 'install_date', 'last_calibration_date', 'needs_calibration']
    ]

    return calibration_report

# pivot table
def create_pivot_table(df):
    pt = pd.pivot_table(
        df,
        index=['clinic_name', 'department'], 
        columns=['model'],                   
        values=['device_id', 'uptime_pct', 'failure_count_12mo'],
        aggfunc={
            'device_id': 'count',           
            'uptime_pct': 'mean',           
            'failure_count_12mo': 'sum'     
        },
        fill_value=0 
    )
    return pt