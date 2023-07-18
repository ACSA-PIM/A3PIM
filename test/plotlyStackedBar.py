import plotly.graph_objects as go
import plotly.express as px
x = [
    ["bc", "bc", "bc", "sssp", "sssp", "sssp"],
    ["CPU-ONLY", "PIM_ONLY", "PIMProf", "CPU-ONLY", "PIM_ONLY", "PIMProf",]
]
fig = go.Figure()

fig.add_bar(x=x,y=[10,2,3,4,5,6], name="CPU")
fig.add_bar(x=x,y=[6,5,4,3,2,1], name="DataMove")
fig.add_bar(x=x,y=[6,5,4,3,2,1], name="PIM")
fig.update_layout(barmode="relative", 
				title="Execution time breakdown of GAP and PrIM workloads using different offloading decisions",
				xaxis_title="GAP and PrIM workloads",
				yaxis_title="Normalized Execution Time",
    			yaxis_range=[0,25],
				legend_title="Legend Title",
				font=dict(
					family="serif",
					size=12,
					color="Black"
				),
				height=600, width=800, # 图片的长宽
				template = "plotly_white", # https://plotly.com/python/templates/
				margin=dict(b=60, t=20, l=200, r=200))
fig.write_image("./test.png")