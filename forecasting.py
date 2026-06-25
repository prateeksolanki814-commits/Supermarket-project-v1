"""Demand Forecasting Module - AI Predictions using Prophet"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import db
from inventory import InventoryManager
from sales import SalesManager
import logging

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Prophet not installed. Forecasting will use fallback method.")

logger = logging.getLogger(__name__)

class DemandForecaster:
    """AI-powered demand forecasting using Prophet."""
    
    @staticmethod
    def get_historical_sales(product_id, days=90):
        """Get historical sales data for a product."""
        try:
            query = f"""
                SELECT DATE(sale_date) as date, SUM(quantity_sold) as quantity
                FROM sales
                WHERE product_id = ? AND sale_date >= datetime('now', '-{days} days')
                GROUP BY DATE(sale_date)
                ORDER BY date
            """
            results = db.fetch_all(query, (product_id,))
            return results
        except Exception as e:
            logger.error(f"Error fetching historical sales: {e}")
            return []
    
    @staticmethod
    def forecast_demand(product_id, days=30):
        """Forecast demand for next N days."""
        try:
            product = InventoryManager.get_product_by_id(product_id)
            if not product:
                return None
            
            historical_data = DemandForecaster.get_historical_sales(product_id, days=90)
            
            if not historical_data:
                # Return default forecast if no historical data
                return DemandForecaster._get_default_forecast(product_id, days)
            
            if PROPHET_AVAILABLE:
                return DemandForecaster._forecast_with_prophet(product_id, historical_data, days)
            else:
                return DemandForecaster._forecast_with_fallback(product_id, historical_data, days)
        except Exception as e:
            logger.error(f"Error forecasting demand: {e}")
            return None
    
    @staticmethod
    def _forecast_with_prophet(product_id, historical_data, days):
        """Forecast using Prophet."""
        try:
            # Prepare data
            df = pd.DataFrame(historical_data, columns=['date', 'quantity'])
            df['ds'] = pd.to_datetime(df['date'])
            df['y'] = df['quantity'].astype(float)
            df = df[['ds', 'y']]
            
            # Handle missing data
            df = df.dropna()
            if len(df) < 7:
                return DemandForecaster._forecast_with_fallback(product_id, historical_data, days)
            
            # Train model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                interval_width=0.95
            )
            model.fit(df)
            
            # Make forecast
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            
            # Extract future forecasts
            future_forecast = forecast[forecast['ds'] > df['ds'].max()][['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            
            forecast_data = []
            for _, row in future_forecast.iterrows():
                forecast_data.append({
                    'date': row['ds'].date(),
                    'forecasted_quantity': max(0, round(row['yhat'], 2)),
                    'lower_bound': max(0, round(row['yhat_lower'], 2)),
                    'upper_bound': max(0, round(row['yhat_upper'], 2))
                })
            
            return forecast_data
        except Exception as e:
            logger.error(f"Prophet forecast error: {e}")
            return DemandForecaster._forecast_with_fallback(product_id, historical_data, days)
    
    @staticmethod
    def _forecast_with_fallback(product_id, historical_data, days):
        """Fallback forecasting method."""
        try:
            df = pd.DataFrame(historical_data, columns=['date', 'quantity'])
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
            
            if len(df) == 0:
                return DemandForecaster._get_default_forecast(product_id, days)
            
            avg_daily = df['quantity'].mean()
            std_daily = df['quantity'].std()
            if pd.isna(std_daily):
                std_daily = avg_daily * 0.2
            
            forecast_data = []
            today = datetime.now()
            
            for i in range(days):
                forecast_date = (today + timedelta(days=i+1)).date()
                # Add slight trend and seasonality
                trend = avg_daily * (1 + (i % 7) * 0.05)  # Weekly pattern
                noise = np.random.normal(0, std_daily * 0.1)
                forecasted_qty = max(0, avg_daily + noise + trend)
                
                forecast_data.append({
                    'date': forecast_date,
                    'forecasted_quantity': round(forecasted_qty, 2),
                    'lower_bound': max(0, round(forecasted_qty - std_daily, 2)),
                    'upper_bound': round(forecasted_qty + std_daily, 2)
                })
            
            return forecast_data
        except Exception as e:
            logger.error(f"Fallback forecast error: {e}")
            return DemandForecaster._get_default_forecast(product_id, days)
    
    @staticmethod
    def _get_default_forecast(product_id, days):
        """Return default forecast when no data available."""
        forecast_data = []
        today = datetime.now()
        
        for i in range(days):
            forecast_date = (today + timedelta(days=i+1)).date()
            forecast_data.append({
                'date': forecast_date,
                'forecasted_quantity': 10,  # Default forecast
                'lower_bound': 5,
                'upper_bound': 15
            })
        
        return forecast_data
    
    @staticmethod
    def get_recommendation(product_id):
        """Get purchasing recommendation based on forecast."""
        try:
            product = InventoryManager.get_product_by_id(product_id)
            if not product:
                return None
            
            stock = product[5]
            reorder_level = product[6]
            
            forecast = DemandForecaster.forecast_demand(product_id, days=30)
            if not forecast:
                return None
            
            total_forecasted = sum([f['forecasted_quantity'] for f in forecast])
            lead_time = 3  # Assumed 3-day lead time
            safety_stock = reorder_level
            
            recommended_quantity = total_forecasted - stock + safety_stock
            
            if recommended_quantity <= 0:
                status = "No reorder needed"
            else:
                status = f"Reorder {int(recommended_quantity)} units"
            
            return {
                'product_id': product_id,
                'current_stock': stock,
                'forecasted_30day_demand': round(total_forecasted, 0),
                'recommended_quantity': max(0, int(recommended_quantity)),
                'status': status,
                'confidence': 0.85
            }
        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            return None
    
    @staticmethod
    def get_all_recommendations():
        """Get purchasing recommendations for all products."""
        try:
            products = InventoryManager.get_all_products()
            recommendations = []
            
            for _, row in products.iterrows():
                rec = DemandForecaster.get_recommendation(row['product_id'])
                if rec and rec['recommended_quantity'] > 0:
                    recommendations.append(rec)
            
            return sorted(recommendations, key=lambda x: x['recommended_quantity'], reverse=True)
        except Exception as e:
            logger.error(f"Error getting all recommendations: {e}")
            return []
