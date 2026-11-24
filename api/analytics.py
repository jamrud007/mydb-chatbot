"""
Analytics API - Pre-processed data endpoints for charts
No AI needed - Direct database queries with visualization-ready format
"""
from flask import Blueprint, jsonify
import logging
from database.query_executor import QueryExecutor
from database.db_connection import DatabaseConnection
from config import Config

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Initialize database components
db_config = Config.get_db_config()
db_connection = DatabaseConnection(db_config)
query_executor = QueryExecutor(
    db_connection,
    read_only=True,  # Analytics should be read-only
    max_rows=1000
)


@analytics_bp.route('/revenue-by-category', methods=['GET'])
def revenue_by_category():
    """
    Get revenue breakdown by product category
    Returns data ready for Bar Chart
    """
    try:
        query = """
            SELECT 
                product_category_name_english as category,
                total_revenue as revenue,
                total_orders as orders
            FROM product_performance
            ORDER BY total_revenue DESC
        """
        
        result = query_executor.execute(query)
        
        if not result['success']:
            return jsonify({'error': result.get('error')}), 500
        
        rows = result['rows']
        
        # Format for Chart.js
        chart_data = {
            'type': 'bar',
            'labels': [row['category'] for row in rows],
            'datasets': [{
                'label': 'Revenue (R$)',
                'data': [float(row['revenue']) for row in rows],
                'backgroundColor': 'rgba(99, 102, 241, 0.8)',
                'borderColor': 'rgba(99, 102, 241, 1)',
                'borderWidth': 2
            }]
        }
        
        return jsonify({
            'success': True,
            'title': 'Revenue by Product Category',
            'chart_data': chart_data,
            'raw_data': rows
        })
        
    except Exception as e:
        logger.error(f"Error in revenue_by_category: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/payment-distribution', methods=['GET'])
def payment_distribution():
    """
    Get payment type distribution
    Returns data ready for Pie Chart
    """
    try:
        query = """
            SELECT 
                payment_type,
                COUNT(*) as count,
                SUM(payment_value) as total_value
            FROM order_payments
            GROUP BY payment_type
            ORDER BY total_value DESC
        """
        
        result = query_executor.execute(query)
        
        if not result['success']:
            return jsonify({'error': result.get('error')}), 500
        
        rows = result['rows']
        
        # Format for Chart.js Pie Chart
        colors = [
            'rgba(99, 102, 241, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
        ]
        
        chart_data = {
            'type': 'pie',
            'labels': [row['payment_type'].replace('_', ' ').title() for row in rows],
            'datasets': [{
                'label': 'Payment Distribution',
                'data': [float(row['total_value']) for row in rows],
                'backgroundColor': colors[:len(rows)],
                'borderColor': ['rgba(255, 255, 255, 0.8)'] * len(rows),
                'borderWidth': 2
            }]
        }
        
        return jsonify({
            'success': True,
            'title': 'Payment Method Distribution',
            'chart_data': chart_data,
            'raw_data': rows
        })
        
    except Exception as e:
        logger.error(f"Error in payment_distribution: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/review-scores', methods=['GET'])
def review_scores():
    """
    Get review score distribution
    Returns data ready for Bar/Pie Chart
    """
    try:
        query = """
            SELECT 
                review_score,
                COUNT(*) as count
            FROM order_reviews
            GROUP BY review_score
            ORDER BY review_score DESC
        """
        
        result = query_executor.execute(query)
        
        if not result['success']:
            return jsonify({'error': result.get('error')}), 500
        
        rows = result['rows']
        
        # Format for Chart.js
        chart_data = {
            'type': 'bar',
            'labels': [f"{row['review_score']} Stars" for row in rows],
            'datasets': [{
                'label': 'Number of Reviews',
                'data': [row['count'] for row in rows],
                'backgroundColor': 'rgba(245, 158, 11, 0.8)',
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 2
            }]
        }
        
        return jsonify({
            'success': True,
            'title': 'Review Score Distribution',
            'chart_data': chart_data,
            'raw_data': rows
        })
        
    except Exception as e:
        logger.error(f"Error in review_scores: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/avg-freight-by-city', methods=['GET'])
def avg_freight_by_city():
    """
    Get average freight value by seller city
    Returns data ready for Horizontal Bar Chart
    """
    try:
        query = """
            SELECT 
                s.seller_city,
                AVG(oi.freight_value) as avg_freight
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            GROUP BY s.seller_city
            ORDER BY avg_freight DESC
        """
        
        result = query_executor.execute(query)
        
        if not result['success']:
            return jsonify({'error': result.get('error')}), 500
        
        rows = result['rows']
        
        # Format for Chart.js Horizontal Bar
        chart_data = {
            'type': 'bar',
            'indexAxis': 'y',  # Makes it horizontal
            'labels': [row['seller_city'].title() for row in rows],
            'datasets': [{
                'label': 'Avg Freight (R$)',
                'data': [float(row['avg_freight']) for row in rows],
                'backgroundColor': 'rgba(16, 185, 129, 0.8)',
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 2
            }]
        }
        
        return jsonify({
            'success': True,
            'title': 'Average Freight Cost by City',
            'chart_data': chart_data,
            'raw_data': rows
        })
        
    except Exception as e:
        logger.error(f"Error in avg_freight_by_city: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/order-status', methods=['GET'])
def order_status():
    """
    Get order count by status
    Returns data ready for Pie Chart
    """
    try:
        query = """
            SELECT 
                order_status,
                COUNT(*) as count
            FROM orders
            GROUP BY order_status
            ORDER BY count DESC
        """
        
        result = query_executor.execute(query)
        
        if not result['success']:
            return jsonify({'error': result.get('error')}), 500
        
        rows = result['rows']
        
        colors = [
            'rgba(16, 185, 129, 0.8)',  # Green for delivered
            'rgba(59, 130, 246, 0.8)',  # Blue for shipped
            'rgba(245, 158, 11, 0.8)',  # Orange for processing
            'rgba(239, 68, 68, 0.8)',   # Red for canceled
        ]
        
        chart_data = {
            'type': 'pie',
            'labels': [row['order_status'].replace('_', ' ').title() for row in rows],
            'datasets': [{
                'label': 'Order Status',
                'data': [row['count'] for row in rows],
                'backgroundColor': colors[:len(rows)],
                'borderColor': ['rgba(255, 255, 255, 0.8)'] * len(rows),
                'borderWidth': 2
            }]
        }
        
        return jsonify({
            'success': True,
            'title': 'Order Status Distribution',
            'chart_data': chart_data,
            'raw_data': rows
        })
        
    except Exception as e:
        logger.error(f"Error in order_status: {e}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/list', methods=['GET'])
def list_analytics():
    """
    List all available analytics endpoints
    """
    endpoints = [
        {
            'path': '/api/analytics/revenue-by-category',
            'description': 'Revenue breakdown by product category',
            'chart_type': 'bar'
        },
        {
            'path': '/api/analytics/payment-distribution',
            'description': 'Payment method distribution',
            'chart_type': 'pie'
        },
        {
            'path': '/api/analytics/review-scores',
            'description': 'Review score distribution',
            'chart_type': 'bar'
        },
        {
            'path': '/api/analytics/avg-freight-by-city',
            'description': 'Average freight cost by seller city',
            'chart_type': 'horizontalBar'
        },
        {
            'path': '/api/analytics/order-status',
            'description': 'Order count by status',
            'chart_type': 'pie'
        }
    ]
    
    return jsonify({
        'success': True,
        'endpoints': endpoints
    })
