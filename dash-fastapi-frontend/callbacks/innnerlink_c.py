from dash.dependencies import Input, Output, State
from server import app


app.clientside_callback(
    """
    (_, current_item) => {
        if (current_item?.props?.modules === 'innerlink') {
            return current_item?.props?.link;
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    Output('innerlink-iframe', 'src'),
    Input('init-iframe-timeout', 'timeoutCount'),
    State('index-side-menu', 'currentItem'),
)
