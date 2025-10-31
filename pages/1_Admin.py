import streamlit as st
from utils.supabase_client import supabase
st.title("Admin Dashboard")
if st.session_state.get('user', {}).get('role') != 'admin':
    st.error("Admin only")
    st.stop()

users = supabase.table('profiles').select('id, display_name, email, role, created_at').execute().data
st.dataframe(users)

# uploads per day
rows = supabase.table('resumes').select('id, user_id, created_at').execute().data
# convert to dataframe and plot counts per day (use pandas)
import pandas as pd
df = pd.DataFrame(rows)
df['date'] = pd.to_datetime(df['created_at']).dt.date
st.bar_chart(df['date'].value_counts().sort_index())
