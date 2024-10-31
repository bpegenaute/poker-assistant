import streamlit as st
from poker.evaluator import HandEvaluator
from poker.calculator import PokerCalculator
from poker.recommendations import RecommendationEngine
from poker.ai_analysis import AIAnalysis
from utils.monitoring import monitor
from components.ui_elements import (
    inject_custom_css,
    create_quick_start_guide,
    create_stack_size_input,
    create_quick_position_selector,
    create_quick_hand_selector,
    create_betting_controls,
    create_community_cards_selector,
    display_recommendation,
    get_street_name
)
from components.tournament_ui import create_tournament_controls
from components.screen_capture_ui import create_screen_capture_controls
import atexit

def initialize_session_state():
    """Initialize session state variables"""
    if 'hole_cards' not in st.session_state:
        st.session_state.hole_cards = []
    if 'minimal_mode' not in st.session_state:
        st.session_state.minimal_mode = False
    if 'window_docked' not in st.session_state:
        st.session_state.window_docked = False
    if 'loading' not in st.session_state:
        st.session_state.loading = False
    if 'stack_size' not in st.session_state:
        st.session_state.stack_size = 100.0
    if 'selected_position' not in st.session_state:
        st.session_state.selected_position = None
    if 'player_id' not in st.session_state:
        st.session_state.player_id = "default_player"
    if 'screen_capture_enabled' not in st.session_state:
        st.session_state.screen_capture_enabled = False
    if 'automated_mode' not in st.session_state:
        st.session_state.automated_mode = False

def display_player_profile():
    """Display player profile and analysis"""
    if st.session_state.player_id:
        ai_analyzer = AIAnalysis()
        profile_data = ai_analyzer.update_player_profile(st.session_state.player_id)
        
        if 'error' not in profile_data:
            st.markdown("### 📊 Player Profile Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Hands", profile_data['stats']['total_hands'])
                st.metric("Win Rate", f"{profile_data['stats'].get('win_rate', 0):.1%}")
            with col2:
                st.metric("Profit/Loss", f"${profile_data['stats']['profit_loss']:.2f}")
                st.metric("Showdown Frequency", f"{profile_data['stats']['showdown_frequency']:.1%}")
            
            with st.expander("🤖 AI Analysis", expanded=False):
                if 'analysis' in profile_data:
                    st.markdown(profile_data['analysis'].get('analysis', ''))

def cleanup():
    """Cleanup function to stop monitoring when the app exits"""
    monitor.stop_monitoring()

def main():
    # Start monitoring
    monitor.start_monitoring()
    atexit.register(cleanup)
    
    st.set_page_config(
        page_title="Poker Assistant",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    initialize_session_state()
    inject_custom_css()
    
    # Header section with controls
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    with col1:
        st.title("Poker Assistant")
    with col2:
        st.session_state.minimal_mode = st.toggle('Minimal Mode 🔄', st.session_state.minimal_mode)
    with col3:
        st.session_state.window_docked = st.toggle('Dock Window 📌', st.session_state.window_docked)
    with col4:
        st.session_state.automated_mode = st.toggle('Automated Mode 🤖', st.session_state.automated_mode)
    with col5:
        st.session_state.screen_capture_enabled = st.toggle('Screen Capture 📸', st.session_state.screen_capture_enabled)
    
    # Display mode indicator
    if st.session_state.automated_mode:
        st.markdown("""
            <div style='padding: 1rem; background-color: #2E7D32; border-radius: 8px; margin-bottom: 1rem;'>
                <h3 style='margin: 0; color: white;'>🤖 Automated Analysis Mode Active</h3>
                <p style='margin: 0.5rem 0 0 0; color: #E8F5E9;'>
                    Screen capture and AI analysis are running. Manual controls are hidden.
                    Toggle 'Automated Mode' off to return to manual input mode.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    if not st.session_state.minimal_mode and not st.session_state.automated_mode:
        create_quick_start_guide()
        display_player_profile()
    
    # Screen Capture Interface (when enabled)
    if st.session_state.screen_capture_enabled and st.session_state.automated_mode:
        create_screen_capture_controls()
    
    # Manual Input Interface (when automated mode is off)
    if not st.session_state.automated_mode:
        # Tournament Controls
        tournament_info = create_tournament_controls()
        
        # Stack Size Section
        st.markdown('<div class="section-container prominent">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 Stack Size</div>', unsafe_allow_html=True)
        stack = create_stack_size_input()
        
        # Position Selection
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Table Position</div>', unsafe_allow_html=True)
        position = create_quick_position_selector()
        
        # Hole Cards Selection
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎴 Your Hand</div>', unsafe_allow_html=True)
        card1, card2 = create_quick_hand_selector()
        if card1 and card2 and card1 != card2:
            st.session_state.hole_cards = [card1, card2]
            if not st.session_state.minimal_mode:
                st.success("Hand selected successfully!")
        
        # Betting Information
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        pot, to_call = create_betting_controls()
        
        # Community Cards
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🃏 Community Cards</div>', unsafe_allow_html=True)
        community_cards = create_community_cards_selector()
        
        # Get Recommendation Button
        street = get_street_name(community_cards)
        rec_button_text = f"Get {street} Play Recommendation 🎯"
        
        st.markdown('<div class="recommendation-button-container">', unsafe_allow_html=True)
        get_rec = st.button(
            rec_button_text,
            type="primary",
            key='get_rec',
            help=f"Calculate the optimal {street.lower()} play (Enter)",
            use_container_width=True
        )
        
        if get_rec or st.session_state.get('enter_pressed', False):
            if not st.session_state.hole_cards:
                st.error("⚠️ Please select your hole cards first!")
            elif not position:
                st.error("⚠️ Please select your position at the table!")
            else:
                st.session_state.loading = True
                st.markdown('<div class="loading">Calculating optimal play...</div>', unsafe_allow_html=True)
                
                engine = RecommendationEngine()
                recommendation = engine.get_recommendation(
                    st.session_state.hole_cards,
                    community_cards,
                    position,
                    pot,
                    to_call,
                    stack,
                    tournament_info=tournament_info
                )
                
                st.session_state.loading = False
                display_recommendation(recommendation, st.session_state.minimal_mode)
                
                # Record the hand in the database
                ai_analyzer = AIAnalysis()
                ai_analyzer.db.record_hand(
                    position=position,
                    hole_cards=st.session_state.hole_cards,
                    community_cards=community_cards,
                    action_taken=recommendation['action'],
                    pot_size=pot,
                    stack_size=stack
                )
    
        # Statistics section
        if not st.session_state.minimal_mode and st.session_state.hole_cards:
            with st.expander("📊 Detailed Statistics", expanded=False):
                evaluator = HandEvaluator()
                calculator = PokerCalculator()
                
                strength = evaluator.evaluate_hand_strength(
                    st.session_state.hole_cards,
                    community_cards
                )
                
                pot_odds = calculator.calculate_pot_odds(to_call, pot)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Hand Strength 💪", f"{strength:.1%}")
                    st.metric("Pot Odds 🎲", f"{pot_odds:.1%}")
                
                if len(community_cards) < 5:
                    with col2:
                        pos_pot, neg_pot = evaluator.calculate_hand_potential(
                            st.session_state.hole_cards,
                            community_cards
                        )
                        st.metric("Positive Potential 📈", f"{pos_pot:.1%}")
                        st.metric("Negative Potential 📉", f"{neg_pot:.1%}")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
