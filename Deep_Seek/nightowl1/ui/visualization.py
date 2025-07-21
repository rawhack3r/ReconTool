import plotly.graph_objects as go
from networkx.drawing.nx_agraph import graphviz_layout

def create_3d_graph(correlation_graph):
    pos = graphviz_layout(correlation_graph, prog='neato', dim=3)
    
    edge_x, edge_y, edge_z = [], [], []
    for edge in correlation_graph.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
    
    node_x, node_y, node_z = [], [], []
    for node in correlation_graph.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
    
    fig = go.Figure(
        data=[
            go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(width=0.5, color='#888')),
            go.Scatter3d(x=node_x, y=node_y, z=node_z, mode='markers', marker=dict(
                size=5,
                color=[correlation_graph.nodes[n].get('risk', 0) for n in correlation_graph.nodes()],
                colorscale='Hot',
                opacity=0.8
            ))
        ],
        layout=go.Layout(
            scene=dict(aspectmode="cube"),
            margin=dict(t=0, b=0, l=0, r=0)
        )
    )
    return fig