"""
AI-Driven Smart Inventory & Financial Analytics Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import custom modules
from database import db, DatabaseManager
from inventory import InventoryManager
from sales import SalesManager
from analytics import Analytics
from discount_engine import DiscountEngine
from forecasting import DemandForecaster

# Page configuration
st.set_page_config(
    page_title="Retail Intelligence Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    .main {
        padding-top: 0rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .alert-critical {
        background-color: #ffcccc;
        border-left: 4px solid #da1e28;
        padding: 10px;
        border-radius: 4px;
        margin: 5px 0;
    }
    .alert-warning {
        background-color: #fff4e6;
        border-left: 4px solid #f1c21b;
        padding: 10px;
        border-radius: 4px;
        margin: 5px 0;
    }
    .alert-info {
        background-color: #e3f2fd;
        border-left: 4px solid #0f62fe;
        padding: 10px;
        border-radius: 4px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

def create_sample_data():
    """Create sample inventory data."""
    sample_products = [
        ("Colgate", "Personal Care", 80, 120, 150, 50, (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')),
        ("Amul Milk", "Dairy", 40, 60, 200, 100, (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
        ("Britannia Bread", "Bakery", 25, 40, 100, 40, (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')),
        ("Parle-G", "Biscuits", 20, 35, 300, 100, (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d')),
        ("Maggi", "Instant Foods", 8, 15, 400, 150, (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')),
        ("Surf Excel", "Detergent", 200, 300, 80, 30, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')),
        ("Tata Salt", "Condiments", 15, 25, 250, 80, (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')),
        ("Aashirvaad Atta", "Staples", 350, 450, 60, 20, (datetime.now() + timedelta(days=200)).strftime('%Y-%m-%d')),
        ("Lay's Chips", "Snacks", 30, 50, 180, 60, (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')),
        ("Coca-Cola", "Beverages", 40, 70, 220, 80, (datetime.now() + timedelta(days=150)).strftime('%Y-%m-%d')),
    ]
    
    for product in sample_products:
        try:
            InventoryManager.add_product(*product)
        except:
            pass  # Product already exists

# Sidebar Navigation
with st.sidebar:
    st.title("🏪 Retail Dashboard")
    st.markdown("---")
    
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "📦 Inventory", "🛒 Sales", "📈 Analytics", 
         "🔮 Forecasting", "⚠️ Alerts", "📥 Restock", "💰 Discounts", "📋 Reports"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔄 Refresh Data"):
        st.session_state.refresh = True
        st.rerun()
    
    if st.button("📌 Load Sample Data"):
        create_sample_data()
        st.success("Sample data loaded!")
        st.rerun()
    
    st.markdown("---")
    st.caption("AI-Driven Inventory Management System")
    st.caption("HCL Jigsaw Innovation Challenge")

# Main content based on page selection
if page == "📊 Dashboard":
    st.title("📊 Executive Dashboard")
    st.markdown("Real-time retail intelligence and KPIs")
    
    # Get KPIs
    kpis = Analytics.get_kpis(days=30)
    
    if kpis:
        # KPI Row 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💼 Inventory Value",
                f"₹{kpis.get('total_inventory_value', 0):,.0f}",
                delta="Stock × Cost Price"
            )
        
        with col2:
            st.metric(
                "💰 Total Revenue",
                f"₹{kpis.get('total_revenue', 0):,.0f}",
                delta="Last 30 days"
            )
        
        with col3:
            st.metric(
                "📈 Total Profit",
                f"₹{kpis.get('total_profit', 0):,.0f}",
                delta=f"{kpis.get('profit_margin_percent', 0):.1f}% margin"
            )
        
        with col4:
            st.metric(
                "⚠️ Alerts",
                kpis.get('items_in_low_stock', 0) + kpis.get('items_near_expiry', 0),
                delta="Active warnings"
            )
        
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📦 Inventory Status")
            try:
                products = InventoryManager.get_all_products()
                if not products.empty:
                    fig = px.bar(
                        products,
                        x='product_name',
                        y='stock',
                        title="Stock Levels",
                        labels={'stock': 'Quantity', 'product_name': 'Product'},
                        color='stock',
                        color_continuous_scale='Viridis'
                    )
                    fig.add_hline(y=products['reorder_level'].mean(), 
                                 line_dash="dash", 
                                 line_color="red",
                                 annotation_text="Reorder Level")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading chart: {e}")
        
        with col2:
            st.subheader("💹 Profit Contribution")
            try:
                sales_contrib = SalesManager.get_product_sales_contribution()
                if sales_contrib:
                    df = pd.DataFrame(sales_contrib, columns=['product_id', 'product_name', 'revenue', 'profit'])
                    fig = px.pie(
                        df,
                        values='profit',
                        names='product_name',
                        title="Profit by Product"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading chart: {e}")
        
        # Sales Trend
        st.subheader("📊 Sales Trend (Last 30 Days)")
        try:
            trend_data = Analytics.get_sales_trend(days=30)
            if trend_data:
                df = pd.DataFrame(trend_data)
                df['date'] = pd.to_datetime(df['date'])
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Scatter(x=df['date'], y=df['revenue'], name="Revenue", mode='lines+markers'),
                    secondary_y=False
                )
                fig.add_trace(
                    go.Bar(x=df['date'], y=df['units_sold'], name="Units Sold", opacity=0.3),
                    secondary_y=True
                )
                
                fig.update_layout(
                    title="Sales Revenue & Units",
                    xaxis_title="Date",
                    yaxis_title="Revenue (₹)",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading trend: {e}")
    else:
        st.info("📌 Load sample data from sidebar to see KPIs")

elif page == "📦 Inventory":
    st.title("📦 Inventory Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View", "Add Product", "Update", "Search"])
    
    with tab1:
        st.subheader("Current Inventory")
        try:
            products = InventoryManager.get_all_products()
            if not products.empty:
                st.dataframe(products, use_container_width=True)
            else:
                st.info("No products in inventory. Add products to get started!")
        except Exception as e:
            st.error(f"Error loading inventory: {e}")
    
    with tab2:
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Product Name")
                cost_price = st.number_input("Cost Price (₹)", min_value=0.0, step=10.0)
                stock = st.number_input("Initial Stock", min_value=0, step=10)
            
            with col2:
                category = st.selectbox("Category", 
                    ["Personal Care", "Dairy", "Bakery", "Biscuits", "Instant Foods", 
                     "Detergent", "Condiments", "Staples", "Snacks", "Beverages", "Other"])
                selling_price = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0)
                reorder_level = st.number_input("Reorder Level", min_value=1, step=5)
            
            expiry_date = st.date_input("Expiry Date", value=datetime.now() + timedelta(days=90))
            
            if st.form_submit_button("✅ Add Product"):
                if product_name and cost_price > 0 and selling_price > cost_price:
                    if InventoryManager.add_product(
                        product_name, category, cost_price, selling_price, 
                        stock, reorder_level, expiry_date.strftime('%Y-%m-%d')
                    ):
                        st.success(f"✅ Product '{product_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add product (may already exist)")
                else:
                    st.error("❌ Invalid input: Check prices and fields")
    
    with tab3:
        st.subheader("Update Product")
        try:
            products = InventoryManager.get_all_products()
            if not products.empty:
                product_id = st.selectbox("Select Product", 
                    options=products['product_id'],
                    format_func=lambda x: products[products['product_id']==x]['product_name'].values[0])
                
                product = InventoryManager.get_product_by_id(product_id)
                if product:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_stock = st.number_input("Stock", value=product[5], step=1)
                        new_cost = st.number_input("Cost Price", value=float(product[3]), step=1.0)
                    with col2:
                        new_selling = st.number_input("Selling Price", value=float(product[4]), step=1.0)
                        new_expiry = st.date_input("Expiry Date", value=datetime.strptime(product[7], '%Y-%m-%d'))
                    
                    if st.button("💾 Update Product"):
                        InventoryManager.update_product(
                            product_id,
                            stock=new_stock,
                            cost_price=new_cost,
                            selling_price=new_selling,
                            expiry_date=new_expiry.strftime('%Y-%m-%d')
                        )
                        st.success("✅ Product updated!")
                        st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab4:
        st.subheader("Search Products")
        search_term = st.text_input("Search by name")
        category_filter = st.selectbox("Filter by category", 
            ["All"] + InventoryManager.get_categories())
        
        if st.button("🔍 Search"):
            results = InventoryManager.search_products(
                search_term=search_term if search_term else None,
                category=category_filter if category_filter != "All" else None
            )
            if results:
                df = pd.DataFrame(results, columns=['ID', 'Name', 'Category', 'Cost', 'Selling', 'Stock', 'Reorder', 'Expiry', 'Created', 'Updated'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No products found")

elif page == "🛒 Sales":
    st.title("🛒 Sales Transactions")
    
    tab1, tab2 = st.tabs(["Record Sale", "Sales History"])
    
    with tab1:
        st.subheader("Record New Sale")
        try:
            products = InventoryManager.get_all_products()
            if not products.empty:
                with st.form("sales_form"):
                    product_id = st.selectbox("Select Product",
                        options=products['product_id'],
                        format_func=lambda x: products[products['product_id']==x]['product_name'].values[0])
                    
                    quantity = st.number_input("Quantity Sold", min_value=1, step=1)
                    discount = st.slider("Discount (%)", 0, 50, 0)
                    
                    if st.form_submit_button("✅ Record Sale"):
                        if SalesManager.record_sale(product_id, quantity, discount):
                            st.success(f"✅ Sale recorded! {quantity} units sold")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Sale recording failed")
            else:
                st.info("Add products to inventory first")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Sales History")
        try:
            sales = SalesManager.get_sales_data(days=30)
            if not sales.empty:
                # Join with product names
                products = InventoryManager.get_all_products()
                sales = sales.merge(products[['product_id', 'product_name']], on='product_id', how='left')
                st.dataframe(sales[['sale_id', 'product_name', 'quantity_sold', 'sale_price', 'discount_applied', 'total_amount', 'sale_date']], use_container_width=True)
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Sales", len(sales))
                with col2:
                    st.metric("Total Revenue", f"₹{sales['total_amount'].sum():,.0f}")
                with col3:
                    st.metric("Total Discounts", f"₹{sales['discount_applied'].sum():,.0f}")
            else:
                st.info("No sales recorded yet")
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "📈 Analytics":
    st.title("📈 Financial Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Category Analysis", "Top Products"])
    
    with tab1:
        st.subheader("Financial Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        revenue = SalesManager.calculate_total_revenue(30)
        profit = SalesManager.calculate_profit(30)
        margin = SalesManager.calculate_profit_margin(30)
        inv_value = InventoryManager.calculate_inventory_value()
        
        with col1:
            st.metric("30-Day Revenue", f"₹{revenue:,.0f}")
        with col2:
            st.metric("30-Day Profit", f"₹{profit:,.0f}")
        with col3:
            st.metric("Profit Margin", f"{margin:.1f}%")
        with col4:
            st.metric("Inventory Value", f"₹{inv_value:,.0f}")
    
    with tab2:
        st.subheader("Category Performance")
        try:
            category_data = Analytics.get_category_performance()
            if category_data:
                df = pd.DataFrame(category_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(df, x='category', y='revenue', title="Revenue by Category")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(df, x='category', y='profit', title="Profit by Category", color_discrete_sequence=['#24A148'])
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("Top Performing Products")
        metric = st.radio("Rank by", ["Profit", "Revenue", "Sales Volume"], horizontal=True)
        
        try:
            top_products = Analytics.get_top_products(
                metric={'Profit': 'profit', 'Revenue': 'revenue', 'Sales Volume': 'sales_volume'}[metric],
                limit=10
            )
            if top_products:
                df = pd.DataFrame(top_products)
                fig = px.bar(df, x='product_name', y='value', title=f"Top 10 by {metric}")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "🔮 Forecasting":
    st.title("🔮 Demand Forecasting")
    
    tab1, tab2 = st.tabs(["Forecast", "Recommendations"])
    
    with tab1:
        st.subheader("30-Day Demand Forecast")
        try:
            products = InventoryManager.get_all_products()
            if not products.empty:
                product_id = st.selectbox("Select Product",
                    options=products['product_id'],
                    format_func=lambda x: products[products['product_id']==x]['product_name'].values[0])
                
                forecast = DemandForecaster.forecast_demand(product_id, days=30)
                if forecast:
                    df = pd.DataFrame(forecast)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df['date'], y=df['forecasted_quantity'],
                        fill='tozeroy', name='Forecast'
                    ))
                    fig.add_trace(go.Scatter(
                        x=df['date'], y=df['upper_bound'],
                        fill=None, name='Upper Bound', line=dict(width=0),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=df['date'], y=df['lower_bound'],
                        fill='tonexty', name='Lower Bound', line=dict(width=0),
                        showlegend=False
                    ))
                    
                    fig.update_layout(
                        title="30-Day Demand Forecast",
                        xaxis_title="Date",
                        yaxis_title="Quantity",
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Purchase Recommendations")
        try:
            recommendations = DemandForecaster.get_all_recommendations()
            if recommendations:
                df = pd.DataFrame(recommendations)
                
                for _, row in df.iterrows():
                    with st.container(border=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Product ID:** {row['product_id']}")
                        with col2:
                            st.write(f"**Current Stock:** {row['current_stock']}")
                        with col3:
                            st.write(f"**30-Day Demand:** {row['forecasted_30day_demand']:.0f}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Recommended Qty", f"{int(row['recommended_quantity'])} units")
                        with col2:
                            st.info(row['status'])
            else:
                st.info("No reorder recommendations at this time")
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "⚠️ Alerts":
    st.title("⚠️ System Alerts")
    
    try:
        alerts = Analytics.get_alerts()
        
        if alerts:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                alert_type = st.multiselect("Alert Type", 
                    options=list(set([a['type'] for a in alerts])),
                    default=list(set([a['type'] for a in alerts])))
            with col2:
                severity = st.multiselect("Severity",
                    options=['critical', 'warning', 'info'],
                    default=['critical', 'warning'])
            
            # Filter alerts
            filtered_alerts = [a for a in alerts if a['type'] in alert_type and a['severity'] in severity]
            
            for alert in filtered_alerts:
                if alert['severity'] == 'critical':
                    st.markdown(f"<div class='alert-critical'>{alert['message']}</div>", unsafe_allow_html=True)
                elif alert['severity'] == 'warning':
                    st.markdown(f"<div class='alert-warning'>{alert['message']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='alert-info'>{alert['message']}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.metric("Total Alerts", len(filtered_alerts))
        else:
            st.success("✅ No active alerts! System is healthy.")
    except Exception as e:
        st.error(f"Error: {e}")

elif page == "📥 Restock":
    st.title("📥 Inventory Restocking")
    
    try:
        products = InventoryManager.get_all_products()
        if not products.empty:
            with st.form("restock_form"):
                st.subheader("Add Stock")
                
                product_id = st.selectbox("Select Product",
                    options=products['product_id'],
                    format_func=lambda x: products[products['product_id']==x]['product_name'].values[0])
                
                quantity = st.number_input("Quantity to Add", min_value=1, step=10)
                cost_per_unit = st.number_input("Cost per Unit (₹)", min_value=0.0, step=10.0)
                
                if st.form_submit_button("✅ Restock"):
                    InventoryManager.update_stock(product_id, quantity, 'restock')
                    
                    # Record purchase
                    total_cost = quantity * cost_per_unit
                    query = """
                        INSERT INTO purchases (product_id, quantity_purchased, cost_per_unit, total_cost)
                        VALUES (?, ?, ?, ?)
                    """
                    db.execute_query(query, (product_id, quantity, cost_per_unit, total_cost))
                    
                    st.success(f"✅ Restocked {quantity} units!")
                    st.rerun()
        else:
            st.info("Add products to inventory first")
    except Exception as e:
        st.error(f"Error: {e}")

elif page == "💰 Discounts":
    st.title("💰 Smart Discount Engine")
    
    tab1, tab2 = st.tabs(["Recommendations", "Apply Discount"])
    
    with tab1:
        st.subheader("AI Discount Recommendations")
        try:
            recommendations = DiscountEngine.get_all_recommendations()
            
            if recommendations:
                for rec in recommendations:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**Product ID {rec['product_id']}**")
                            st.write(rec['recommendation'])
                        
                        with col2:
                            urgency_color = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                            st.write(f"**{urgency_color.get(rec['urgency'], '')} {rec['urgency']}**")
                            st.write(f"**Discount:** {rec['discount']}%")
                        
                        with col3:
                            st.metric("Price", f"₹{rec['discounted_price']:.2f}")
                            st.metric("Est. Profit", f"₹{rec['estimated_profit_recovery']:.0f}")
                
                if st.button("📊 Apply All Recommendations"):
                    st.success("Recommendations applied!")
            else:
                st.info("No discount recommendations at this time")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Apply Custom Discount")
        try:
            products = InventoryManager.get_all_products()
            if not products.empty:
                with st.form("discount_form"):
                    product_id = st.selectbox("Product",
                        options=products['product_id'],
                        format_func=lambda x: products[products['product_id']==x]['product_name'].values[0])
                    
                    discount = st.slider("Discount %", 0, 50, 10)
                    reason = st.text_input("Reason for discount")
                    
                    if st.form_submit_button("✅ Apply Discount"):
                        DiscountEngine.apply_discount_recommendation(product_id, discount, reason)
                        st.success(f"✅ {discount}% discount applied!")
                        st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "📋 Reports":
    st.title("📋 Reports & Exports")
    
    tab1, tab2 = st.tabs(["Generate", "View"])
    
    with tab1:
        st.subheader("Generate Reports")
        
        report_type = st.radio("Report Type", 
            ["Inventory Report", "Sales Report", "Financial Report", "Complete Report"])
        
        days = st.slider("Include data from last (days)", 1, 365, 30)
        
        if st.button("📥 Generate Report"):
            try:
                if report_type == "Inventory Report":
                    products = InventoryManager.get_all_products()
                    csv = products.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d')}.csv"
                    )
                
                elif report_type == "Sales Report":
                    sales = SalesManager.get_sales_data(days)
                    csv = sales.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv"
                    )
                
                elif report_type == "Financial Report":
                    kpis = Analytics.get_kpis(days)
                    df = pd.DataFrame([kpis])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"financial_report_{datetime.now().strftime('%Y%m%d')}.csv"
                    )
                
                st.success("✅ Report generated!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("View Reports")
        st.info("📌 Reports are generated on demand from the Generate tab")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    🏪 AI-Driven Retail Intelligence Dashboard | HCL Jigsaw Innovation Challenge<br>
    Built with ❤️ using Streamlit & Python
    </div>
""", unsafe_allow_html=True)
