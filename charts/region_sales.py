import plotly.express as px

def region_sales_chart(df):

    region_df = df.groupby('Region')['Sales'].sum().reset_index()

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

    fig.update_traces(textposition="outside")

    return fig
