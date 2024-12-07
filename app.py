import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import scipy.stats as stats

# Đọc dữ liệu
df1 = pd.read_csv('weather_data_cleaned_1.csv')
df2 = pd.read_csv('weather_data_cleaned_2.csv')
df3 = pd.read_csv('weather_data_cleaned_3.csv')

# Gộp các DataFrame lại với nhau
df = pd.concat([df1, df2, df3], ignore_index=True)  # Đảm bảo đường dẫn đúng đến file dữ liệu của bạn

# Lấy danh sách tất cả các cột từ DataFrame
all_columns = df.columns.tolist()

# Hàm tính toán số liệu tổng quan
def get_summary_statistics(var1, var2):
    summary = {}
    summary['Total Samples'] = len(df)
    
    # Tính toán các số liệu nếu biến là số
    if df[var1].dtype in ['float64', 'int64']:
        summary['Mean Var1'] = round(df[var1].mean(), 2)
        summary['Variance Var1'] = round(df[var1].var(), 2)
        summary['Std Dev Var1'] = round(df[var1].std(), 2)
        summary['Min Var1'] = round(df[var1].min(), 2)
        summary['Max Var1'] = round(df[var1].max(), 2)
    else:
        summary['Mean Var1'] = None
        summary['Variance Var1'] = None
        summary['Std Dev Var1'] = None
        summary['Min Var1'] = None
        summary['Max Var1'] = None

    if df[var2].dtype in ['float64', 'int64']:
        summary['Mean Var2'] = round(df[var2].mean(), 2)
        summary['Variance Var2'] = round(df[var2].var(), 2)
        summary['Std Dev Var2'] = round(df[var2].std(), 2)
        summary['Min Var2'] = round(df[var2].min(), 2)
        summary['Max Var2'] = round(df[var2].max(), 2)
    else:
        summary['Mean Var2'] = None
        summary['Variance Var2'] = None
        summary['Std Dev Var2'] = None
        summary['Min Var2'] = None
        summary['Max Var2'] = None

    # Xác định loại biến
    summary['Type Var1'] = 'Quantitative' if df[var1].dtype in ['float64', 'int64'] else 'Categorical'
    summary['Type Var2'] = 'Quantitative' if df[var2].dtype in ['float64', 'int64'] else 'Categorical'

    # Tính tương quan Pearson nếu cả 2 biến đều là định lượng
    if df[var1].dtype in ['float64', 'int64'] and df[var2].dtype in ['float64', 'int64']:
        summary['Pearson Correlation'] = round(df[var1].corr(df[var2]), 2)
    else:
        summary['Pearson Correlation'] = None
    
    # Kiểm định Chi-square nếu cả 2 biến đều là phân loại
    if df[var1].dtype == 'object' and df[var2].dtype == 'object':
        contingency_table = pd.crosstab(df[var1], df[var2])
        chi2_stat, p_val, _, _ = stats.chi2_contingency(contingency_table)
        summary['Chi-Square Test'] = f"Chi2 = {chi2_stat:.2f}, p-value = {p_val:.4f}"
    else:
        summary['Chi-Square Test'] = None
    
    # Kiểm định ANOVA nếu 1 biến là định lượng và 1 biến là phân loại
    if df[var1].dtype in ['float64', 'int64'] and df[var2].dtype == 'object':
        groups = [df[df[var2] == category][var1] for category in df[var2].unique()]
        f_stat, p_val = stats.f_oneway(*groups)
        summary['ANOVA Test'] = f"F-stat = {f_stat:.2f}, p-value = {p_val:.4f}"
    else:
        summary['ANOVA Test'] = None
    
    return summary

# Khởi tạo Dash app
app = dash.Dash(__name__)

