import pandas as pd
import datetime

on_calls_code=["On Call MF", "On Call WE", "OnCall PH"]
q_notifiers=["Weekdays", "Saturdays", "Sundays", "Weekday Public Holidays", "Weekend Public Holidays"]
q_queries=[
    "notifiers=='weekday'",
    "notifiers=='saturday'",
    "notifiers=='sunday' and label=='On Call WE'",
    "notifiers=='sunday' and label=='OnCall PH'",
    "notifiers=='weekend_pubhol'"
]

def apply_rates(df: pd.DataFrame, rates: list):
    ndf=df.copy()
    def apply_rate(rowdat, rate_info):
        # Check if date is inside the rate
        if rowdat.Column1>=rate_info["start_date"]:
            if rowdat.label=="On Call MF":
                return rate_info["weekday"]
            elif rowdat.label=="On Call WE":
                return rate_info["saturday"] if rowdat.Column1.weekday()==5 else rate_info["sunday"]
            elif rowdat.label=="OnCall PH":
                return rate_info["sunday"] if rowdat.Column1.weekday()<5 else rate_info["weekend_pubhol"]
        else:
            return False

    all_rates=[]
    notifiers=[]
    for rowdat in df.itertuples():
        rt, nt=False, ""
        for rate in rates:
            n_rt=apply_rate(rowdat, rate)
            rt=n_rt if n_rt else rt
            if n_rt: nt=list(rate.keys())[list(rate.values()).index(rt)]
        notifiers.append(nt if rt else "N/a")
        all_rates.append(rt if rt else 0)
        
    ndf["rates"]=all_rates
    ndf["notifiers"]=notifiers
    return ndf

def calculate_backpays(fdf):
    fdf["total_allowances"]=fdf.qty*fdf.rates/2
    fdf["total_backpay"]=fdf.qty*(fdf.rates-72.2)

    all_on_calls=[int(sum(fdf.query(q_query).qty)/2) for q_query in q_queries]
    total_on_calls=int(sum(fdf.qty)/2)
    assert sum(all_on_calls)==total_on_calls

    all_allowances=[sum(fdf.query(q_query).total_allowances) for q_query in q_queries]
    total_allowances=sum(fdf.total_allowances)
    assert sum(all_allowances)==total_allowances

    # Calculate total backpay outstanding
    return all_on_calls, all_allowances