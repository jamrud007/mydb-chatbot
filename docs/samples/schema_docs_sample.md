# Database Schema Documentation

**Generated:** 2026-01-30 17:18:54
**Total Tables:** 14

## Table of Contents

1. [customers](#customers)
2. [geolocation](#geolocation)
3. [leads_closed](#leads_closed)
4. [leads_qualified](#leads_qualified)
5. [order_items](#order_items)
6. [order_payments](#order_payments)
7. [order_reviews](#order_reviews)
8. [order_summary](#order_summary)
9. [orders](#orders)
10. [product_category_name_translation](#product_category_name_translation)
11. [product_performance](#product_performance)
12. [products](#products)
13. [sellers](#sellers)
14. [users](#users)

---

## customers

**Total Columns:** 5

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `customer_id` | varchar | ✗ | - | - | - |
| `customer_unique_id` | varchar | ✓ | - | - | - |
| `customer_zip_code_prefix` | varchar | ✓ | - | - | - |
| `customer_city` | varchar | ✓ | - | - | - |
| `customer_state` | varchar | ✓ | - | - | - |

---

## geolocation

**Total Columns:** 6

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `geolocation_id` | int | ✗ | - | - | - |
| `geolocation_zip_code_prefix` | varchar | ✓ | - | - | - |
| `geolocation_lat` | decimal | ✓ | - | - | - |
| `geolocation_lng` | decimal | ✓ | - | - | - |
| `geolocation_city` | varchar | ✓ | - | - | - |
| `geolocation_state` | varchar | ✓ | - | - | - |

---

## leads_closed

**Total Columns:** 14

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `mql_id` | varchar | ✗ | - | - | - |
| `seller_id` | varchar | ✓ | - | - | - |
| `sdr_id` | varchar | ✓ | - | - | - |
| `sr_id` | varchar | ✓ | - | - | - |
| `won_date` | datetime | ✓ | - | - | - |
| `business_segment` | varchar | ✓ | - | - | - |
| `lead_type` | varchar | ✓ | - | - | - |
| `lead_behaviour_profile` | varchar | ✓ | - | - | - |
| `has_company` | tinyint | ✓ | - | - | - |
| `has_gtin` | tinyint | ✓ | - | - | - |
| `average_stock` | varchar | ✓ | - | - | - |
| `business_type` | varchar | ✓ | - | - | - |
| `declared_product_catalog_size` | int | ✓ | - | - | - |
| `declared_monthly_revenue` | decimal | ✓ | - | - | - |

---

## leads_qualified

**Total Columns:** 4

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `mql_id` | varchar | ✗ | - | - | - |
| `first_contact_date` | datetime | ✓ | - | - | - |
| `landing_page_id` | varchar | ✓ | - | - | - |
| `origin` | varchar | ✓ | - | - | - |

---

## order_items

**Total Columns:** 7

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `order_id` | varchar | ✗ | - | - | - |
| `order_item_id` | int | ✗ | - | - | - |
| `product_id` | varchar | ✓ | - | - | - |
| `seller_id` | varchar | ✓ | - | - | - |
| `shipping_limit_date` | datetime | ✓ | - | - | - |
| `price` | decimal | ✓ | - | - | - |
| `freight_value` | decimal | ✓ | - | - | - |

---

## order_payments

**Total Columns:** 5

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `order_id` | varchar | ✗ | - | - | - |
| `payment_sequential` | int | ✗ | - | - | - |
| `payment_type` | varchar | ✓ | - | - | - |
| `payment_installments` | int | ✓ | - | - | - |
| `payment_value` | decimal | ✓ | - | - | - |

---

## order_reviews

**Total Columns:** 7

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `review_id` | varchar | ✗ | - | - | - |
| `order_id` | varchar | ✓ | - | - | - |
| `review_score` | int | ✓ | - | - | - |
| `review_comment_title` | varchar | ✓ | - | - | - |
| `review_comment_message` | text | ✓ | - | - | - |
| `review_creation_date` | datetime | ✓ | - | - | - |
| `review_answer_timestamp` | datetime | ✓ | - | - | - |

---

## order_summary

**Total Columns:** 7

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `order_id` | varchar | ✗ | - | - | - |
| `customer_id` | varchar | ✓ | - | - | - |
| `order_status` | varchar | ✓ | - | - | - |
| `order_purchase_timestamp` | datetime | ✓ | - | - | - |
| `total_items` | bigint | ✗ | - | - | - |
| `total_value` | decimal | ✓ | - | - | - |
| `avg_review_score` | decimal | ✓ | - | - | - |

---

## orders

**Total Columns:** 8

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `order_id` | varchar | ✗ | - | - | - |
| `customer_id` | varchar | ✓ | - | - | - |
| `order_status` | varchar | ✓ | - | - | - |
| `order_purchase_timestamp` | datetime | ✓ | - | - | - |
| `order_approved_at` | datetime | ✓ | - | - | - |
| `order_delivered_carrier_date` | datetime | ✓ | - | - | - |
| `order_delivered_customer_date` | datetime | ✓ | - | - | - |
| `order_estimated_delivery_date` | datetime | ✓ | - | - | - |

---

## product_category_name_translation

**Total Columns:** 2

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `product_category_name` | varchar | ✗ | - | - | - |
| `product_category_name_english` | varchar | ✓ | - | - | - |

---

## product_performance

**Total Columns:** 6

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `product_id` | varchar | ✗ | - | - | - |
| `product_category_name` | varchar | ✓ | - | - | - |
| `product_category_name_english` | varchar | ✓ | - | - | - |
| `total_orders` | bigint | ✗ | - | - | - |
| `total_revenue` | decimal | ✓ | - | - | - |
| `avg_price` | decimal | ✓ | - | - | - |

---

## products

**Total Columns:** 9

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `product_id` | varchar | ✗ | - | - | - |
| `product_category_name` | varchar | ✓ | - | - | - |
| `product_name_length` | int | ✓ | - | - | - |
| `product_description_length` | int | ✓ | - | - | - |
| `product_photos_qty` | int | ✓ | - | - | - |
| `product_weight_g` | int | ✓ | - | - | - |
| `product_length_cm` | int | ✓ | - | - | - |
| `product_height_cm` | int | ✓ | - | - | - |
| `product_width_cm` | int | ✓ | - | - | - |

---

## sellers

**Total Columns:** 4

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `seller_id` | varchar | ✗ | - | - | - |
| `seller_zip_code_prefix` | varchar | ✓ | - | - | - |
| `seller_city` | varchar | ✓ | - | - | - |
| `seller_state` | varchar | ✓ | - | - | - |

---

## users

**Total Columns:** 9

### Columns

| Column | Type | Nullable | Key | Default | Extra |
|--------|------|----------|-----|---------|-------|
| `id` | int | ✗ | - | - | - |
| `username` | varchar | ✗ | - | - | - |
| `email` | varchar | ✗ | - | - | - |
| `hashed_password` | varchar | ✗ | - | - | - |
| `created_at` | timestamp | ✓ | - | - | - |
| `last_login` | timestamp | ✓ | - | - | - |
| `is_active` | tinyint | ✓ | - | - | - |
| `is_verified` | tinyint | ✓ | - | - | - |
| `verification_code` | varchar | ✓ | - | - | - |

---
