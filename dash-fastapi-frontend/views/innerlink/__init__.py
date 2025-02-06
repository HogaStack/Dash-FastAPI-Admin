from dash import html
import feffery_utils_components as fuc
from callbacks import innnerlink_c  # noqa: F401


def render(*args, **kwargs):
    return [
        html.Div(
            [
                fuc.FefferyTimeout(id='init-iframe-timeout', delay=500),
                fuc.FefferyStyle(
                    rawStyle="""
                    iframe {
                        border: none;
                        width: 100%;
                        height: 100%;
                        display: block
                    }
                    """
                ),
                html.Iframe(
                    id='innerlink-iframe',
                ),
            ],
            id='innerlink-container',
            style={'position': 'relative', 'height': 'calc(100vh - 120px)'},
        )
    ]
