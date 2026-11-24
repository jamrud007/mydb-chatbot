# 📊 Advanced Chart Types - Implementation Plan

## 🎯 Focus: 4 Core Visualization Categories

### 1. 📊 **Bandingkan Kategori (Comparison)**
**Charts**: Bar, Column, Stacked Bar

**Current**: ✅ Bar Chart
**To Add**: 
- ✅ Horizontal Bar (sudah ada)
- 🆕 **Stacked Bar** (multi-series comparison)

**Use Cases**:
- Compare values across categories
- Show sub-categories within main categories
- **Example**: Sales by product category, broken down by region

**Keywords**: `compare`, `vs`, `versus`, `by category`, `breakdown by`

---

### 2. 📈 **Tren Waktu (Time Trends)**
**Charts**: Line, Area

**Current**: ✅ Line Chart
**To Add**:
- 🆕 **Area Chart** (filled line for cumulative view)

**Use Cases**:
- Show changes over time
- Visualize cumulative totals
- **Example**: Revenue over months, user growth

**Keywords**: `trend`, `over time`, `per month`, `growth`, `cumulative`

---

### 3. 🥧 **Komposisi (Composition)**
**Charts**: Stacked Bar, Pie

**Current**: ✅ Pie Chart (for few categories)
**To Add**:
- 🆕 **Stacked Bar** (better for many categories)
- Consider: Treemap (future - needs D3.js)

**Use Cases**:
- Show part-to-whole relationships
- Compare composition across groups
- **Example**: Order status distribution by month

**Keywords**: `composition`, `breakdown`, `proportion`, `percentage of`

---

### 4. 📊 **Distribusi (Distribution)**
**Charts**: Histogram, Box Plot

**To Add**:
- 🆕 **Histogram** (frequency distribution of numeric values)
- Consider: Box/Violin (future - complex)

**Use Cases**:
- Show frequency distribution
- Identify patterns, outliers, skewness
- **Example**: Price distribution, age groups

**Keywords**: `distribution`, `frequency`, `range`, `histogram`

---

## 🛠️ Implementation Plan

### Phase 1: Add Stacked Bar Chart

**What**: Multi-series bar chart with stacking

**Use Case**: 
```sql
-- Sales by category per month (stacked)
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    product_category,
    SUM(price) as total_sales
FROM orders
GROUP BY month, product_category
ORDER BY month;
```

**Detection Logic**:
- Multiple numeric columns OR
- Group by 2+ columns (time + category)
- Keyword: "breakdown by", "stacked"

**Chart.js Config**:
```javascript
{
    type: 'bar',
    data: {
        labels: ['Jan', 'Feb', 'Mar'],
        datasets: [
            { label: 'Electronics', data: [100, 120, 150], stack: 'Stack 0' },
            { label: 'Clothing', data: [80, 90, 100], stack: 'Stack 0' }
        ]
    },
    options: {
        scales: {
            x: { stacked: true },
            y: { stacked: true }
        }
    }
}
```

---

### Phase 2: Add Area Chart

**What**: Filled line chart for cumulative trends

**Use Case**:
```sql
-- Cumulative orders over time
SELECT 
    DATE(order_date) as date,
    SUM(quantity) as daily_total
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY date
ORDER BY date;
```

**Detection Logic**:
- Time series data
- Keyword: "cumulative", "total over time", "growth"

**Chart.js Config**:
```javascript
{
    type: 'line',
    data: { ... },
    options: {
        plugins: { filler: { propagate: false } },
        fill: 'origin'  // Fill to zero
    }
}
```

---

### Phase 3: Add Histogram

**What**: Binned frequency distribution

**Use Case**:
```sql
-- Price distribution (binned)
SELECT 
    FLOOR(price / 100) * 100 as price_range,
    COUNT(*) as frequency
FROM products
GROUP BY price_range
ORDER BY price_range;
```

**Detection Logic**:
- Numeric bins/ranges in labels
- Keyword: "distribution", "histogram", "frequency"

**Chart.js Config**:
```javascript
{
    type: 'bar',
    data: {
        labels: ['0-100', '100-200', '200-300'],
        datasets: [{
            data: [50, 120, 80],
            barPercentage: 1.0,  // No gaps between bars
            categoryPercentage: 1.0
        }]
    }
}
```

---

## 🎯 Detection Logic Summary

```python
# In visualization_helper.py

def _determine_advanced_chart_type():
    # 1. STACKED BAR
    if multiple_numeric_cols or "breakdown by" in query:
        return create_stacked_bar()
    
    # 2. AREA CHART  
    if is_time_series and ("cumulative" in query or "growth" in query):
        return create_area_chart()
    
    # 3. HISTOGRAM
    if has_numeric_bins or "distribution" in query or "histogram" in query:
        return create_histogram()
    
    # 4. Continue with existing logic
    ...
```

---

## 📝 Example Queries

### Stacked Bar:
```
Show sales by product category per month
Order breakdown by status for each seller
```

### Area Chart:
```
Show cumulative revenue over time
Total user growth per day
```

### Histogram:
```
Show price distribution of products
Distribution of order values
Frequency of delivery times
```

---

## 🔧 Files to Modify

1. **`utils/visualization_helper.py`**:
   - Add `_create_stacked_bar_config()`
   - Add `_create_area_chart_config()`
   - Add `_create_histogram_config()`
   - Update `_determine_chart_type()` with new logic

2. **`static/js/chat.js`**:
   - Update `renderChart()` to handle stacked option
   - Handle area chart (fill) option
   - Handle histogram (bar spacing) option

3. **`static/css/style.css`**:
   - No changes needed (Chart.js handles styling)

---

## ⏱️ Implementation Time

- ✅ **Stacked Bar**: ~30 minutes
- ✅ **Area Chart**: ~15 minutes (simple variant)
- ✅ **Histogram**: ~45 minutes (needs binning logic)

**Total**: ~1.5 hours

---

## 🚀 Ready to Implement?

Shall I start with:
1. **Stacked Bar** (most useful for multi-dimensional analysis)
2. **Area Chart** (easy, visual enhancement for trends)
3. **Histogram** (needs data preprocessing logic)

Or implement all 3 in sequence?

Let me know and I'll start coding! 💻
