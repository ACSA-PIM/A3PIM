import numpy as np
from dash import Dash, html, dcc
import pandas as pd
import plotly.express as px

# https://towardsdatascience.com/how-to-create-dynamic-3d-scatter-plots-with-plotly-6371adafd14

x = [i for i in range(0,60)]
y = [i for i in range(0,60)]
z = [i+j for i,j in zip(x,y)]
print(z)
# z[-30:] = z[-30:]*5 + 2
z[-30:] = [x * 5 + 2 for x in z[-30:]]

# # manual cata categories
# categories = "A "*30 + "B "*30
# categories = categories.split(" ")
# categories.pop(60)
# df = pd.DataFrame({
# 'cat':categories, 'col_x':x, 'col_y':y, 'col_z':z
# })
# df.head()

# # 2D
# # fig = px.scatter(df, x='col_x', y='col_y', color='cat',
# #                  width=700, height=500,
# #                  title="2D Scatter Plot")

# fig = px.scatter_3d(df, x='col_x', y='col_y', z='col_z',
#                     color='cat',
#                     title="3D Scatter Plot")

fig = px.scatter_3d(x=x, y=y, z=z,
                    color=z,
                    size=x, size_max=20,
                    title="3D Scatter Plot")

# dash to show
app = Dash(__name__)
# colors = {
#     'background': '#111111',
#     'text': '#7FDBFF'
# }

app.layout = html.Div(children=[
    # html.H1(children='Hello Dash'),

    # html.Div(children='''
    #     Dash: A web application framework for your data.
    # '''),

    dcc.Graph(
        id='example-graph',
        figure=fig,
        style = {'height': '100vh'}
    )
])

# app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
#     html.H1(
#         children='Hello Dash',
#         style={
#             'textAlign': 'center',
#             'color': colors['text']
#         }
#     ),

#     html.Div(children='Dash: A web application framework for your data.', style={
#         'textAlign': 'center',
#         'color': colors['text']
#     }),

#     dcc.Graph(
#         id='example-graph-2',
#         figure=fig,
#         style = {'height': '1000px'}
#     )
# ])

if __name__ == '__main__':
    app.run_server(debug=True)