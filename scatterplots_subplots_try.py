from plotly import tools
import plotly.offline as pyo
import plotly.graph_objs as go

trace1 = go.Scatter(x=[1, 2, 3],
                    y=[4, 5, 6],
                    hoverinfo='text',
                    text=
                        'Here is the displayed info when hover on the figure',
                    mode = 'markers',
                    opacity=1,
                    marker={
                        'size':5,
                        'line':{'width': 0.8}
                            },
                    name='name of this scatter pts'
                    )

trace1 = go.Scatter(x=[10, 20, 30,40,50],
                    y=[43, 54, 60,71,38],
                    hoverinfo='text',
                    text=
                        'Here is the displayed info when hover on the figure',
                    mode = 'markers',
                    opacity=1,
                    marker={
                        'size':5,
                        'line':{'width': 0.8}
                            },
                    name='name of this scatter pts'
                    )

trace2 = go.Scatter(x=[20,50,80,120,130],
                    y=[40,50,60,90,70],
                    hoverinfo='text',
                    text=
                        'Here is the displayed info when hover on the figure',
                    mode = 'markers+lines',
                    opacity=1,
                    marker={
                        'size':5,
                        'line':{'width': 0.8}
                            },
                    name='name of this scatter pts'
                    )

trace3 = go.Scatter(x=[12,3,4,1,2,1,-2],
                    y=[80,30,20,65,42,67],
                    hoverinfo='text',
                    text=
                        'Here is the displayed info when hover on the figure',
                    mode = 'markers',
                    opacity=1,
                    marker={
                        'size':5,
                        'line':{'width': 0.8}
                            },
                    name='name of this scatter pts'
                    )

trace4 = go.Scatter(x=[1, 2, 3],
                    y=[4, 5, 6],
                    hoverinfo='text',
                    text=
                        'Here is the displayed info when hover on the figure',
                    mode = 'markers',
                    opacity=1,
                    marker={
                        'size':5,
                        'line':{'width': 0.8}
                            },
                    name='name of this scatter pts'
                    )



fig = tools.make_subplots(rows=2,
                          cols=2,
                          subplot_titles=(
                                'Plot 1', 'Plot 2',
                                'Plot 3', 'Plot 4'))

fig.append_trace(trace1, 1, 1)
fig.append_trace(trace2, 1, 2)
fig.append_trace(trace3, 2, 1)
fig.append_trace(trace4, 2, 2)

fig['layout'].update(height=700, width=750, title='Multiple Subplots' +
                                                  ' with Titles')

pyo.plot(fig, filename='make-subplots-multiple-with-titles.html')
