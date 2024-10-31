import streamlit as st
from poker.screen_capture import PokerScreenCapture
import tempfile
import os
from PIL import Image
import io

def create_screen_capture_controls():
    """Create UI controls for screen capture functionality"""
    st.markdown("### 📸 Screen Capture Settings")
    
    # Initialize screen capture in session state if not exists
    if 'screen_capture' not in st.session_state:
        st.session_state.screen_capture = PokerScreenCapture()
        
    if 'ocr_results' not in st.session_state:
        st.session_state.ocr_results = {}
    
    # Calibration section
    st.subheader("Calibration")
    uploaded_file = st.file_uploader(
        "Upload template image for calibration",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a screenshot of your poker table to calibrate the screen regions"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            template_path = tmp_file.name
        
        if st.button("Calibrate Regions"):
            with st.spinner("Calibrating screen regions..."):
                if st.session_state.screen_capture.calibrate_regions(template_path):
                    st.success("Screen regions calibrated successfully!")
                else:
                    st.error("Calibration failed. Please try again with a different template.")
        
        # Clean up temporary file
        os.unlink(template_path)
    
    # Region preview section
    if st.session_state.screen_capture.is_calibrated:
        st.subheader("Region Preview")
        
        if st.button("Capture and Analyze Current View"):
            cols = st.columns(len(st.session_state.screen_capture.regions))
            
            for i, (region_name, _) in enumerate(st.session_state.screen_capture.regions.items()):
                with cols[i]:
                    st.markdown(f"**{region_name.replace('_', ' ').title()}**")
                    img = st.session_state.screen_capture.capture_region(region_name)
                    if img:
                        # Process and analyze the image
                        analysis = st.session_state.screen_capture.analyze_region(region_name, img)
                        st.session_state.ocr_results[region_name] = analysis
                        
                        # Convert PIL image to bytes for streamlit
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        st.image(buf.getvalue(), use_column_width=True)
                        
                        # Display OCR results
                        if 'cards' in analysis:
                            st.write("Detected Cards:", ', '.join(analysis['cards']))
                        elif 'value' in analysis:
                            st.write(f"Detected Value: {analysis['value']:.2f}")
                    else:
                        st.error("Failed to capture region")
    
    # Display OCR Results
    if st.session_state.ocr_results:
        st.subheader("OCR Analysis Results")
        
        col1, col2 = st.columns(2)
        with col1:
            if 'hole_cards' in st.session_state.ocr_results:
                st.markdown("**Hole Cards**")
                st.write(st.session_state.ocr_results['hole_cards'].get('cards', []))
            
            if 'community_cards' in st.session_state.ocr_results:
                st.markdown("**Community Cards**")
                st.write(st.session_state.ocr_results['community_cards'].get('cards', []))
        
        with col2:
            if 'pot' in st.session_state.ocr_results:
                st.markdown("**Pot Size**")
                st.write(f"${st.session_state.ocr_results['pot'].get('value', 0):.2f}")
            
            if 'stack' in st.session_state.ocr_results:
                st.markdown("**Stack Size**")
                st.write(f"${st.session_state.ocr_results['stack'].get('value', 0):.2f}")
    
    # Monitoring controls
    st.subheader("Continuous Monitoring")
    col1, col2 = st.columns(2)
    
    with col1:
        monitoring_interval = st.slider(
            "Monitoring Interval (seconds)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="How frequently to check for changes in the poker table"
        )
    
    with col2:
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if st.button(
            "Start Monitoring" if not st.session_state.monitoring_active else "Stop Monitoring",
            type="primary"
        ):
            st.session_state.monitoring_active = not st.session_state.monitoring_active
    
    if st.session_state.monitoring_active:
        st.markdown("🔴 **Monitoring Active**")
        
        # Create placeholder for live updates
        if 'monitor_placeholder' not in st.session_state:
            st.session_state.monitor_placeholder = st.empty()
            
        def update_callback(region_name: str, analysis: dict):
            """Callback for monitor updates"""
            with st.session_state.monitor_placeholder:
                st.markdown(f"**Change detected in {region_name}**")
                if 'cards' in analysis:
                    st.write(f"Cards: {', '.join(analysis['cards'])}")
                elif 'value' in analysis:
                    st.write(f"Value: ${analysis['value']:.2f}")
                st.session_state.ocr_results[region_name] = analysis
        
        # Start monitoring in a separate thread
        try:
            st.session_state.screen_capture.monitor_poker_table(
                callback=update_callback,
                interval=monitoring_interval
            )
        except Exception as e:
            st.error(f"Monitoring error: {str(e)}")
            st.session_state.monitoring_active = False
