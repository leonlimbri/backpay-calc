from utils import *
import streamlit as st
import pandas as pd
import json, chardet, io

# Simple streamlit app for backpay calculation
st.set_page_config(page_title="Backpay Calculator", page_icon="🩺")
st.title("On-Call Allowances Backpay Calculator")

# Find how many different rates level needed? Initially has to be 3
df_rate=pd.DataFrame(json.load(open("rates.json")))
df_rate["start_date"]=df_rate.start_date.apply(lambda d: pd.Timestamp(d))
all_cols=["Weekdays", "Saturdays", "Sunday/Weekday PH", "Weekend PH"]

# Rates
with st.expander("On Call Allowances Rates", expanded=True):
    st.write("""
        The following are the rates used for the calculation of the backpay. 
        _Note these rates are editable as follows._
    """)
    current_base_rate=st.number_input(label="Current Allowance Rate", format="%0.2f", value=72.2)
    edited_df_rate=st.data_editor(
        df_rate, 
        column_config={
            col: st.column_config.NumberColumn(
                lab,
                help=f"How much of allowace for {lab.lower()} that you got?",
                min_value=0,
                max_value=5,
                format="$%.2f",
            )
            for col, lab in zip([col for col in df_rate.columns if col!="start_date"], all_cols)
        } | {"start_date": st.column_config.DateColumn("Start Date")},
        num_rows="dynamic"
    )

# File uploader
with st.expander("Uploaded Timesheets", expanded=True):
    files=st.file_uploader(
        label="Upload **all** of the timesheets to be calculated.", 
        type="csv",
        accept_multiple_files=True
    )

# Read files
df_timesheet=pd.DataFrame()
for file in files:
    bytes_data=file.read()
    _df=pd.read_csv(io.BytesIO(bytes_data), encoding=chardet.detect(bytes_data)['encoding'])
    df_timesheet=pd.concat([df_timesheet, _df]).reset_index(drop=True)

# Calculate backpay
if st.button("Calculate"):
    if len(files):
        # Set up the dataframe first
        fdf=pd.DataFrame()
        ts_colnames=["Column1"]

        for i in range(13):
            ncolnames=ts_colnames+[f"tt_label_{i+1}", f"tt_qty_{i+1}"]
            ndf=df_timesheet[ncolnames]
            ndf.columns=ts_colnames+["label", "qty"]
            fdf=pd.concat([fdf, ndf.reset_index(drop=True)])

        # Change data type
        fdf.loc[:,"Column1"]=fdf.Column1.apply(lambda dt: datetime.datetime.strptime(dt, "%d/%m/%Y %I:%M:%S %p").date())

        edited_df_rate["start_date"]=edited_df_rate.start_date.apply(lambda d: d.date())

        # Calculation done here
        fdf=apply_rates(fdf, edited_df_rate.to_dict("records"))
        fdf=fdf.query("label in @on_calls_code")
        all_on_calls, all_allowances=calculate_backpays(fdf)

        total_allowances=sum(all_allowances)
        total_allowances_paid=sum(all_on_calls)*current_base_rate/2
        total_backpays=sum(all_allowances)-total_allowances_paid

        st.header("Below is summary of your Backpay", divider=True)
        st.write(f"Total Allowances for period **{fdf.Column1.min().strftime('%d %b %Y')} - {fdf.Column1.max().strftime('%d %b %Y')}**:")
        for q_notifier, on_call, allowance in zip(q_notifiers, all_on_calls, all_allowances):
            if on_call:
                st.write(
                    "You had ", on_call, f"on calls on **{q_notifier}**", f"which equates to _\${allowance}_", 
                    f", however only paid _\${round(on_call*current_base_rate, 2)}_.",
                    f" **Therefore, expect a backpay of _\${round(allowance-on_call*current_base_rate, 2)}_.**"
                )
        st.subheader(f"**Total Allowances = \${total_allowances}**")
        st.subheader(f"**Total Backpays = \${total_backpays}**")
    else:
        st.caption("No files supplied...")