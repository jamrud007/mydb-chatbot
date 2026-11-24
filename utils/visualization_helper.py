"""
Visualization Helper - Intelligent chart type detection and configuration
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class VisualizationHelper:
    """Helper class to analyze query results and suggest visualizations"""
    
    # 🎨 Modern Color Palettes
    COLOR_PALETTES = {
        'primary': [
            'rgba(99, 102, 241, 0.8)',   # Indigo
            'rgba(59, 130, 246, 0.8)',   # Blue
            'rgba(16, 185, 129, 0.8)',   # Green
            'rgba(245, 158, 11, 0.8)',   # Amber
            'rgba(239, 68, 68, 0.8)',    # Red
            'rgba(168, 85, 247, 0.8)',   # Purple
            'rgba(236, 72, 153, 0.8)',   # Pink
            'rgba(20, 184, 166, 0.8)',   # Teal
        ],
        'pastel': [
            'rgba(147, 197, 253, 0.8)',  # Light Blue
            'rgba(167, 243, 208, 0.8)',  # Light Green
            'rgba(253, 186, 116, 0.8)',  # Light Orange
            'rgba(252, 165, 165, 0.8)',  # Light Red
            'rgba(196, 181, 253, 0.8)',  # Light Purple
        ]
    }
    
    # 📅 Date Patterns for Column Detection
    DATE_PATTERNS = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        'date', 'time', 'month', 'year', 'day', 'week',
        'tanggal', 'bulan', 'tahun', 'waktu'
    ]

    # 🔍 ID Patterns
    ID_PATTERNS = ['_id', 'id_', 'code', 'kode', 'uuid']

    @classmethod
    def analyze_for_visualization(cls, results: List[Dict], columns: List[str], user_query: str = '') -> Dict[str, Any]:
        """
        Analyze query results and recommend best visualization using Rule-Based Logic
        """
        if not results or not columns:
            return {'can_visualize': False, 'reason': 'No data to visualize'}
        
        # 0. Guardrail: Data Size
        if len(results) > 100:
             return {'can_visualize': False, 'reason': 'Too many rows (>100) for client-side rendering.'}

        # 1. Classify Columns
        col_types = cls._classify_columns(results, columns)
        dimensions = col_types['dimensions']
        metrics = col_types['metrics']
        time_dims = col_types['time']

        # 2. Detect Intent
        intent = cls._detect_intent(user_query, columns)
        logger.info(f"Detected Intent: {intent}, Dimensions: {dimensions}, Metrics: {metrics}, Time: {time_dims}")

        # 3. Apply Rules Engine
        return cls._apply_chart_rules(results, dimensions, metrics, time_dims, intent)

    @classmethod
    def _classify_columns(cls, results: List[Dict], columns: List[str]) -> Dict[str, List[str]]:
        """Classify columns into Dimensions (Time/Cat) and Metrics (Numeric)"""
        classification = {'dimensions': [], 'metrics': [], 'time': [], 'ids': []}
        
        for col in columns:
            # Get samples (skip None)
            samples = [row[col] for row in results if row[col] is not None][:5]
            if not samples:
                continue
            
            first_val = samples[0]
            str_val = str(first_val)
            col_lower = col.lower()

            # A. Check for ID (usually dimension, but often high cardinality)
            if any(p in col_lower for p in cls.ID_PATTERNS):
                classification['ids'].append(col)
                # IDs are dimensions, but handled carefully
                classification['dimensions'].append(col) 
                continue

            # B. Check for Time
            is_time = False
            if isinstance(first_val, datetime) or cls._is_date_like(col, str_val):
                classification['time'].append(col)
                classification['dimensions'].append(col)
                is_time = True
            
            # C. Check for Numeric (Metrics)
            if not is_time:
                # If direct number
                if isinstance(first_val, (int, float)):
                    classification['metrics'].append(col)
                # If formatted string number "Rp 1.000"
                elif cls._is_numeric_like(str_val):
                    classification['metrics'].append(col)
                else:
                    # Default to Dimension (Category)
                    classification['dimensions'].append(col)

        return classification

    @classmethod
    def _detect_intent(cls, query: str, columns: List[str]) -> str:
        """Parse user query to detect visualization intent"""
        q = query.lower()
        
        # 1. Trend / Time Series
        if any(k in q for k in ['trend', 'tren', 'waktu', 'time', 'per bulan', 'monthly', 'daily', 'yearly']):
            return 'trend'
        
        # 2. Composition / Part-to-whole
        if any(k in q for k in ['komposisi', 'composition', 'percentage', 'persentase', 'share', 'proporsi', 'ratio']):
            return 'composition'
        
        # 3. Ranking / Top N
        if any(k in q for k in ['top', 'rank', 'best', 'worst', 'tertinggi', 'terendah', 'termurah', 'termahal']):
            return 'ranking'
        
        # 4. Distribution
        if any(k in q for k in ['distribusi', 'sebaran', 'distribution', 'histogram', 'range']):
            return 'distribution'
            
        # 5. Relationship / Correlation
        if any(k in q for k in ['hubungan', 'korelasi', 'relasi', 'correlation', 'vs', 'pengaruh']):
            return 'relationship'

        return 'comparison' # Default

    @classmethod
    def _apply_chart_rules(cls, results: List[Dict], dims: List[str], metrics: List[str], time_dims: List[str], intent: str) -> Dict[str, Any]:
        """Core Rule Engine for Chart Selection"""
        
        # Rule 0: No Metrics -> Table
        if not metrics:
            return {'can_visualize': False, 'reason': 'No numeric metrics found.'}

        # Rule 1: Time Dimension -> Line Chart (Universal Rule for Trends)
        if time_dims:
            label = time_dims[0]
            # If multiple metrics, Multi-Line
            return cls._create_line_chart_config(results, label, metrics, title=f"Trend by {label}")

        # Rule 2: Relationship (No Dim + 2+ Metrics) -> Scatter
        # e.g. "Price vs Rating" (no category grouping, just raw points)
        if not dims and len(metrics) >= 2:
            return cls._create_scatter_config(results, metrics[0], metrics[1], title=f"{metrics[0]} vs {metrics[1]}")
        
        # Rule 3: Composition -> Pie/Donut or Stacked
        if intent == 'composition':
            # Strict Pie Rule: 1 Dim, 1 Metric, 3-8 Categories
            if len(dims) == 1 and len(metrics) == 1:
                unique_vals = len(set(row[dims[0]] for row in results))
                if 3 <= unique_vals <= 8:
                    return cls._create_pie_chart_config(results, dims[0], metrics[0])
        
        # Rule 4: Ranking -> Horizontal Bar (Sorted)
        # Rule 4: Ranking -> Horizontal Bar (Sorted)
        if intent == 'ranking' or len(results) > 10:
             if dims:
                 # Check for multiple metrics with scale disparity
                 if len(metrics) > 1:
                     # Switch to Horizontal Combo Chart (User Request)
                     return cls._create_horizontal_dual_axis_config(results, dims[0], metrics)
                 return cls._create_horizontal_bar_config(results, dims[0], metrics)
        
        # Rule 5: Comparison (Default)
        if dims:
            primary_dim = dims[0]
            # Multi-Metric Scale Check
            # If metrics have vastly different scales (e.g. Price 1M vs Rating 5), 
            # we should NOT plot them on same Y-axis without secondary axis.
            # Simplified: Plot Primary Metric, Tooltip others.
            if len(metrics) > 1:
                return cls._create_dual_axis_combo_config(results, primary_dim, metrics)
            
            return cls._create_bar_chart_config(results, primary_dim, metrics)

        # Fallback
        return {'can_visualize': False, 'reason': 'Data structure not suitable for defined logical rules.'}

    # --- Chart Configuration Generators ---

    @classmethod
    def _create_line_chart_config(cls, results, label_col, value_cols, title=""):
        labels = [str(row[label_col]) for row in results]
        datasets = []
        for i, col in enumerate(value_cols):
            data = [cls._parse_value(row[col]) for row in results]
            color = cls.COLOR_PALETTES['primary'][i % len(cls.COLOR_PALETTES['primary'])]
            datasets.append({
                'label': col,
                'data': data,
                'borderColor': color.replace('0.8', '1'),
                'backgroundColor': color,
                'tension': 0.4,
                'fill': True
            })
        
        return {
            'can_visualize': True,
            'chart_type': 'line',
            'chart_data': {
                'type': 'line',  # Added type
                'labels': labels, 
                'datasets': datasets
            },
            'reason': f'{title} ({", ".join(value_cols)})'
        }

    @classmethod
    def _create_bar_chart_config(cls, results, label_col, value_cols, orientation='vertical'):
        labels = [str(row[label_col]) for row in results]
        datasets = []
        for i, col in enumerate(value_cols):
            data = [cls._parse_value(row[col]) for row in results]
            color = cls.COLOR_PALETTES['primary'][i % len(cls.COLOR_PALETTES['primary'])]
            datasets.append({
                'label': col,
                'data': data,
                'backgroundColor': color,
                'borderRadius': 6
            })
        
        return {
            'can_visualize': True,
            'chart_type': 'bar',
            'chart_data': {
                'type': 'bar',   # Added type
                'labels': labels, 
                'datasets': datasets,
                'indexAxis': 'y' if orientation == 'horizontal' else 'x'
            },
            'reason': f'Comparing {", ".join(value_cols)} by {label_col}'
        }

    @classmethod
    def _create_horizontal_bar_config(cls, results, label_col, value_cols):
        # Sort logic could be added here if not already sorted by SQL
        return cls._create_bar_chart_config(results, label_col, value_cols, orientation='horizontal')

    @classmethod
    def _create_pie_chart_config(cls, results, label_col, value_col):
        labels = [str(row[label_col]) for row in results]
        data = [cls._parse_value(row[value_col]) for row in results]
        colors = cls.COLOR_PALETTES['primary'] + cls.COLOR_PALETTES['pastel']
        
        return {
            'can_visualize': True,
            'chart_type': 'pie',
            'chart_data': {
                'type': 'pie',   # Added type
                'labels': labels,
                'datasets': [{
                    'label': value_col,
                    'data': data,
                    'backgroundColor': colors[:len(data)],
                    'borderColor': '#fff',
                    'borderWidth': 1
                }]
            },
            'reason': f'Composition of {value_col} by {label_col}'
        }

    @classmethod
    def _create_scatter_config(cls, results, x_col, y_col, title=""):
        # Scatter needs explicit {x, y} structure
        data_points = []
        for row in results:
            data_points.append({
                'x': cls._parse_value(row[x_col]),
                'y': cls._parse_value(row[y_col]),
                # Optional: Add extra info for tooltip if available?
            })
            
        return {
            'can_visualize': True,
            'chart_type': 'scatter',
            'chart_data': {
                'type': 'scatter', # Added type
                'datasets': [{
                    'label': title,
                    'data': data_points,
                    'backgroundColor': cls.COLOR_PALETTES['primary'][0]
                }]
            },
            'reason': f'Relationship between {x_col} and {y_col}'
        }

    @classmethod
    def _create_dual_axis_combo_config(cls, results, label_col, metrics):
        """
        Create a Vertical Combo Chart (Bar + Line)
        Metric[0] -> Bar (Left Y-Axis)
        Metric[1] -> Line (Right Y-Axis)
        """
        primary_metric = metrics[0] 
        secondary_metric = metrics[1]
        
        labels = [str(row[label_col]) for row in results]
        
        # Dataset 1: Bar
        data1 = [cls._parse_value(row[primary_metric]) for row in results]
        ds1 = {
            'type': 'bar',
            'label': primary_metric,
            'data': data1,
            'backgroundColor': cls.COLOR_PALETTES['primary'][0],
            'yAxisID': 'y',
            'order': 2
        }

        # Dataset 2: Line
        data2 = [cls._parse_value(row[secondary_metric]) for row in results]
        ds2 = {
            'type': 'line',
            'label': secondary_metric,
            'data': data2,
            'borderColor': cls.COLOR_PALETTES['primary'][3], # Amber/Orange
            'backgroundColor': cls.COLOR_PALETTES['primary'][3],
            'borderWidth': 2,
            'pointRadius': 4,
            'yAxisID': 'y1', # Secondary Y-Axis
            'order': 1
        }

        return {
            'can_visualize': True,
            'chart_type': 'bar', # Main type
            'chart_data': {
                'type': 'bar',
                'labels': labels, 
                'datasets': [ds1, ds2],
                'is_dual_axis': True, # Shared flag
                'primaryAxisTitle': primary_metric.replace('_', ' ').title(),
                'secondaryAxisTitle': secondary_metric.replace('_', ' ').title()
            },
            'reason': f'Comparing {primary_metric} vs {secondary_metric} by {label_col}',
            'is_dual_axis': True
        }

    @classmethod
    def _create_horizontal_dual_axis_config(cls, results, label_col, metrics):
        """
        Create a Horizontal Combo Chart (Horizontal Bar + Scatter/Line Points)
        Metric[0] -> Bar (Bottom X-Axis)
        Metric[1] -> Scatter Points (Top X-Axis)
        """
        primary_metric = metrics[0] 
        secondary_metric = metrics[1]
        
        labels = [str(row[label_col]) for row in results]
        
        # Dataset 1: Horizontal Bar (Revenue)
        data1 = [cls._parse_value(row[primary_metric]) for row in results]
        ds1 = {
            'type': 'bar',
            'label': primary_metric,
            'data': data1,
            'backgroundColor': cls.COLOR_PALETTES['primary'][0],
            'xAxisID': 'xRevenue', # Changed from yAxisID
            'yAxisID': 'y',
            'order': 2 
        }

        # Dataset 2: Points (Rating)
        data2 = [cls._parse_value(row[secondary_metric]) for row in results]
        ds2 = {
            'type': 'line',
            'label': secondary_metric,
            'data': data2,
            'borderColor': '#10b981', # Green for rating
            'backgroundColor': '#10b981',
            'borderWidth': 0,
            'pointRadius': 6,
            'pointHoverRadius': 8,
            'showLine': False,
            'xAxisID': 'xRating', # Secondary X-Axis
            'yAxisID': 'y',
            'order': 1
        }

        # Check if secondary metric looks like a Rating (0-5)
        is_rating = all(0 <= x <= 5 for x in data2 if x is not None)

        return {
            'can_visualize': True,
            'chart_type': 'bar',
            'chart_data': {
                'type': 'bar',
                'labels': labels, 
                'datasets': [ds1, ds2],
                'is_horizontal_combo': True, # New flag for frontend
                'primaryAxisTitle': primary_metric.replace('_', ' ').title(),
                'secondaryAxisTitle': secondary_metric.replace('_', ' ').title(),
                'is_rating': is_rating,
                'indexAxis': 'y' # Explicitly horizontal
            },
            'reason': f'Comparing {primary_metric} vs {secondary_metric} by {label_col}',
            'is_dual_axis': True
        }

    # --- Helpers ---

    @classmethod
    def _is_date_like(cls, col_name, value_str):
        col_lower = col_name.lower()
        if any(p in col_lower for p in cls.DATE_PATTERNS if isinstance(p, str)): return True
        return False

    @classmethod
    def _is_numeric_like(cls, value):
        if not value: return False
        clean_val = re.sub(r'[Rp$€£¥\s.,%]', '', str(value))
        return clean_val.replace('-','').isdigit()

    @classmethod
    def _parse_value(cls, value):
        if value is None: return 0
        if isinstance(value, (int, float)): return value
        s = str(value)
        s_clean = re.sub(r'[^\d.,-]', '', s)
        if '.' in s_clean and ',' in s_clean:
            if s_clean.rindex(',') > s_clean.rindex('.'): s_clean = s_clean.replace('.', '').replace(',', '.') # 1.000,00
            else: s_clean = s_clean.replace(',', '') # 1,000.00
        elif ',' in s_clean:
             parts = s_clean.split(',')
             if len(parts) == 2 and len(parts[1]) != 3: s_clean = s_clean.replace(',', '.')
             else: s_clean = s_clean.replace(',', '')
        elif '.' in s_clean:
             parts = s_clean.split('.')
             if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]): s_clean = s_clean.replace('.', '')
        try: return float(s_clean)
        except: return 0

    @classmethod
    def _format_value(cls, val):
        return str(val) # Keep original formatting for tooltip text
