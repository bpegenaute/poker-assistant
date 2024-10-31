import streamlit as st
from poker.screen_capture import PokerScreenCapture
import json
import time

def create_screen_capture_controls():
    """Create UI controls for browser-based screen capture functionality"""
    st.markdown("### 📸 Screen Capture Settings")
    
    # Initialize screen capture in session state if not exists
    if 'screen_capture' not in st.session_state:
        st.session_state.screen_capture = PokerScreenCapture()
        
    if 'ocr_results' not in st.session_state:
        st.session_state.ocr_results = {}
        
    if 'monitoring_active' not in st.session_state:
        st.session_state.monitoring_active = False

    # Add JavaScript for continuous screen capture
    st.markdown("""
        <script>
        let captureInterval;
        
        async function startContinuousCapture(interval) {
            if (captureInterval) {
                clearInterval(captureInterval);
            }
            
            captureInterval = setInterval(async () => {
                try {
                    const stream = await navigator.mediaDevices.getDisplayMedia({
                        video: { mediaSource: "screen" }
                    });
                    
                    const track = stream.getVideoTracks()[0];
                    const imageCapture = new ImageCapture(track);
                    const bitmap = await imageCapture.grabFrame();
                    
                    const canvas = document.createElement('canvas');
                    canvas.width = bitmap.width;
                    canvas.height = bitmap.height;
                    const context = canvas.getContext('2d');
                    context.drawImage(bitmap, 0, 0);
                    
                    const base64Data = canvas.toDataURL('image/png');
                    
                    // Clean up
                    stream.getTracks().forEach(track => track.stop());
                    
                    // Send data back to Streamlit
                    window.parent.postMessage({
                        type: 'continuous_capture',
                        data: base64Data
                    }, '*');
                    
                } catch (err) {
                    console.error('Screen capture failed:', err);
                    window.parent.postMessage({
                        type: 'screen_capture_error',
                        error: err.message
                    }, '*');
                    clearInterval(captureInterval);
                }
            }, interval);
        }

        function stopContinuousCapture() {
            if (captureInterval) {
                clearInterval(captureInterval);
                captureInterval = null;
            }
        }

        // Add control buttons
        const startBtn = document.createElement('button');
        startBtn.innerText = 'Start Monitoring';
        startBtn.onclick = () => startContinuousCapture(2000);  // 2 second interval
        document.body.appendChild(startBtn);

        const stopBtn = document.createElement('button');
        stopBtn.innerText = 'Stop Monitoring';
        stopBtn.onclick = stopContinuousCapture;
        document.body.appendChild(stopBtn);
        </script>
    """, unsafe_allow_html=True)

    # Calibration section
    st.subheader("Calibration")
    
    # Custom file uploader for template
    template_file = st.file_uploader(
        "Upload template image for calibration",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a screenshot of your poker table to calibrate the screen regions"
    )

    if template_file is not None:
        import base64
        
        # Convert uploaded file to base64
        template_base64 = base64.b64encode(template_file.getvalue()).decode()
        
        if st.button("Calibrate Regions"):
            with st.spinner("Calibrating screen regions..."):
                if st.session_state.screen_capture.calibrate_regions(template_base64):
                    st.success("Screen regions calibrated successfully!")
                else:
                    st.error("Calibration failed. Please try again with a different template.")

    # Monitoring controls
    st.subheader("Continuous Monitoring")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Monitoring", 
                    disabled=not st.session_state.screen_capture.is_calibrated):
            st.session_state.monitoring_active = True
            st.session_state.screen_capture.start_continuous_capture(
                callback=lambda results: st.session_state.update(
                    {'ocr_results': results}
                )
            )
            st.success("Continuous monitoring started!")
            
    with col2:
        if st.button("Stop Monitoring", 
                    disabled=not st.session_state.monitoring_active):
            st.session_state.monitoring_active = False
            st.session_state.screen_capture.stop_continuous_capture()
            st.info("Monitoring stopped.")

    # JavaScript callback handler
    st.markdown("""
        <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'continuous_capture') {
                // Process captured image
                const streamlit = window.parent.streamlit;
                streamlit.setComponentValue({
                    type: 'captured_image',
                    data: event.data.data
                });
            }
        });
        </script>
    """, unsafe_allow_html=True)

    # Process continuous capture results
    if 'captured_image' in st.session_state:
        st.session_state.screen_capture.add_capture_to_queue(
            st.session_state.captured_image
        )

    # Display Live Analysis Results
    if st.session_state.monitoring_active:
        st.subheader("Live Analysis")
        
        # Create placeholder for live updates
        if 'analysis_placeholder' not in st.session_state:
            st.session_state.analysis_placeholder = st.empty()
        
        # Update the analysis display
        with st.session_state.analysis_placeholder.container():
            results = st.session_state.screen_capture.get_last_analysis()
            
            if results:
                col1, col2 = st.columns(2)
                with col1:
                    if 'hole_cards' in results:
                        st.markdown("**Hole Cards**")
                        st.write(results['hole_cards'].get('cards', []))
                    
                    if 'community_cards' in results:
                        st.markdown("**Community Cards**")
                        st.write(results['community_cards'].get('cards', []))
                
                with col2:
                    if 'pot' in results:
                        st.markdown("**Pot Size**")
                        st.write(f"${results['pot'].get('value', 0):.2f}")
                    
                    if 'stack' in results:
                        st.markdown("**Stack Size**")
                        st.write(f"${results['stack'].get('value', 0):.2f}")

    # Help text
    st.markdown("""
        #### How to use continuous monitoring:
        1. Upload a template image and calibrate the regions
        2. Click "Start Monitoring"
        3. Select the poker table window/area
        4. Watch the live analysis results
        5. Click "Stop Monitoring" when finished
    """)
