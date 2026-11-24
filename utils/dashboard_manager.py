"""
Dashboard Manager
Manages dashboard layouts, configurations, and templates
"""
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DashboardManager:
    """Manages dashboard configurations and templates"""
    
    def __init__(self):
        """Initialize dashboard manager"""
        self.current_dashboard = None
    
    def create_dashboard(self, title: str = "New Dashboard") -> Dict:
        """
        Create a new empty dashboard
        
        Args:
            title: Dashboard title
            
        Returns:
            Dashboard configuration dict
        """
        return {
            'id': self._generate_id(),
            'title': title,
            'created_at': datetime.now().isoformat(),
            'layout': {
                'type': 'grid',  # 'grid' or 'flex'
                'columns': 2,
                'rows': 2
            },
            'charts': [],
            'metrics': []
        }
    
    def add_chart(self, dashboard: Dict, chart_config: Dict, position: Optional[Dict] = None) -> Dict:
        """
        Add a chart to dashboard
        
        Args:
            dashboard: Dashboard configuration
            chart_config: Chart configuration
            position: Optional position {'row': 0, 'col': 0}
            
        Returns:
            Updated dashboard
        """
        chart = {
            'id': self._generate_id(),
            'type': chart_config['type'],
            'title': chart_config.get('title', 'Untitled Chart'),
            'data_config': chart_config.get('data_config', {}),
            'position': position or self._find_next_position(dashboard),
            'size': chart_config.get('size', {'width': 1, 'height': 1})
        }
        
        dashboard['charts'].append(chart)
        return dashboard
    
    def remove_chart(self, dashboard: Dict, chart_id: str) -> Dict:
        """Remove a chart from dashboard"""
        dashboard['charts'] = [
            c for c in dashboard['charts'] if c['id'] != chart_id
        ]
        return dashboard
    
    def move_chart(self, dashboard: Dict, chart_id: str, new_position: Dict) -> Dict:
        """
        Move a chart to new position
        
        Args:
            dashboard: Dashboard configuration
            chart_id: Chart ID to move
            new_position: New position {'row': 0, 'col': 1}
        """
        for chart in dashboard['charts']:
            if chart['id'] == chart_id:
                chart['position'] = new_position
                break
        return dashboard
    
    def add_metric(self, dashboard: Dict, metric: Dict) -> Dict:
        """
        Add a metric card to dashboard
        
        Args:
            metric: {'label': 'Total Sales', 'value': 1000000, 'format': 'currency'}
        """
        dashboard['metrics'].append(metric)
        return dashboard
    
    def get_chart_options(self, results: List[Dict], columns: List[str]) -> List[Dict]:
        """
        Analyze data and suggest available chart types
        
        Args:
            results: Query results
            columns: Column names
            
        Returns:
            List of available chart configurations
        """
        if not results or not columns:
            return []
        
        options = []

        # Analyze column types
        numeric_cols = self._get_numeric_columns(results, columns)
        category_cols = self._get_category_columns(results, columns)
        time_cols = [c for c in category_cols if self._is_time_column(c)]

        # Strong default path: categorical distribution dashboards
        if category_cols and numeric_cols:
            primary_cat = category_cols[0]
            primary_num = numeric_cols[0]

            # 1) Horizontal Top-N bar for readability on long labels/cardinality
            options.append({
                'type': 'bar',
                'title': f'Top 10 {primary_cat} by {primary_num}',
                'data_config': {
                    'x_column': primary_cat,
                    'y_column': primary_num,
                    'orientation': 'h',
                    'top_n': 10,
                    'sort_desc': True
                },
                'icon': '📊'
            })

            # 2) Pareto: bar + cumulative % (best for skewed distributions)
            options.append({
                'type': 'pareto',
                'title': f'Pareto {primary_num} by {primary_cat}',
                'data_config': {
                    'x_column': primary_cat,
                    'y_column': primary_num,
                    'top_n': 15,
                    'sort_desc': True
                },
                'icon': '📈'
            })

            # 3) Pie only for concise view: Top 5 + OTHER
            options.append({
                'type': 'pie',
                'title': f'{primary_num} share by {primary_cat} (Top 5 + OTHER)',
                'data_config': {
                    'labels_column': primary_cat,
                    'values_column': primary_num,
                    'top_n': 5,
                    'group_other': True,
                    'other_label': 'OTHER'
                },
                'icon': '🥧'
            })

            # 4) Extra bar for 2nd metric if available
            if len(numeric_cols) > 1:
                options.append({
                    'type': 'bar',
                    'title': f'Top 10 {primary_cat} by {numeric_cols[1]}',
                    'data_config': {
                        'x_column': primary_cat,
                        'y_column': numeric_cols[1],
                        'orientation': 'h',
                        'top_n': 10,
                        'sort_desc': True
                    },
                    'icon': '📊'
                })

        # Line chart only when there is an explicit time-like dimension
        if time_cols and numeric_cols:
            options.append({
                'type': 'line',
                'title': f'{numeric_cols[0]} Trend',
                'data_config': {
                    'x_column': time_cols[0],
                    'y_column': numeric_cols[0]
                },
                'icon': '📈'
            })

        # Scatter Plot - only if at least 2 numeric columns
        if len(numeric_cols) >= 2:
            options.append({
                'type': 'scatter',
                'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
                'data_config': {
                    'x_column': numeric_cols[0],
                    'y_column': numeric_cols[1]
                },
                'icon': '⚫'
            })

        # Heatmap - requires 2 categories + 1 numeric
        if len(category_cols) >= 2 and numeric_cols:
            options.append({
                'type': 'heatmap',
                'title': f'{category_cols[0]} × {category_cols[1]} Heatmap',
                'data_config': {
                    'x_column': category_cols[0],
                    'y_column': category_cols[1],
                    'value_column': numeric_cols[0]
                },
                'icon': '🔥'
            })

        return options
    
    def get_metrics(self, results: List[Dict], columns: List[str]) -> List[Dict]:
        """
        Calculate summary metrics from data
        
        Returns:
            List of metrics: [{'label': 'Total', 'value': 100, 'format': 'number'}]
        """
        if not results:
            return []
        
        metrics = []
        numeric_cols = self._get_numeric_columns(results, columns)
        
        # Rows returned (from current query result, often limited by API)
        metrics.append({
            'label': 'Rows Returned',
            'value': len(results),
            'format': 'number'
        })
        
        # Sum of numeric columns
        for col in numeric_cols[:3]:  # Limit to 3
            try:
                total = sum(float(row.get(col, 0) or 0) for row in results)
                metrics.append({
                    'label': f'Total {col}',
                    'value': total,
                    'format': 'number'
                })
            except Exception:
                pass

        # Distribution summary when data is category + metric
        category_cols = self._get_category_columns(results, columns)
        if category_cols and numeric_cols:
            cat = category_cols[0]
            metric = numeric_cols[0]
            try:
                sorted_rows = sorted(
                    results,
                    key=lambda r: float(r.get(metric, 0) or 0),
                    reverse=True
                )
                total_metric = sum(float(r.get(metric, 0) or 0) for r in sorted_rows)
                top3_metric = sum(float(r.get(metric, 0) or 0) for r in sorted_rows[:3])
                top3_share = (top3_metric / total_metric * 100) if total_metric > 0 else 0

                metrics.append({
                    'label': 'Top 3 Share (%)',
                    'value': round(top3_share, 2),
                    'format': 'number'
                })
                metrics.append({
                    'label': f'Unique {cat}',
                    'value': len({str(r.get(cat)) for r in results}),
                    'format': 'number'
                })
            except Exception:
                pass
        
        return metrics
    
    def _get_numeric_columns(self, results: List[Dict], columns: List[str]) -> List[str]:
        """Identify numeric columns"""
        if not results:
            return []
        
        numeric_cols = []
        sample = results[0]
        
        for col in columns:
            try:
                val = sample.get(col)
                if val is not None and isinstance(val, (int, float)):
                    numeric_cols.append(col)
                elif val is not None:
                    # Try to convert
                    float(str(val))
                    numeric_cols.append(col)
            except:
                pass
        
        return numeric_cols
    
    def _get_category_columns(self, results: List[Dict], columns: List[str]) -> List[str]:
        """Identify categorical columns"""
        numeric_cols = set(self._get_numeric_columns(results, columns))
        return [c for c in columns if c not in numeric_cols]

    def _is_time_column(self, column_name: str) -> bool:
        """Heuristic check for time/date-like columns."""
        col = column_name.lower()
        time_tokens = ['date', 'time', 'month', 'year', 'day', 'week', 'timestamp']
        return any(token in col for token in time_tokens)
    
    def _find_next_position(self, dashboard: Dict) -> Dict:
        """Find next available position in grid"""
        layout = dashboard['layout']
        occupied = {(c['position']['row'], c['position']['col']) for c in dashboard['charts']}
        
        for row in range(layout['rows']):
            for col in range(layout['columns']):
                if (row, col) not in occupied:
                    return {'row': row, 'col': col}
        
        # If all occupied, add to next row
        return {'row': layout['rows'], 'col': 0}
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def to_json(self, dashboard: Dict) -> str:
        """Serialize dashboard to JSON"""
        return json.dumps(dashboard, indent=2)
    
    def from_json(self, json_str: str) -> Dict:
        """Deserialize dashboard from JSON"""
        return json.loads(json_str)
