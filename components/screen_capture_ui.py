import streamlit as st
from poker.screen_capture import PokerScreenCapture
from poker.table_analyzer import TableAnalyzer
import json
import time
import cv2
import numpy as np
from PIL import Image
import io
import base64

def create_screen_capture_controls():
    """Create UI controls for browser-based screen capture functionality"""
    st.markdown("### 📸 Automated Table Analysis")
    
    # Initialize components in session state
    if 'screen_capture' not in st.session_state:
        st.session_state.screen_capture = PokerScreenCapture()
        
    if 'table_analyzer' not in st.session_state:
        st.session_state.table_analyzer = TableAnalyzer()
        
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
        
    if 'monitoring_active' not in st.session_state:
        st.session_state.monitoring_active = False

    # Calibration section with improved wizard
    with st.expander("📊 Calibration Wizard", expanded=not st.session_state.table_analyzer.regions):
        st.markdown("""
        ### Table Calibration Steps:
        1. Upload a clear screenshot of your poker table
        2. Adjust detection regions if needed
        3. Verify calibration results
        """)
        
        # Template upload
        template_file = st.file_uploader(
            "Upload poker table template",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear screenshot of your poker table for calibration"
        )

        if template_file:
            try:
                # Convert uploaded image to numpy array
                image_bytes = template_file.read()
                nparr = np.frombuffer(image_bytes, np.uint8)
                template_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Show template image
                st.image(template_image, caption="Uploaded template", use_column_width=True)
                
                # Calibration button
                if st.button("Calibrate Regions"):
                    with st.spinner("Calibrating regions..."):
                        if st.session_state.table_analyzer.calibrate_regions(template_image):
                            # Test calibration
                            analysis = st.session_state.table_analyzer.analyze_table(template_image)
                            if analysis:
                                st.success("✅ Calibration successful!")
                                st.json(analysis)
                            else:
                                st.error("❌ Calibration failed. Please try a different template.")
                        else:
                            st.error("❌ Calibration failed. Please try a different template.")

    # Monitoring controls
    st.subheader("🔄 Live Monitoring")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Start Monitoring",
            disabled=not st.session_state.table_analyzer.regions,
            type="primary"
        ):
            st.session_state.monitoring_active = True
            st.session_state.screen_capture.start_continuous_capture(
                callback=lambda img: process_captured_frame(img)
            )
            st.success("🎥 Continuous monitoring started!")
            
    with col2:
        if st.button(
            "Stop Monitoring",
            disabled=not st.session_state.monitoring_active,
            type="secondary"
        ):
            st.session_state.monitoring_active = False
            st.session_state.screen_capture.stop_continuous_capture()
            st.info("⏹️ Monitoring stopped.")

    # Live analysis display
    if st.session_state.monitoring_active:
        st.markdown("### 📊 Live Analysis")
        
        # Create placeholders for live updates
        if 'analysis_container' not in st.session_state:
            st.session_state.analysis_container = st.empty()
            
        # Update analysis display
        with st.session_state.analysis_container.container():
            results = st.session_state.analysis_results
            if results:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Position",
                        results.get('position', 'Unknown'),
                        f"Confidence: {results.get('position_confidence', 0):.2%}"
                    )
                    
                    cards = results.get('hole_cards', [])
                    st.metric("Hole Cards", ' '.join(cards) if cards else "None")
                    
                with col2:
                    st.metric(
                        "Pot Size",
                        f"${results.get('pot_size', 0):.2f}",
                        delta=f"Stack: ${results.get('stack_size', 0):.2f}"
                    )
                    
                    community = results.get('community_cards', [])
                    st.metric("Community Cards", ' '.join(community) if community else "None")
                    
                with col3:
                    actions = results.get('actions', {})
                    for action, amount in actions.items():
                        if amount > 0:
                            st.metric(action, f"${amount:.2f}")
                            
                # Show significant changes
                changes = st.session_state.table_analyzer.detect_significant_changes()
                if any(changes.values()):
                    st.markdown("#### 🔔 Recent Changes")
                    for change, occurred in changes.items():
                        if occurred:
                            st.info(f"• {change.replace('_', ' ').title()}")

def process_captured_frame(base64_image: str):
    """Process a captured frame and update analysis"""
    try:
        # Convert base64 to image
        image_data = base64.b64decode(base64_image.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Analyze table
        analysis = st.session_state.table_analyzer.analyze_table(image)
        if analysis:
            st.session_state.analysis_results = analysis
            
            # Record in database if significant changes detected
            changes = st.session_state.table_analyzer.detect_significant_changes()
            if any(changes.values()):
                from poker.database import Database
                db = Database()
                db.record_automated_capture(
                    position=analysis['position'],
                    active_position=analysis['position'],
                    pot_size=analysis['pot_size'],
                    current_bet=max(analysis['actions'].values()),
                    player_stacks={'hero': analysis['stack_size']},
                    detected_cards={
                        'hole_cards': analysis['hole_cards'],
                        'community_cards': analysis['community_cards']
                    },
                    action_history=[{
                        'action': action,
                        'amount': amount
                    } for action, amount in analysis['actions'].items() if amount > 0],
                    confidence_score=analysis['position_confidence']
                )
                db.close()
                
    except Exception as e:
        st.error(f"Error processing frame: {str(e)}")