# Tạo layout cho Dashboard
app.layout = html.Div([
    html.H1("Interactive Data Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Select Variable 1"),
            dcc.Dropdown(
                id='var1-dropdown',
                options=[{'label': col, 'value': col} for col in all_columns],
                value=all_columns[0],  # Giá trị mặc định
                multi=False
            ),
            
            html.Label("Select Variable 2"),
            dcc.Dropdown(
                id='var2-dropdown',
                options=[{'label': col, 'value': col} for col in all_columns],
                value=all_columns[1],  # Giá trị mặc định
                multi=False
            ),
        ], style={'width': '50%', 'padding': '20px', 'marginRight': '20px'}),

        html.Div(id='summary-stats', style={'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '10px', 'width': '40%'}), 
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px', 'padding': '0 20px'}), 

    html.Div([
        html.Div([ 
            dcc.Graph(id='relationship-graph')
        ], style={'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '10px', 'width': '32%'}),
        html.Div([
            dcc.Graph(id='distribution-graph-var1')
        ], style={'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '10px', 'width': '32%'}),
        html.Div([
            dcc.Graph(id='distribution-graph-var2')
        ], style={'padding': '20px', 'border': '1px solid #ccc', 'borderRadius': '10px', 'width': '32%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '30px'})
])

# Callback để cập nhật các biểu đồ và số liệu tổng quan khi thay đổi lựa chọn
@app.callback(
    [Output('relationship-graph', 'figure'),
     Output('distribution-graph-var1', 'figure'),
     Output('distribution-graph-var2', 'figure'),
     Output('summary-stats', 'children')],
    [Input('var1-dropdown', 'value'),
     Input('var2-dropdown', 'value')]
)
def update_dashboard(var1, var2):
    relationship_fig = px.scatter(df, x=var1, y=var2, title=f"Relationship between {var1} and {var2}")
    dist_fig_var1 = px.histogram(df, x=var1, nbins=30, title=f"Distribution of {var1}")
    dist_fig_var2 = px.histogram(df, x=var2, nbins=30, title=f"Distribution of {var2}")
    summary = get_summary_statistics(var1, var2)
    
    # Tạo bảng summary statistics với đường kẻ và tên biến
    summary_stats = html.Table(
    style={
        'border': '1px solid black',  # Đường kẻ bảng ngoài
        'borderCollapse': 'collapse',  # Đảm bảo các đường kẻ được gộp lại
        'width': '100%',  # Chiều rộng 100%
        'textAlign': 'center'
    },
    children=[
        html.Tr([html.Th("Metric", style={'border': '1px solid'}), html.Th(var1, style={'border': '1px solid'}), html.Th(var2, style={'border': '1px solid'})]),
        html.Tr([html.Td("Total Samples", style={'border': '1px solid'}), html.Td(summary['Total Samples'], style={'border': '1px solid'}), html.Td(summary['Total Samples'], style={'border': '1px solid'})]),
        html.Tr([html.Td("Mean", style={'border': '1px solid'}), html.Td(summary['Mean Var1'], style={'border': '1px solid'}), html.Td(summary['Mean Var2'], style={'border': '1px solid'})]),
        html.Tr([html.Td("Variance", style={'border': '1px solid'}), html.Td(summary['Variance Var1'], style={'border': '1px solid'}), html.Td(summary['Variance Var2'], style={'border': '1px solid'})]),
        html.Tr([html.Td("Std Dev", style={'border': '1px solid'}), html.Td(summary['Std Dev Var1'], style={'border': '1px solid'}), html.Td(summary['Std Dev Var2'], style={'border': '1px solid'})]),
        html.Tr([html.Td("Min", style={'border': '1px solid'}), html.Td(summary['Min Var1'], style={'border': '1px solid'}), html.Td(summary['Min Var2'], style={'border': '1px solid'})]),
        html.Tr([html.Td("Max", style={'border': '1px solid'}), html.Td(summary['Max Var1'], style={'border': '1px solid'}), html.Td(summary['Max Var2'], style={'border': '1px solid'})]),
        html.Tr([html.Td("Type", style={'border': '1px solid'}), html.Td(summary['Type Var1'], style={'border': '1px solid'}), html.Td(summary['Type Var2'], style={'border': '1px solid'})]),
        html.Tr([html.Td("Pearson Correlation", style={'border': '1px solid'}), html.Td(summary['Pearson Correlation'], colSpan=2, style={'border': '1px solid'})]),
        html.Tr([html.Td("Chi-Square Test", style={'border': '1px solid'}), html.Td(summary['Chi-Square Test'], colSpan=2, style={'border': '1px solid'})]),
        html.Tr([html.Td("ANOVA Test", style={'border': '1px solid'}), html.Td(summary['ANOVA Test'], colSpan=2, style={'border': '1px solid'})])
    ])
    
    return relationship_fig, dist_fig_var1, dist_fig_var2, summary_stats

# Chạy ứng dụng
if __name__ == '__main__':
    app.run_server(debug=True)
