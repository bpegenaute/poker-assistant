import streamlit as st
from typing import List, Tuple
import json

def inject_custom_css():
    """Inject custom CSS for better UI appearance"""
    st.markdown("""
        <style>
        /* High contrast theme */
        :root {
            --primary-color: #1E88E5;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --background-color: #1E1E1E;
            --text-color: #FFFFFF;
        }

        /* Compact layout */
        .main {
            padding: 1rem !important;
        }

        /* Card styles */
        .card {
            background-color: #2D2D2D;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #404040;
        }

        /* Button styles */
        .quick-button {
            background-color: var(--primary-color);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            margin: 0.25rem;
            cursor: pointer;
            display: inline-block;
            border: none;
            font-size: 14px;
            transition: background-color 0.2s;
        }

        .quick-button:hover {
            background-color: var(--success-color);
        }

        .preset-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            justify-content: center;
        }

        /* Minimal mode styles */
        .minimal-mode .non-essential {
            display: none !important;
        }

        .minimal-mode .card {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }

        /* Action colors */
        .action-raise { color: var(--success-color) !important; }
        .action-call { color: var(--primary-color) !important; }
        .action-fold { color: var(--danger-color) !important; }

        /* Keyboard shortcut hints */
        .shortcut-hint {
            position: absolute;
            right: 8px;
            top: 8px;
            background: rgba(255,255,255,0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }

        /* Compact inputs */
        .compact-input {
            max-width: 120px !important;
        }

        .stSelectbox {
            min-width: 120px !important;
        }
        </style>

        <script>
        function setToCall(button, multiplier) {
            const pot = parseFloat(document.querySelector('#pot_size').value) || 0;
            const toCallInput = document.querySelector('#to_call');
            if (toCallInput) {
                toCallInput.value = (pot * multiplier).toFixed(2);
                toCallInput.dispatchEvent(new Event('input'));
            }
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                document.querySelector('button[data-testid="get_rec"]')?.click();
            } else if (e.key === 'Escape') {
                window.streamlit.setComponentValue('clear_selections', true);
            }
        });
        </script>
    """, unsafe_allow_html=True)

def create_quick_hand_selector() -> Tuple[str, str]:
    """Create a quick hand selection interface"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    cols = st.columns([3, 3, 1])
    
    with cols[0]:
        rank1 = st.selectbox(
            'Card 1',
            [''] + list('23456789TJQKA'),
            key='quick_rank1',
            format_func=lambda x: x if x else 'Rank'
        )
        suit1 = st.selectbox(
            'Suit 1',
            [''] + list('♣♦♥♠'),
            key='quick_suit1',
            format_func=lambda x: x if x else 'Suit',
            label_visibility='collapsed'
        )
    
    with cols[1]:
        rank2 = st.selectbox(
            'Card 2',
            [''] + list('23456789TJQKA'),
            key='quick_rank2',
            format_func=lambda x: x if x else 'Rank'
        )
        suit2 = st.selectbox(
            'Suit 2',
            [''] + list('♣♦♥♠'),
            key='quick_suit2',
            format_func=lambda x: x if x else 'Suit',
            label_visibility='collapsed'
        )

    with cols[2]:
        st.markdown('<div class="shortcut-hint">1-9, T, J, Q, K, A</div>', unsafe_allow_html=True)
        if st.button('Clear', key='clear_hand'):
            return "", ""

    st.markdown('</div>', unsafe_allow_html=True)
    
    if rank1 and suit1 and rank2 and suit2:
        suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
        return f"{rank1}{suit_map[suit1]}", f"{rank2}{suit_map[suit2]}"
    return "", ""

def create_community_cards_selector() -> List[str]:
    """Create a single-line community cards selector"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    cols = st.columns(5)
    community_cards = []
    
    for i in range(5):
        with cols[i]:
            rank = st.selectbox(
                f'Card {i+1}',
                [''] + list('23456789TJQKA'),
                key=f'comm_rank{i}'
            )
            suit = st.selectbox(
                f'Suit {i+1}',
                [''] + list('♣♦♥♠'),
                key=f'comm_suit{i}',
                label_visibility='collapsed'
            )
            
            if rank and suit:
                suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
                card = f"{rank}{suit_map[suit]}"
                community_cards.append(card)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return community_cards

def create_betting_controls() -> Tuple[float, float, float]:
    """Create compact betting controls with presets"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Create a single row of columns for inputs
    cols = st.columns([2, 2, 2])
    
    with cols[0]:
        stack = st.number_input('Stack', min_value=0.0, value=100.0, step=1.0, key='stack_size')
        
    with cols[1]:
        pot = st.number_input('Pot', min_value=0.0, value=0.0, step=1.0, key='pot_size')
        
    with cols[2]:
        to_call = st.number_input('To Call', min_value=0.0, value=0.0, step=1.0, key='to_call')
    
    # Add preset buttons using CSS flexbox
    st.markdown('''
        <div class="preset-buttons">
            <button class="quick-button" onclick="setToCall(this, 0.5)">½ Pot</button>
            <button class="quick-button" onclick="setToCall(this, 0.75)">¾ Pot</button>
            <button class="quick-button" onclick="setToCall(this, 1.0)">Pot</button>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return stack, pot, to_call

def create_quick_position_selector() -> str:
    """Create a quick position selector with buttons"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    positions = {
        'BTN': 'Button',
        'CO': 'Cutoff',
        'MP': 'Middle',
        'EP': 'Early',
        'BB': 'Big Blind',
        'SB': 'Small Blind'
    }
    
    cols = st.columns(len(positions))
    selected_position = None
    
    for i, (pos, label) in enumerate(positions.items()):
        with cols[i]:
            if st.button(label, key=f'pos_{pos}'):
                selected_position = pos
    
    st.markdown('</div>', unsafe_allow_html=True)
    return selected_position

def display_recommendation(recommendation: dict, minimal: bool = False):
    """Display the recommendation with styling"""
    action_colors = {
        'RAISE': '#28a745',
        'CALL': '#007bff',
        'FOLD': '#dc3545'
    }
    
    if minimal:
        st.markdown(f"""
        <div style='padding: 10px; border-radius: 5px; background-color: {action_colors[recommendation['action']]}20;
                    border: 1px solid {action_colors[recommendation['action']]}'>
            <h3 style='color: {action_colors[recommendation['action']]}; margin: 0;'>
                {recommendation['action']} ({recommendation['confidence']:.0%})
            </h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='padding: 20px; border-radius: 10px; background-color: {action_colors[recommendation['action']]}20;
                    border: 1px solid {action_colors[recommendation['action']]}'>
            <h2 style='color: {action_colors[recommendation['action']]};'>{recommendation['action']}</h2>
            <p style='font-size: 1.2em;'>Confidence: {recommendation['confidence']:.1%}</p>
            <div style='background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px;'>
                {recommendation['reasoning']}
            </div>
        </div>
        """, unsafe_allow_html=True)
