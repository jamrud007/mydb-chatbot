# Analytics API Documentation

Provides pre-processed data optimized for Chart.js visualization.
**Base URL:** `/api/analytics`

## Endpoints

### 1. Revenue by Category
- **URL:** `/revenue-by-category`
- **Method:** `GET`
- **Data:** Top products by revenue
- **Chart Type:** Vertical Bar
- **Response:**
  ```json
  {
    "success": true,
    "title": "Revenue by Product Category",
    "chart_data": { ...Chart.js config... }
  }
  ```

### 2. Payment Distribution
- **URL:** `/payment-distribution`
- **Method:** `GET`
- **Data:** Count and total value by payment type
- **Chart Type:** Pie Chart

### 3. Review Score Distribution
- **URL:** `/review-scores`
- **Method:** `GET`
- **Data:** Review counts per star rating
- **Chart Type:** Bar Chart

### 4. Average Freight by City
- **URL:** `/avg-freight-by-city`
- **Method:** `GET`
- **Data:** Top seller cities by avg freight cost
- **Chart Type:** Horizontal Bar (**indexAxis: 'y'**)

### 5. Order Status
- **URL:** `/order-status`
- **Method:** `GET`
- **Data:** Order counts by status
- **Chart Type:** Pie Chart

## Frontend Integration

```javascript
async function loadDashboard(endpoint) {
    const response = await fetch(`/api/analytics/${endpoint}`);
    const data = await response.json();
    
    if (data.success) {
        renderChart(data.chart_data);
    }
}
```
