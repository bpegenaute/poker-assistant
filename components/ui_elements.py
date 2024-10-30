import streamlit as st
from typing import List, Tuple

def create_card_selector(key_prefix: str) -> List[str]:
    """Create a card selection widget"""
    cols = st.columns(2)
    
    with cols[0]:
        rank = st.selectbox(
            'Rank',
            [''] + list('23456789TJQKA'),
            key=f'{key_prefix}_rank'
        )
    
    with cols[1]:
        suit = st.selectbox(
            'Suit',
            [''] + list('♣♦♥♠'),
            key=f'{key_prefix}_suit'
        )
    
    if rank and suit:
        suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
        return f"{rank}{suit_map[suit]}"
    return ""

def create_position_input() -> str:
    """Create a position selection widget"""
    return st.selectbox(
        'Position',
        ['BTN', 'CO', 'MP', 'EP', 'BB', 'SB']
    )

def create_stack_input() -> Tuple[float, float, float]:
    """Create stack and betting inputs"""
    cols = st.columns(3)
    
    with cols[0]:
        stack = st.number_input('Stack Size', min_value=0.0, value=100.0)
    
    with cols[1]:
        pot = st.number_input('Pot Size', min_value=0.0, value=0.0)
    
    with cols[2]:
        to_call = st.number_input('To Call', min_value=0.0, value=0.0)
    
    return stack, pot, to_call

def display_recommendation(recommendation: dict):
    """Display the recommendation with styling"""
    action_colors = {
        'RAISE': 'green',
        'CALL': 'blue',
        'FOLD': 'red'
    }
    
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 10px; background-color: {action_colors[recommendation['action']]}20;'>
        <h2 style='color: {action_colors[recommendation['action']]};'>{recommendation['action']}</h2>
        <p>Confidence: {recommendation['confidence']:.1%}</p>
        <pre>{recommendation['reasoning']}</pre>
    </div>
    """, unsafe_allow_html=True)
