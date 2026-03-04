import plotly.express as px

def region_sales_chart(filtered_df):

    region_df = (
        filtered_df.groupby("Region")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )

    fig = px.bar(
        region_df,
        x="Region",
        y="Sales",
        color="Sales",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        title="Sales by Region",
        title_x=0.3
    )

    fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')

    return fig
