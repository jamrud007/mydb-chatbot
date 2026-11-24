"""
Chart Factory
Creates various chart types using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class ChartFactory:
    """Factory for creating various chart types"""
    
    @staticmethod
    def create_chart(chart_type: str, data: List[Dict], config: Dict) -> Optional[go.Figure]:
        """
        Create a chart based on type and configuration
        
        Args:
            chart_type: Type of chart ('bar', 'line', 'pie', etc.)
            data: Query results data
            config: Chart configuration
            
        Returns:
            Plotly Figure or None
        """
        if not data:
            return ChartFactory._create_empty_chart("No data available")
        
        try:
            df = pd.DataFrame(data)
            
            if chart_type == 'bar':
                return ChartFactory._create_bar_chart(df, config)
            elif chart_type == 'line':
                return ChartFactory._create_line_chart(df, config)
            elif chart_type == 'pie':
                return ChartFactory._create_pie_chart(df, config)
            elif chart_type == 'scatter':
                return ChartFactory._create_scatter_chart(df, config)
            elif chart_type == 'pareto':
                return ChartFactory._create_pareto_chart(df, config)
            elif chart_type == 'heatmap':
                return ChartFactory._create_heatmap(df, config)
            elif chart_type == 'gauge':
                return ChartFactory._create_gauge_chart(df, config)
            elif chart_type == 'area':
                return ChartFactory._create_area_chart(df, config)
            elif chart_type == 'histogram':
                return ChartFactory._create_histogram(df, config)
            elif chart_type == 'box':
                return ChartFactory._create_box_plot(df, config)
            else:
                return ChartFactory._create_empty_chart(f"Unsupported chart type: {chart_type}")
        
        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {e}")
            return ChartFactory._create_empty_chart(f"Error: {str(e)}")
    
    @staticmethod
    def _create_bar_chart(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create bar chart"""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        orientation = config.get('orientation', 'v')
        top_n = config.get('top_n')
        sort_desc = config.get('sort_desc', True)
        
        if not x_col or not y_col:
            return ChartFactory._create_empty_chart("Missing x or y column")

        # Ensure numeric for sorting/plotting
        plot_df = df.copy()
        plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce').fillna(0)

        if sort_desc is not None:
            plot_df = plot_df.sort_values(by=y_col, ascending=not sort_desc)

        if top_n and isinstance(top_n, int) and top_n > 0:
            plot_df = plot_df.head(top_n)

        fig = go.Figure(data=[
            go.Bar(
                x=plot_df[x_col] if orientation != 'h' else plot_df[y_col],
                y=plot_df[y_col] if orientation != 'h' else plot_df[x_col],
                marker_color=config.get('color', '#3b82f6'),
                orientation=orientation
            )
        ])
        
        fig.update_layout(
            title=config.get('title', 'Bar Chart'),
            xaxis_title=x_col if orientation != 'h' else y_col,
            yaxis_title=y_col if orientation != 'h' else x_col,
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    @staticmethod
    def _create_line_chart(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create line chart"""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        
        if not y_col:
            return ChartFactory._create_empty_chart("Missing y column")
        
        # Use index if no x_column
        if not x_col:
            x_data = df.index
            x_title = 'Index'
        else:
            x_data = df[x_col]
            x_title = x_col
        
        fig = go.Figure(data=[
            go.Scatter(
                x=x_data,
                y=df[y_col],
                mode='lines+markers',
                line=dict(color=config.get('color', '#3b82f6'), width=2),
                marker=dict(size=6)
            )
        ])
        
        fig.update_layout(
            title=config.get('title', 'Line Chart'),
            xaxis_title=x_title,
            yaxis_title=y_col,
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    @staticmethod
    def _create_pie_chart(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create pie chart"""
        labels_col = config.get('labels_column')
        values_col = config.get('values_column')
        top_n = config.get('top_n')
        group_other = config.get('group_other', False)
        other_label = config.get('other_label', 'OTHER')
        
        if not labels_col or not values_col:
            return ChartFactory._create_empty_chart("Missing labels or values column")

        plot_df = df.copy()
        plot_df[values_col] = pd.to_numeric(plot_df[values_col], errors='coerce').fillna(0)
        plot_df = plot_df.groupby(labels_col, as_index=False)[values_col].sum()
        plot_df = plot_df.sort_values(by=values_col, ascending=False)

        if top_n and isinstance(top_n, int) and top_n > 0 and len(plot_df) > top_n:
            if group_other:
                top_df = plot_df.head(top_n).copy()
                other_value = plot_df.iloc[top_n:][values_col].sum()
                if other_value > 0:
                    top_df.loc[len(top_df)] = {labels_col: other_label, values_col: other_value}
                plot_df = top_df
            else:
                plot_df = plot_df.head(top_n)

        fig = go.Figure(data=[
            go.Pie(
                labels=plot_df[labels_col],
                values=plot_df[values_col],
                hole=0.3  # Donut chart
            )
        ])
        
        fig.update_layout(
            title=config.get('title', 'Pie Chart'),
            template='plotly_dark',
            height=400
        )
        
        return fig

    @staticmethod
    def _create_pareto_chart(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create Pareto chart (bar + cumulative percentage line)."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        top_n = config.get('top_n', 15)
        sort_desc = config.get('sort_desc', True)

        if not x_col or not y_col:
            return ChartFactory._create_empty_chart("Missing x or y column")

        plot_df = df.copy()
        plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce').fillna(0)
        plot_df = plot_df.groupby(x_col, as_index=False)[y_col].sum()
        plot_df = plot_df.sort_values(by=y_col, ascending=not sort_desc)
        if top_n and isinstance(top_n, int) and top_n > 0:
            plot_df = plot_df.head(top_n)

        total = plot_df[y_col].sum()
        if total <= 0:
            return ChartFactory._create_empty_chart("No positive values for Pareto chart")

        plot_df['cumulative_pct'] = (plot_df[y_col].cumsum() / total) * 100

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=plot_df[x_col],
                y=plot_df[y_col],
                name=y_col,
                marker_color='#3b82f6'
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=plot_df[x_col],
                y=plot_df['cumulative_pct'],
                name='Cumulative %',
                mode='lines+markers',
                line=dict(color='#f59e0b', width=2),
                marker=dict(size=6)
            ),
            secondary_y=True
        )

        fig.update_yaxes(title_text=y_col, secondary_y=False)
        fig.update_yaxes(title_text='Cumulative %', range=[0, 105], secondary_y=True)
        fig.update_layout(
            title=config.get('title', 'Pareto Chart'),
            xaxis_title=x_col,
            template='plotly_dark',
            height=450
        )
        return fig
    
    @staticmethod
    def _create_scatter_chart(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create scatter plot"""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        
        if not x_col or not y_col:
            return ChartFactory._create_empty_chart("Missing x or y column")
        
        fig = go.Figure(data=[
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=dict(
                    size=10,
                    color=config.get('color', '#3b82f6'),
                    opacity=0.7
                )
            )
        ])
        
        fig.update_layout(
            title=config.get('title', 'Scatter Plot'),
            xaxis_title=x_col,
            yaxis_title=y_col,
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    @staticmethod
    def _create_heatmap(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create heatmap"""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        value_col = config.get('value_column')
        
        if not x_col or not y_col or not value_col:
            return ChartFactory._create_empty_chart("Missing required columns for heatmap")
        
        # Pivot data for heatmap
        try:
            pivot_df = df.pivot_table(
                index=y_col,
                columns=x_col,
                values=value_col,
                aggfunc='sum'
            )
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale='Viridis',
                text=pivot_df.values,
                texttemplate='%{text:.2f}',
                textfont={"size": 10}
            ))
            
            fig.update_layout(
                title=config.get('title', 'Heatmap'),
                xaxis_title=x_col,
                yaxis_title=y_col,
                template='plotly_dark',
                height=500
            )
            
            return fig
        except Exception as e:
            return ChartFactory._create_empty_chart(f"Heatmap error: {str(e)}")
    
    @staticmethod
    def _create_gauge_chart(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create gauge chart (single metric)"""
        value_col = config.get('value_column')
        
        if not value_col:
            return ChartFactory._create_empty_chart("Missing value column")
        
        # Take first value or sum
        value = df[value_col].iloc[0] if len(df) == 1 else df[value_col].sum()
        max_value = config.get('max_value', value * 1.5)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': config.get('title', 'Gauge')},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "lightgray"},
                    {'range': [max_value * 0.5, max_value * 0.75], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=300
        )
        
        return fig
    
    @staticmethod
    def _create_area_chart(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create area chart (filled line chart)"""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        
        if not y_col:
            return ChartFactory._create_empty_chart("Missing y column")
        
        if not x_col:
            x_data = df.index
            x_title = 'Index'
        else:
            x_data = df[x_col]
            x_title = x_col
        
        fig = go.Figure(data=[
            go.Scatter(
                x=x_data,
                y=df[y_col],
                fill='tozeroy',
                mode='lines',
                line=dict(color='#3b82f6', width=2)
            )
        ])
        
        fig.update_layout(
            title=config.get('title', 'Area Chart'),
            xaxis_title=x_title,
            yaxis_title=y_col,
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    @staticmethod
    def _create_histogram(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create histogram"""
        value_col = config.get('value_column')
        
        if not value_col:
            return ChartFactory._create_empty_chart("Missing value column")
        
        fig = go.Figure(data=[
            go.Histogram(
                x=df[value_col],
                marker_color='#3b82f6',
                nbinsx=config.get('bins', 20)
            )
        ])
        
        fig.update_layout(
            title=config.get('title', 'Histogram'),
            xaxis_title=value_col,
            yaxis_title='Frequency',
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    @staticmethod
    def _create_box_plot(df: pd.DataFrame, config: Dict) -> go.Figure:
        """Create box plot"""
        value_col = config.get('value_column')
        group_col = config.get('group_column')
        
        if not value_col:
            return ChartFactory._create_empty_chart("Missing value column")
        
        if group_col:
            # Grouped box plot
            fig = go.Figure()
            for group in df[group_col].unique():
                group_data = df[df[group_col] == group][value_col]
                fig.add_trace(go.Box(
                    y=group_data,
                    name=str(group),
                    boxmean='sd'
                ))
        else:
            # Single box plot
            fig = go.Figure(data=[
                go.Box(
                    y=df[value_col],
                    boxmean='sd',
                    marker_color='#3b82f6'
                )
            ])
        
        fig.update_layout(
            title=config.get('title', 'Box Plot'),
            yaxis_title=value_col,
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    @staticmethod
    def _create_empty_chart(message: str) -> go.Figure:
        """Create empty/error chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="white")
        )
        fig.update_layout(
            template='plotly_dark',
            height=300,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig
