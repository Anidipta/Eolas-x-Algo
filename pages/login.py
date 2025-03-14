# pages/login.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import json

def show_login():
    st.markdown("# Login to CryptoGridPro")
    
    with st.container():
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("## Welcome Back!")
            
            with st.form("login_form"):
                email = st.text_input("Email Address", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                
                login_button = st.form_submit_button("Login", use_container_width=True)
                
                if login_button:
                    if email and password:
                        try:
                            # Using the FastAPI endpoint for login
                            response = requests.post(
                                "http://localhost:8000/api/login",
                                json={"email": email, "password": password}
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                token = data["access_token"]
                                
                                # Authenticate with Firebase directly
                                try:
                                    # Get user info
                                    user_record = auth.get_user_by_email(email)
                                    
                                    # Set session state
                                    st.session_state.authenticated = True
                                    st.session_state.user_id = user_record.uid
                                    
                                    st.success("Login successful! Redirecting to dashboard...")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Authentication error: {e}")
                            else:
                                st.error("Invalid email or password.")
                        except Exception as e:
                            st.error(f"Login error: {e}")
                    else:
                        st.warning("Please enter your email and password.")
            
            st.markdown("---")
            st.markdown("Don't have an account? [Sign up now](signup)")
        
        with col2:
            st.markdown("## Quick Login")
            st.markdown("Connect with an existing account:")
            
            # Social login buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Google", use_container_width=True):
                    st.info("Google authentication is currently being configured.")
            with col2:
                if st.button("Metamask", use_container_width=True):
                    st.info("Web3 wallet connect is coming soon!")

def show_signup():
    st.markdown("# Create your CryptoGridPro Account")
    
    with st.container():
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("## Join CryptoGridPro")
            
            with st.form("signup_form"):
                name = st.text_input("Full Name", key="signup_name")
                email = st.text_input("Email Address", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
                
                terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="signup_terms")
                
                signup_button = st.form_submit_button("Create Account", use_container_width=True)
                
                if signup_button:
                    if not (name and email and password and password_confirm):
                        st.warning("Please fill in all fields.")
                    elif password != password_confirm:
                        st.error("Passwords do not match.")
                    elif not terms:
                        st.warning("You must agree to the Terms of Service and Privacy Policy.")
                    else:
                        try:
                            # Using the FastAPI endpoint for signup
                            response = requests.post(
                                "http://localhost:8000/api/signup",
                                json={"name": name, "email": email, "password": password}
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                token = data["access_token"]
                                
                                # Get user information
                                user_record = auth.get_user_by_email(email)
                                
                                # Set session state
                                st.session_state.authenticated = True
                                st.session_state.user_id = user_record.uid
                                
                                st.success("Account created successfully! Redirecting to dashboard...")
                                st.rerun()
                            else:
                                st.error("Error creating account. Please try again.")
                        except Exception as e:
                            st.error(f"Signup error: {e}")
            
            st.markdown("---")
            st.markdown("Already have an account? [Login here](login)")
        
        with col2:
            st.markdown("## Benefits")
            st.markdown("""
            - Access to AI-powered grid trading strategies
            - Real-time market signals and alerts
            - Social sentiment analysis
            - Performance tracking and analysis
            - Priority support
            """)