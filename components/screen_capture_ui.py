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
    # Initialize components in session state
    if 'screen_capture' not in st.session_state:
        st.session_state.screen_capture = PokerScreenCapture()
        
    if 'table_analyzer' not in st.session_state:
        st.session_state.table_analyzer = TableAnalyzer()
        
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
        
    if 'monitoring_active' not in st.session_state:
        st.session_state.monitoring_active = False

    # Main screen capture interface
    st.title("🎮 Automated Poker Analysis")
    
    # Status indicator with enhanced visibility
    status = "🟢 Active" if st.session_state.monitoring_active else "⚪ Inactive"
    st.markdown(f"""
        <div style='padding: 1rem; background-color: {"#2E7D32" if st.session_state.monitoring_active else "#424242"}; 
                    border-radius: 8px; margin-bottom: 1rem;'>
            <h2 style='margin: 0; color: white;'>System Status: {status}</h2>
        </div>
    """, unsafe_allow_html=True)

    # Control buttons in a prominent position
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button(
            "▶️ Start Monitoring",
            disabled=not st.session_state.table_analyzer.regions or st.session_state.monitoring_active,
            type="primary",
            use_container_width=True
        )
        
    with col2:
        stop_button = st.button(
            "⏹️ Stop Monitoring",
            disabled=not st.session_state.monitoring_active,
            type="secondary",
            use_container_width=True
        )

    # Handle button actions
    if start_button:
        st.session_state.monitoring_active = True
        st.session_state.screen_capture.start_continuous_capture(
            callback=lambda img: process_captured_frame(img)
        )
        st.success("🎥 Table monitoring started!")
        
    if stop_button:
        st.session_state.monitoring_active = False
        st.session_state.screen_capture.stop_continuous_capture()
        st.info("Monitoring stopped.")

    # Only show calibration when not monitoring
    if not st.session_state.monitoring_active:
        # Calibration wizard
        with st.expander("📊 Table Calibration", expanded=not st.session_state.table_analyzer.regions):
            st.markdown("""
            ### Quick Setup Guide:
            1. Select your poker client
            2. Upload a clear table screenshot
            3. Verify region detection
            """)
            
            try:
                # Poker client selection
                client = st.selectbox(
                    "Select Poker Client",
                    ["PokerStars", "GGPoker", "PartyPoker", "888Poker", "Other"],
                    help="Choose your poker client for optimized detection"
                )
                
                # Template upload
                template_file = st.file_uploader(
                    "Upload Table Screenshot",
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload a clear screenshot of your poker table"
                )

                if template_file:
                    # Convert uploaded image to numpy array
                    image_bytes = template_file.read()
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    template_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    # Show template image with detected regions
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.image(template_image, caption="Table Screenshot", use_column_width=True)
                    
                    with col2:
                        if st.button("🎯 Calibrate Regions", type="primary"):
                            with st.spinner("Calibrating..."):
                                if st.session_state.table_analyzer.calibrate_regions(template_image):
                                    analysis = st.session_state.table_analyzer.analyze_table(template_image)
                                    if analysis:
                                        st.success("✅ Calibration successful!")
                                        st.json(analysis)
                                    else:
                                        st.error("❌ Analysis failed. Please try a clearer image.")
                                else:
                                    st.error("❌ Calibration failed. Please try another screenshot.")
            except Exception as e:
                st.error(f"Error during calibration: {str(e)}")

    # Live analysis display (only show when monitoring is active)
    if st.session_state.monitoring_active:
        st.markdown("### 📊 Live Analysis")
        
        if 'analysis_container' not in st.session_state:
            st.session_state.analysis_container = st.empty()
            
        with st.session_state.analysis_container.container():
            results = st.session_state.analysis_results
            if results:
                # Primary info in a clean layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "👥 Position",
                        results.get('position', 'Unknown'),
                        f"Confidence: {results.get('position_confidence', 0):.2%}"
                    )
                    
                    hole_cards = results.get('hole_cards', [])
                    st.metric("🎴 Hole Cards", ' '.join(hole_cards) if hole_cards else "None")
                    
                    community = results.get('community_cards', [])
                    st.metric("🃏 Board", ' '.join(community) if community else "None")
                    
                with col2:
                    st.metric(
                        "💰 Pot Size",
                        f"${results.get('pot_size', 0):.2f}",
                        f"Stack: ${results.get('stack_size', 0):.2f}"
                    )
                    
                    actions = results.get('actions', {})
                    for action, amount in actions.items():
                        if amount > 0:
                            st.metric(
                                f"⚡ {action}",
                                f"${amount:.2f}",
                                delta_color="normal"
                            )
                
                # Show recommendations
                changes = st.session_state.table_analyzer.detect_significant_changes()
                if any(changes.values()):
                    st.markdown("### 💡 Recommendation")
                    from poker.recommendations import RecommendationEngine
                    engine = RecommendationEngine()
                    recommendation = engine.get_recommendation(
                        hole_cards=results.get('hole_cards', []),
                        community_cards=results.get('community_cards', []),
                        position=results.get('position', 'Unknown'),
                        pot_size=results.get('pot_size', 0),
                        to_call=max(results.get('actions', {}).values()),
                        stack_size=results.get('stack_size', 100)
                    )
                    
                    if recommendation:
                        st.success(f"**{recommendation['action']}** ({recommendation['confidence']:.0%} confident)")
                        with st.expander("View Reasoning"):
                            st.markdown(recommendation['reasoning'])

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
                try:
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
                finally:
                    db.close()
                    
    except Exception as e:
        st.error(f"Error processing frame: {str(e)}")
