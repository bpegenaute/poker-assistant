import streamlit as st
from typing import List, Tuple

def inject_custom_css():
    """Inject custom CSS for better UI appearance"""
    st.markdown("""
        <style>
        /* Make select boxes wider */
        .stSelectbox {
            min-width: 200px !important;
        }
        
        /* Improve select box appearance */
        .stSelectbox > div > div {
            padding: 8px !important;
        }
        
        /* Add some spacing between elements */
        .element-container {
            margin-bottom: 1rem;
        }
        
        /* Style card selectors */
        .card-selector {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def create_card_selector(key_prefix: str) -> str:
    """Create a card selection widget"""
    st.markdown(f'<div class="card-selector">', unsafe_allow_html=True)
    
    cols = st.columns(2)
    
    with cols[0]:
        rank = st.selectbox(
            'Rank',
            [''] + list('23456789TJQKA'),
            key=f'{key_prefix}_rank',
            format_func=lambda x: x if x else 'Select Rank'
        )
    
    with cols[1]:
        suit = st.selectbox(
            'Suit',
            [''] + list('♣♦♥♠'),
            key=f'{key_prefix}_suit',
            format_func=lambda x: x if x else 'Select Suit'
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if rank and suit:
        suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
        return f"{rank}{suit_map[suit]}"
    return ""

def create_position_input() -> str:
    """Create a position selection widget"""
    st.markdown('<div style="margin: 1rem 0;">', unsafe_allow_html=True)
    position = st.selectbox(
        'Position',
        ['BTN', 'CO', 'MP', 'EP', 'BB', 'SB'],
        format_func=lambda x: {'BTN': 'Button', 'CO': 'Cut-off', 'MP': 'Middle Position',
                             'EP': 'Early Position', 'BB': 'Big Blind', 'SB': 'Small Blind'}[x]
    )
    st.markdown('</div>', unsafe_allow_html=True)
    return position

def create_stack_input() -> Tuple[float, float, float]:
    """Create stack and betting inputs"""
    st.markdown('<div style="margin: 1rem 0;">', unsafe_allow_html=True)
    cols = st.columns(3)
    
    with cols[0]:
        stack = st.number_input('Stack Size ($)', min_value=0.0, value=100.0, step=1.0)
    
    with cols[1]:
        pot = st.number_input('Pot Size ($)', min_value=0.0, value=0.0, step=1.0)
    
    with cols[2]:
        to_call = st.number_input('To Call ($)', min_value=0.0, value=0.0, step=1.0)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return stack, pot, to_call

def display_recommendation(recommendation: dict):
    """Display the recommendation with styling"""
    action_colors = {
        'RAISE': '#28a745',
        'CALL': '#007bff',
        'FOLD': '#dc3545'
    }
    
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 10px; background-color: {action_colors[recommendation['action']]}20;
                border: 1px solid {action_colors[recommendation['action']]}'>
        <h2 style='color: {action_colors[recommendation['action']]};'>{recommendation['action']}</h2>
        <p style='font-size: 1.2em;'>Confidence: {recommendation['confidence']:.1%}</p>
        <div style='background-color: white; padding: 15px; border-radius: 5px;'>
            {recommendation['reasoning']}
        </div>
    </div>
    """, unsafe_allow_html=True)
