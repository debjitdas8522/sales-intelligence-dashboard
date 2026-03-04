import plotly.express as px

def monthly_sales_chart(filtered_df):
    
    monthly_sales = (
        filtered_df
        .set_index('Order Date')
        .resample('M')['Sales']
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly_sales,
        x="Order Date",
        y="Sales",
        markers=True
    )

    fig.update_layout(
        template="plotly_dark",
        title="Sales Trend Over Time",
        title_x=0.3,
        xaxis_title="Month",
        yaxis_title="Sales"
    )

    return fig
