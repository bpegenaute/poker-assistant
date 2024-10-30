import streamlit as st
from typing import List, Tuple

def inject_custom_css():
    """Inject custom CSS for better UI appearance"""
    st.markdown("""
        <style>
        /* High contrast theme */
        :root {
            --primary-color: #2196F3;
            --primary-dark: #1976D2;
            --success-color: #4CAF50;
            --warning-color: #FFC107;
            --danger-color: #F44336;
            --text-color: #FFFFFF;
            --text-secondary: #B0BEC5;
            --background-dark: #1E1E1E;
            --background-card: #2D2D2D;
            --border-color: #404040;
        }

        /* Position button styles */
        .position-button {
            width: 100%;
            padding: 0.5rem;
            margin: 0.25rem 0;
            border: 2px solid var(--primary-color);
            background-color: var(--background-card);
            color: var(--text-color);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .position-button:hover {
            background-color: var(--primary-dark);
            transform: translateY(-2px);
        }

        .position-button.selected {
            background-color: var(--primary-color);
            box-shadow: 0 0 10px var(--primary-color);
        }

        .position-indicator {
            text-align: center;
            padding: 0.5rem;
            margin-top: 1rem;
            background-color: var(--background-card);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        /* Layout improvements */
        .main {
            padding: 1rem !important;
            max-width: 1200px !important;
        }

        .main-content {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .section-container {
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }

        .section-container.prominent {
            background-color: var(--background-dark);
            border: 2px solid var(--primary-color);
            padding: 1.5rem;
            border-radius: 12px;
        }

        .section-title {
            color: var(--text-color);
            font-size: 1.4rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: bold;
        }

        .section-subtitle {
            color: var(--text-color);
            font-size: 1.1rem;
            margin: 1rem 0;
            font-weight: bold;
        }

        .card {
            background-color: var(--background-card);
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .street-separator {
            border-left: 2px solid var(--primary-color);
            margin: 0.5rem 0;
            padding-top: 1rem;
        }

        .stack-size-unit {
            margin-top: 30px;
            color: var(--text-color);
            font-size: 1.2rem;
            font-weight: bold;
        }

        .recommendation-button-container {
            margin-top: 2rem;
            padding: 1rem;
            background-color: var(--background-dark);
            border-radius: 8px;
            border: 2px solid var(--primary-color);
        }

        .quick-button {
            background-color: var(--primary-color);
            color: var(--text-color);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            margin: 0.25rem;
            cursor: pointer;
            border: none;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.2s;
            position: relative;
            overflow: hidden;
            width: 100%;
        }

        .quick-button:hover {
            background-color: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .quick-button:active {
            transform: translateY(1px);
        }

        .preset-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            justify-content: center;
        }

        .tooltip {
            position: relative;
            display: inline-block;
            width: 100%;
        }

        .tooltip .tooltip-text {
            visibility: hidden;
            background-color: var(--background-dark);
            color: var(--text-color);
            text-align: center;
            padding: 8px 12px;
            border-radius: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }

        .shortcut-hint {
            position: absolute;
            right: 8px;
            top: 8px;
            background: rgba(255,255,255,0.1);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .action-raise { color: var(--success-color) !important; }
        .action-call { color: var(--primary-color) !important; }
        .action-fold { color: var(--danger-color) !important; }

        @media (max-width: 768px) {
            .card {
                padding: 1rem;
            }
            
            .preset-buttons {
                flex-wrap: wrap;
            }
        }
        </style>
    """, unsafe_allow_html=True)

def create_stack_size_input() -> float:
    """Create a prominent stack size input"""
    col1, col2 = st.columns([4, 1])
    with col1:
        stack = st.number_input(
            'Your Stack Size',
            min_value=0.0,
            value=st.session_state.stack_size,
            step=1.0,
            key='stack_size_input',
            help="Enter your current stack size in big blinds"
        )
    with col2:
        st.markdown('<div class="stack-size-unit">BB</div>', unsafe_allow_html=True)
    return stack

