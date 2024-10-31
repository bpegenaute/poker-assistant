import streamlit as st
from poker.screen_capture import PokerScreenCapture
import json

def create_screen_capture_controls():
    """Create UI controls for browser-based screen capture functionality"""
    st.markdown("### 📸 Screen Capture Settings")
    
    # Initialize screen capture in session state if not exists
    if 'screen_capture' not in st.session_state:
        st.session_state.screen_capture = PokerScreenCapture()
        
    if 'ocr_results' not in st.session_state:
        st.session_state.ocr_results = {}

    # Add JavaScript for screen capture
    st.markdown("""
        <script>
        async function captureScreen() {
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
                    type: 'screen_capture',
                    data: base64Data
                }, '*');
                
            } catch (err) {
                console.error('Screen capture failed:', err);
                window.parent.postMessage({
                    type: 'screen_capture_error',
                    error: err.message
                }, '*');
            }
        }

        // Add capture button
        const captureBtn = document.createElement('button');
        captureBtn.innerText = 'Capture Screen';
        captureBtn.onclick = captureScreen;
        document.body.appendChild(captureBtn);
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

    # Region preview section
    if st.session_state.screen_capture.is_calibrated:
        st.subheader("Region Preview")
        
        # JavaScript callback handler
        st.markdown("""
            <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'screen_capture') {
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

        if 'captured_image' in st.session_state:
            image_data = st.session_state.captured_image
            for region_name, region in st.session_state.screen_capture.regions.items():
                st.markdown(f"**{region_name.replace('_', ' ').title()}**")
                
                # Process region
                result = st.session_state.screen_capture.process_captured_image(
                    image_data, region_name
                )
                st.session_state.ocr_results[region_name] = result
                
                # Display results
                if 'cards' in result:
                    st.write("Detected Cards:", ', '.join(result['cards']))
                elif 'value' in result:
                    st.write(f"Detected Value: {result['value']:.2f}")
                elif 'error' in result:
                    st.error(f"Error processing region: {result['error']}")

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

    # Help text
    st.markdown("""
        #### How to use screen capture:
        1. Upload a template image to calibrate the regions
        2. Click the "Capture Screen" button
        3. Select the poker table window/area
        4. Wait for the analysis results
    """)
