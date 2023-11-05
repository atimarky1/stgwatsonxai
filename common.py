import streamlit as st

BACKGROUND_COLOR = 'white'
COLOR = 'black'

def set_page_container_style(
        max_width: int = 1100, max_width_100_percent: bool = False,
        padding_top: int = 1, padding_right: int = 10, padding_left: int = 1, padding_bottom: int = 10,
        color: str = COLOR, background_color: str = BACKGROUND_COLOR,
    ):
        if max_width_100_percent:
            max_width_str = f'max-width: 100%;'
        else:
            max_width_str = f'max-width: {max_width}px;'
        st.markdown(
            f'''
            <style>
                .st-emotion-cache-18ni7ap {{
                    z-index: 1;
                }}
                .st-emotion-cache-uf99v8 {{
                    overflow: auto;
                }}
                .st-emotion-cache-z5fcl4 {{
                    {max_width_str}
                    padding-top: 1.5rem;
                    padding-right: 2rem;
                    padding-left: 2rem;
                    padding-bottom: 5rem;
                }}
                .reportview-container .main {{
                    color: {color};
                    background-color: {background_color};
                }}
            </style>
            ''',
            unsafe_allow_html=True,
        )
