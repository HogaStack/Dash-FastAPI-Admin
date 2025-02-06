from dash.dependencies import ClientsideFunction, Input, Output, State
from server import app


# 初始化echarts图表数据
app.clientside_callback(
    """
    (n_intervals, data) => {
        return data;
    }
    """,
    Output('echarts-data-container', 'data'),
    Input('init-echarts-timeout', 'timeoutCount'),
    State('init-echarts-data-container', 'data'),
    prevent_initial_call=True,
)


# 渲染命令统计图表
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_command_stats',
        function_name='render_command_stats_chart',
    ),
    Output('command-stats-charts-container', 'children'),
    Input('echarts-data-container', 'data'),
)


# 渲染内存信息统计图表
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_memory', function_name='render_memory_chart'
    ),
    Output('memory-charts-container', 'children'),
    Input('echarts-data-container', 'data'),
)