def create_quick_position_selector() -> str:
    """Create a quick position selector with prominent buttons"""
    if 'selected_position' not in st.session_state:
        st.session_state.selected_position = None

    positions = {
        'BTN': ('Button', 'Last to act preflop, best position'),
        'CO': ('Cutoff', 'Second-best position, one before button'),
        'MP': ('Middle', 'Middle position, average playability'),
        'EP': ('Early', 'First positions to act, be cautious'),
        'BB': ('Big Blind', 'Must defend against steals'),
        'SB': ('Small Blind', 'Worst position, act first postflop')
    }
    
    cols = st.columns(len(positions))
    
    for i, (pos, (label, tooltip)) in enumerate(positions.items()):
        with cols[i]:
            is_selected = st.session_state.selected_position == pos
            button_class = "position-button selected" if is_selected else "position-button"
            
            if st.button(
                label,
                key=f'pos_{pos}',
                help=tooltip,
                on_click=lambda p=pos: setattr(st.session_state, 'selected_position', p)
            ):
                st.session_state.selected_position = pos

    if st.session_state.selected_position:
        st.markdown(
            f'<div class="position-indicator">Selected Position: {positions[st.session_state.selected_position][0]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Please select your position at the table")
    
    return st.session_state.selected_position

def create_quick_hand_selector() -> Tuple[str, str]:
    """Create a quick hand selection interface"""
    cols = st.columns([3, 3, 1])
    
    with cols[0]:
        rank1 = st.selectbox(
            'First Card',
            [''] + list('23456789TJQKA'),
            key='quick_rank1',
            format_func=lambda x: x if x else 'Select Rank',
            help="Select the rank of your first card (2-A)"
        )
        suit1 = st.selectbox(
            'Suit 1',
            [''] + list('♣♦♥♠'),
            key='quick_suit1',
            format_func=lambda x: x if x else 'Select Suit',
            help="Select the suit of your first card",
            label_visibility='collapsed'
        )
    
    with cols[1]:
        rank2 = st.selectbox(
            'Second Card',
            [''] + list('23456789TJQKA'),
            key='quick_rank2',
            format_func=lambda x: x if x else 'Select Rank',
            help="Select the rank of your second card (2-A)"
        )
        suit2 = st.selectbox(
            'Suit 2',
            [''] + list('♣♦♥♠'),
            key='quick_suit2',
            format_func=lambda x: x if x else 'Select Suit',
            help="Select the suit of your second card",
            label_visibility='collapsed'
        )
    
    with cols[2]:
        st.markdown('<div class="shortcut-hint">2-9,T,J,Q,K,A</div>', unsafe_allow_html=True)
        if st.button('Clear', key='clear_hand', help="Clear your hole cards selection"):
            return "", ""
    
    if rank1 and suit1 and rank2 and suit2:
        suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
        return f"{rank1}{suit_map[suit1]}", f"{rank2}{suit_map[suit2]}"
    return "", ""

def create_betting_controls() -> Tuple[float, float]:
    """Create compact betting controls with presets"""
    st.markdown('<div class="section-title">💰 Betting Information</div>', unsafe_allow_html=True)
    
    cols = st.columns([1, 1])
    
    with cols[0]:
        pot = st.number_input(
            'Pot Size',
            min_value=0.0,
            value=0.0,
            step=1.0,
            key='pot_size',
            help="Current pot size including all bets"
        )
    
    with cols[1]:
        to_call = st.number_input(
            'Amount to Call',
            min_value=0.0,
            value=0.0,
            step=1.0,
            key='to_call',
            help="Amount you need to call to continue in the hand"
        )
    
    st.markdown('''
        <div class="preset-buttons">
            <div class="tooltip">
                <button class="quick-button" onclick="setToCall(this, 0.5)">½ Pot</button>
                <span class="tooltip-text">Set to half the current pot size</span>
            </div>
            <div class="tooltip">
                <button class="quick-button" onclick="setToCall(this, 0.75)">¾ Pot</button>
                <span class="tooltip-text">Set to three-quarters of the pot size</span>
            </div>
            <div class="tooltip">
                <button class="quick-button" onclick="setToCall(this, 1.0)">Pot</button>
                <span class="tooltip-text">Set to the full pot size</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    return pot, to_call

def create_community_cards_selector() -> List[str]:
    """Create a community cards selector with street separation"""
    community_cards = []
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Flop</div>', unsafe_allow_html=True)
    flop_cols = st.columns(3)
    for i in range(3):
        with flop_cols[i]:
            rank = st.selectbox(
                f'Flop Card {i+1}',
                [''] + list('23456789TJQKA'),
                key=f'flop_rank{i}',
                help=f"Select the rank of flop card {i+1}"
            )
            suit = st.selectbox(
                f'Suit {i+1}',
                [''] + list('♣♦♥♠'),
                key=f'flop_suit{i}',
                help=f"Select the suit of flop card {i+1}",
                label_visibility='collapsed'
            )
            if rank and suit:
                suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
                community_cards.append(f"{rank}{suit_map[suit]}")
    
    if len(community_cards) == 3:
        st.markdown('<div class="street-separator"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Turn</div>', unsafe_allow_html=True)
        turn_col1, turn_col2 = st.columns([1, 3])
        with turn_col1:
            rank = st.selectbox(
                'Turn Card',
                [''] + list('23456789TJQKA'),
                key='turn_rank',
                help="Select the rank of the turn card"
            )
            suit = st.selectbox(
                'Turn Suit',
                [''] + list('♣♦♥♠'),
                key='turn_suit',
                help="Select the suit of the turn card",
                label_visibility='collapsed'
            )
            if rank and suit:
                suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
                community_cards.append(f"{rank}{suit_map[suit]}")
    
    if len(community_cards) == 4:
        st.markdown('<div class="street-separator"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">River</div>', unsafe_allow_html=True)
        river_col1, river_col2 = st.columns([1, 3])
        with river_col1:
            rank = st.selectbox(
                'River Card',
                [''] + list('23456789TJQKA'),
                key='river_rank',
                help="Select the rank of the river card"
            )
            suit = st.selectbox(
                'River Suit',
                [''] + list('♣♦♥♠'),
                key='river_suit',
                help="Select the suit of the river card",
                label_visibility='collapsed'
            )
            if rank and suit:
                suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
                community_cards.append(f"{rank}{suit_map[suit]}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    return community_cards

def get_street_name(community_cards: List[str]) -> str:
    """Get the current street name based on community cards"""
    if not community_cards:
        return "Pre-flop"
    elif len(community_cards) == 3:
        return "Flop"
    elif len(community_cards) == 4:
        return "Turn"
    elif len(community_cards) == 5:
        return "River"
    return "Pre-flop"

def create_quick_start_guide():
    """Create a collapsible quick start guide"""
    with st.expander("📚 Quick Start Guide", expanded=False):
        st.markdown("""
        <div class="quick-start">
            <h3>How to Use the Poker Assistant</h3>
            <ol>
                <li>Enter your stack size in big blinds</li>
                <li>Select your table position</li>
                <li>Choose your hole cards</li>
                <li>Enter the current pot size and any bet to call</li>
                <li>Add community cards as they appear</li>
                <li>Get street-specific recommendations</li>
            </ol>
            <h3>Keyboard Shortcuts</h3>
            <ul>
                <li>Enter: Get recommendation</li>
                <li>Numbers (2-9) & T,J,Q,K,A: Quick card selection</li>
                <li>Tab: Navigate between inputs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_recommendation(recommendation: dict, minimal: bool = False):
    """Display the recommendation with styling"""
    action_colors = {
        'RAISE': 'var(--success-color)',
        'CALL': 'var(--primary-color)',
        'FOLD': 'var(--danger-color)'
    }
    
    if minimal:
        st.markdown(f"""
        <div class="card" style='background-color: {action_colors[recommendation['action']]}20;
                    border-color: {action_colors[recommendation['action']]}'>
            <h3 style='color: {action_colors[recommendation['action']]}; margin: 0;'>
                {recommendation['action']} ({recommendation['confidence']:.0%})
            </h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card" style='background-color: {action_colors[recommendation['action']]}20;
                    border-color: {action_colors[recommendation['action']]}'>
            <h2 style='color: {action_colors[recommendation['action']]};'>{recommendation['action']}</h2>
            <p style='font-size: 1.2em;'>Confidence: {recommendation['confidence']:.1%}</p>
            <div style='background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px;'>
                {recommendation['reasoning']}
            </div>
        </div>
        """, unsafe_allow_html=True)