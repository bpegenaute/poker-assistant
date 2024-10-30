import streamlit as st
from poker.evaluator import HandEvaluator
from poker.calculator import PokerCalculator
from poker.recommendations import RecommendationEngine
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

def main():
    st.set_page_config(
        page_title="Poker Assistant",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    initialize_session_state()
    inject_custom_css()
    
    # Header section with controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("Poker Assistant")
    with col2:
        st.session_state.minimal_mode = st.toggle('Minimal Mode 🔄', st.session_state.minimal_mode, help="Toggle between full and minimal display")
    with col3:
        st.session_state.window_docked = st.toggle('Dock Window 📌', st.session_state.window_docked, help="Keep window on top")
    
    # Quick Start Guide
    if not st.session_state.minimal_mode:
        create_quick_start_guide()
    
    # Main content
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # 1. Stack Size Section (Top Priority)
    st.markdown('<div class="section-container prominent">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💰 Stack Size</div>', unsafe_allow_html=True)
    stack = create_stack_size_input()
    
    # 2. Position Selection
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎯 Table Position</div>', unsafe_allow_html=True)
    position = create_quick_position_selector()
    
    # 3. Hole Cards Selection
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎴 Your Hand</div>', unsafe_allow_html=True)
    card1, card2 = create_quick_hand_selector()
    if card1 and card2 and card1 != card2:
        st.session_state.hole_cards = [card1, card2]
        if not st.session_state.minimal_mode:
            st.success("Hand selected successfully!")
    
    # 4. Betting Information
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    pot, to_call = create_betting_controls()
    
    # 5. Community Cards
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🃏 Community Cards</div>', unsafe_allow_html=True)
    community_cards = create_community_cards_selector()
    
    # 6. Get Recommendation Button
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
        else:
            st.session_state.loading = True
            st.markdown('<div class="loading">Calculating optimal play...</div>', unsafe_allow_html=True)
            
            engine = RecommendationEngine()
            recommendation = engine.get_recommendation(
                st.session_state.hole_cards,
                community_cards,
                position or 'MP',  # Default to MP if no position selected
                pot,
                to_call,
                stack
            )
            
            st.session_state.loading = False
            display_recommendation(recommendation, st.session_state.minimal_mode)
    
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
