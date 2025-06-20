import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Mental Health Dashboard", layout="wide")

# ─── Data used ───────────────────────────────────────────────────────────
@st.cache_data
def load_mh_data():
    df = pd.read_csv('dataset_mh_disorders_v2.csv')
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r'[ /-]+', '_', regex=True)
    )
    return df

@st.cache_data
def load_facilities_data():
    df = pd.read_csv('nb_of_facilities.csv')
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r'[ /-]+', '_', regex=True)
    )
    if 'nb_of_users_per_100000' in df.columns:
        df = df.rename(columns={'nb_of_users_per_100000':'users_per_100k'})
    return df

@st.cache_data
def load_hr_data():
    df = pd.read_csv('nb_of_hr.csv')
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r'[ /-]+', '_', regex=True)
    )
    if 'position' in df.columns and 'nb_staff_per_100000' in df.columns:
        df = df.rename(columns={'position':'profession', 'nb_staff_per_100000':'workers_per_100k'})
    return df

@st.cache_data
def load_suicide_data():
    df = pd.read_csv('increased_suicide_risk_by_MH_disorder.csv')
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r'[ /-]+', '_', regex=True)
    )
    df = df.rename(columns={df.columns[0]:'disorder', df.columns[1]:'or'})
    return df

@st.cache_data
def load_risk_factors():
    df = pd.read_csv('risk_factors.csv')
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r'[ /-]+', '_', regex=True)
    )
    return df.rename(columns={
        'val':'ylds_rate_per_100k',
        'upper':'ci_upper',
        'lower':'ci_lower',
        'risk':'risk_factor'
    })


