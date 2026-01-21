import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from time import sleep

# --- Configuration ---
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Inventory Management System", layout="wide")
st.title("📦 Inventory Management System")

# --- Helper Functions ---
def get_vendors():
    try:
        response = requests.get(f"{API_URL}/vendors/")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend. Is the FastAPI server running?")
    return []

def get_products():
    try:
        response = requests.get(f"{API_URL}/products/")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend. Is the FastAPI server running?")
    return []

def get_low_stock(threshold=10):
    try:
        response = requests.get(f"{API_URL}/reports/low-stock", params={"threshold": threshold})
        if response.status_code == 200:
            return response.json()
    except:
        return []

# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Vendors", "Products", "Transactions", "Reports"])

# --- Dashboard ---
if page == "Dashboard":
    st.header("Dashboard")
    
    vendors = get_vendors()
    products = get_products()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Vendors", len(vendors))
    
    with col2:
        st.metric("Total Products", len(products))
        
    with col3:
        low_stock_count = len(get_low_stock())
        st.metric("Low Stock Items", low_stock_count, delta_color="inverse" if low_stock_count > 0 else "normal")

# --- Vendors ---
elif page == "Vendors":
    st.header("Vendor Management")
    
    tab1, tab2 = st.tabs(["List Vendors", "Add Vendor"])
    
    with tab1:
        vendors = get_vendors()
        if vendors:
            df = pd.DataFrame(vendors)
            
            st.dataframe(df[['id', 'name', 'contact_email', 'phone']], use_container_width=True)
            
            st.subheader("Delete Vendor")
            vendor_to_delete = st.selectbox("Select Vendor to Delete", vendors, format_func=lambda x: f"{x['name']} (ID: {x['id']})")
            if st.button("Delete Vendor"):
                try:
                    res = requests.delete(f"{API_URL}/vendors/{vendor_to_delete['id']}")
                    if res.status_code == 200:
                        st.success("Vendor deleted successfully!")
                        sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete vendor.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No vendors found.")
            
    with tab2:
        with st.form("add_vendor_form"):
            name = st.text_input("Vendor Name")
            email = st.text_input("Contact Email")
            phone = st.text_input("Phone Number")
            submit = st.form_submit_button("Add Vendor")
            
            if submit:
                if name:
                    payload = {"name": name, "contact_email": email, "phone": phone}
                    res = requests.post(f"{API_URL}/vendors/", json=payload)
                    if res.status_code == 200:
                        st.success(f"Vendor '{name}' added!")
                        sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to add vendor.")
                else:
                    st.warning("Vendor Name is required.")

# --- Products ---
elif page == "Products":
    st.header("Product Management")
    
    vendors = get_vendors()
    
    tab1, tab2 = st.tabs(["List Products", "Add Product"])
    
    with tab1:
        products = get_products()
        if products:

            vendor_map = {v['id']: v['name'] for v in vendors}
            
            display_products = []
            for p in products:
                p_copy = p.copy()
                p_copy['vendor_name'] = vendor_map.get(p['vendor_id'], 'Unknown')
                display_products.append(p_copy)

            df = pd.DataFrame(display_products)
            st.dataframe(df[['id', 'name', 'description', 'price', 'quantity', 'vendor_id', 'vendor_name']], use_container_width=True)
            
            # Delete Product
            st.subheader("Delete Products")
            products_to_delete = st.selectbox("Select Product to Delete", products, format_func=lambda x: f"{x['name']} (ID: {x['id']})")
            if st.button("Delete Product"):
                try:
                    res = requests.delete(f"{API_URL}/products/{products_to_delete['id']}")
                    if res.status_code == 200:
                        st.success("Product deleted successfully!")
                        sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete product.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No products found.")
            
    with tab2:
        if vendors:
            with st.form("add_product_form"):
                name = st.text_input("Product Name")
                desc = st.text_area("Description")
                price = st.number_input("Price", min_value=0.0, step=0.01)
                quantity = st.number_input("Initial Quantity", min_value=0, step=1)
                vendor_sel = st.selectbox("Vendor", vendors, format_func=lambda x: x['name'])
                
                submit = st.form_submit_button("Add Product")
                
                if submit:
                    payload = {
                        "name": name,
                        "description": desc,
                        "price": price,
                        "quantity": quantity,
                        "vendor_id": vendor_sel['id']
                    }
                    res = requests.post(f"{API_URL}/products/", json=payload)
                    if res.status_code == 200:
                        st.success(f"Product '{name}' added!")
                        sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to add product.")
        else:
            st.warning("You must add a vendor before adding products.")

# --- Transactions ---
elif page == "Transactions":
    st.header("Process Transaction")
    
    products = get_products()
    vendors = get_vendors()
    
    if products and vendors:
        with st.form("transaction_form"):
            st.subheader("New Transaction")
            product_sel = st.selectbox("Select Product", products, format_func=lambda x: f"{x['name']} (Stock: {x['quantity']})")
            
            quantity = st.number_input("Quantity (Positive for Restock, Negative for Sale)", step=1)
            
            submit = st.form_submit_button("Process Transaction")
            
            if submit:
                if quantity == 0:
                    st.error("Quantity cannot be 0")
                elif product_sel:
                    # Check stock for sales
                    if quantity < 0 and (product_sel['quantity'] + quantity < 0):
                        st.error(f"Insufficient stock! Current: {product_sel['quantity']}")
                    else:
                        payload = {
                            "product_id": product_sel['id'],
                            "vendor_id": product_sel['vendor_id'],
                            "quantity": quantity
                        }
                        
                        res = requests.post(f"{API_URL}/transactions/", json=payload)
                        if res.status_code == 200:
                            st.success("Transaction recorded successfully!")
                            st.info(f"New Stock Level: {product_sel['quantity'] + quantity}")
                            sleep(2)
                            st.rerun()
                        else:
                            st.error(f"Transaction failed: {res.text}")
        
        st.divider()
        st.subheader("Transaction History")
        try:
            res = requests.get(f"{API_URL}/transactions/")
            if res.status_code == 200:
                trans_data = res.json()
                if trans_data:
                    df = pd.DataFrame(trans_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No transactions yet.")
        except:
            st.error("Could not fetch history.")

    else:
        st.warning("Add products and vendors first.")

# --- Reports ---
elif page == "Reports":
    st.header("Reports & System")
    
    st.subheader("Low Stock Alert")
    threshold = st.slider("Low Stock Threshold", 5, 50, 10)
    low_stock_items = get_low_stock(threshold)
    
    if low_stock_items:
        st.error(f"Found {len(low_stock_items)} items below threshold!")
        df = pd.DataFrame(low_stock_items)
        st.dataframe(df, use_container_width=True)
    else:
        st.success("No items are low on stock.")
        
    st.divider()
    st.subheader("System Backup")
    if st.button("Download Backup JSON"):
        try:
            res = requests.get(f"{API_URL}/system/backup")
            if res.status_code == 200:
                st.download_button(
                    label="Click to Download",
                    data=res.text,
                    file_name=f"inventory_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        except Exception as e:
            st.error(f"Backup failed: {e}")