def main():
    st.title("Mental Health Disorders Dashboard")

    # Load data
    mh_df       = load_mh_data()
    fac_df      = load_facilities_data()
    hr_df       = load_hr_data()
    risk_df     = load_suicide_data()
    rfactors_df = load_risk_factors()

    # Sidebar filters
    causes   = mh_df['cause'].unique().tolist()
    sexes    = mh_df['sex'].unique().tolist()
    ages     = mh_df['age'].unique().tolist()
    min_year, max_year = int(mh_df['year'].min()), int(mh_df['year'].max())

    st.sidebar.header("Filters — MH Metrics")
    sel_causes = st.sidebar.multiselect("Disorder", causes, default=["Anxiety disorders"], key="sel_causes")
    sel_sexes  = st.sidebar.multiselect("Sex", sexes, default=["Female","Male"], key="sel_sexes")
    sel_ages   = st.sidebar.multiselect("Age Group", ages, default=["All ages"], key="sel_ages")
    sel_years  = st.sidebar.slider("Year Range", min_year, max_year, (min_year, max_year), key="sel_years")

    st.sidebar.markdown("---")
    st.sidebar.header("Filters — Risk Factors")
    sel_rf_causes = st.sidebar.multiselect(
        "Disorder", rfactors_df['cause'].unique().tolist(),
        default=["Anxiety disorders"], key="sel_rf_causes"
    )
    sel_rfactors = st.sidebar.multiselect(
        "Risk Factor", rfactors_df['risk_factor'].unique().tolist(),
        default=["Behavioral risks"], key="sel_rfactors"
    )
    sel_rf_sex = st.sidebar.multiselect("Sex", sexes, default=["Female","Male"], key="sel_rf_sex")

    # KPIs for latest year
    latest = mh_df.query(
        "country=='Lebanon' & year==@max_year & cause in @sel_causes & sex in @sel_sexes & age in @sel_ages"
    )
    if len(latest) == 1:
        val_prev, val_inc, val_ylds = latest[['prevalence_rate','incidence_rate','ylds_rate']].iloc[0]
    else:
        val_prev = latest.prevalence_rate.mean()
        val_inc  = latest.incidence_rate.mean()
        val_ylds = latest.ylds_rate.mean()

    total_workers = hr_df['workers_per_100k'].sum()
    outp_rate     = fac_df.query("facility_type=='Outpatient'")['users_per_100k'].squeeze()
    inp_rate      = fac_df.query("facility_type=='Mental Hospitals'")['users_per_100k'].squeeze()

    st.subheader("Key Indicators")
    _, m1, m2, m3, m4, m5, m6, _ = st.columns([1,3,3,3,3,3,3,1])
    with m1:
        st.markdown(
            f"<div style='font-size:0.9em; font-weight:600;'>Prevalence (2021, per 100k)</div>"
            f"<div style='font-size:2.0em; font-weight:700; margin-top:4px;'>{val_prev:.1f}</div>",
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"<div style='font-size:0.9em; font-weight:600;'>Incidence (2021, per 100k)</div>"
            f"<div style='font-size:2.0em; font-weight:700; margin-top:4px;'>{val_inc:.1f}</div>",
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"<div style='font-size:0.9em; font-weight:600;'>YLDs (2021, per 100k)</div>"
            f"<div style='font-size:2.0em; font-weight:700; margin-top:4px;'>{val_ylds:.1f}</div>",
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"<div style='font-size:0.9em; font-weight:600;'>HC Workers (2015, per 100k)</div>"
            f"<div style='font-size:2.0em; font-weight:700; margin-top:4px;'>{total_workers:.1f}</div>",
            unsafe_allow_html=True
        )
    with m5:
        st.markdown(
            f"<div style='font-size:0.9em; font-weight:600;'>Outpatients (2015, per 100k)</div>"
            f"<div style='font-size:2.0em; font-weight:700; margin-top:4px;'>{outp_rate:.1f}</div>",
            unsafe_allow_html=True
        )
    with m6:
        st.markdown(
            f"<div style='font-size:0.9em; font-weight:600;'>Inpatients (2015, per 100k)</div>"
            f"<div style='font-size:2.0em; font-weight:700; margin-top:4px;'>{inp_rate:.1f}</div>",
            unsafe_allow_html=True
        )

    # Row 1 chart
    metric_map = {
        "Prevalence Rate": "prevalence_rate",
        "Incidence Rate":  "incidence_rate",
        "YLDs Rate":       "ylds_rate"
    }
    metric_choice = st.selectbox("Choose metric", list(metric_map.keys()), key="main_metric")
    disorder_text1 = ", ".join(sel_causes)
    st.markdown(f"#### {metric_choice} per 100k for **{disorder_text1}** — Global vs Lebanon", unsafe_allow_html=True)

    df_plot = (
        mh_df[
            mh_df['country'].isin(['Lebanon','Global']) &
            mh_df['cause'].isin(sel_causes) &
            mh_df['sex'].isin(sel_sexes) &
            mh_df['age'].isin(sel_ages) &
            mh_df['year'].between(sel_years[0], sel_years[1])
        ]
        .assign(Legend=lambda d: d['country'] + " | " + d['sex'] + " | " + d['age'])
    )
    bar = alt.Chart(df_plot).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        xOffset=alt.XOffset('country:N'),
        y=alt.Y(f"{metric_map[metric_choice]}:Q", title=f"{metric_choice} per 100k"),
        color='Legend:N',
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('Legend:N', title='Country | Sex | Age'),
            alt.Tooltip(f"{metric_map[metric_choice]}:Q", title=metric_choice, format=".1f")
        ]
    ).properties(height=350)
    st.altair_chart(bar, use_container_width=True)

    # Row 2 chart
    col1, col2, col3 = st.columns([2,2,3])
    with col1:
        st.markdown("<h4 style='text-align:center;'>Suicide Ideation Risk by Disorder (2014)</h4>", unsafe_allow_html=True)
        max_upper = risk_df['ci_higher'].max() * 1.1
        interval = (
            alt.Chart(risk_df).mark_bar(color='#ddd', size=16)
            .encode(
                y=alt.Y('disorder:N', sort=alt.EncodingSortField('or', order='descending'), title=''),
                x=alt.X('ci_lower:Q', title="Risk increase by number of folds (x)", scale=alt.Scale(domain=[0, max_upper])),
                x2='ci_higher'
            )
        )
        median = alt.Chart(risk_df).mark_tick(color='red', size=20, thickness=2).encode(y='disorder:N', x='or:Q')
        st.altair_chart((interval + median).properties(height=250), use_container_width=True)

    with col2:
        st.markdown(
            "<h4 style='text-align:center;'>HC Workers per 100k by Profession (2015)</h4>",
            unsafe_allow_html=True
        )
        hr_display = (
            hr_df[['profession','workers_per_100k']]
            .dropna()
            .rename(columns={'profession':'Profession','workers_per_100k':'Workers per 100k'})
            .reset_index(drop=True)
        )
        styled_hr = hr_display.style.hide(axis='index').format({'Workers per 100k':'{:.2f}'})
        st.dataframe(styled_hr, height=280)

    with col3:
        disorder_text2 = ", ".join(sel_rf_causes)
        st.markdown(
            f"<h4 style='text-align:center;'>YLD Rate by Age & Risk Factor for {disorder_text2} (2021)</h4>",
            unsafe_allow_html=True
        )
        rf = (
            rfactors_df[
                rfactors_df['cause'].isin(sel_rf_causes) &
                rfactors_df['risk_factor'].isin(sel_rfactors) &
                rfactors_df['sex'].isin(sel_rf_sex)
            ]
            .assign(Legend=lambda d: d['risk_factor'] + " | " + d['sex'])
        )
        bar_rf = alt.Chart(rf).mark_bar().encode(
            x=alt.X('age:N', title='Age Group'),
            y=alt.Y('ylds_rate_per_100k:Q', title='YLD per 100k'),
            color='Legend:N'
        ).properties(height=350)
        st.altair_chart(bar_rf, use_container_width=True)

    # Footer
    st.markdown(
        "<div style='text-align:center; padding:8px; font-size:1.2em; color:#555;'>"
        "Data sources: GBD (2021) & WHO (2015) | Dashboard by Karim Samman"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
