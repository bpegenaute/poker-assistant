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

        /* Layout improvements */
        .main {
            padding: 1rem !important;
            max-width: 1200px !important;
        }

        .section-container {
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }

        .section-title {
            color: var(--text-color);
            font-size: 1.2rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Card styles with improved visuals */
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

        /* Interactive elements */
        .quick-button {
            background-color: var(--primary-color);
            color: var(--text-color);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            margin: 0.25rem;
            cursor: pointer;
            border: none;
            font-size: 14px;
            transition: all 0.2s;
            position: relative;
            overflow: hidden;
        }

        .quick-button:hover {
            background-color: var(--primary-dark);
            transform: translateY(-1px);
        }

        .quick-button:active {
            transform: translateY(1px);
        }

        /* Button container */
        .preset-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            justify-content: center;
        }

        /* Tooltip styles */
        .tooltip {
            position: relative;
            display: inline-block;
        }

        .tooltip .tooltip-text {
            visibility: hidden;
            background-color: var(--background-dark);
            color: var(--text-color);
            text-align: center;
            padding: 5px 10px;
            border-radius: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            white-space: nowrap;
            border: 1px solid var(--border-color);
        }

        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }

        /* Keyboard shortcut hints */
        .shortcut-hint {
            position: absolute;
            right: 8px;
            top: 8px;
            background: rgba(255,255,255,0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        /* Loading animation */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .loading {
            animation: pulse 1.5s infinite;
        }

        /* Quick Start Guide */
        .quick-start {
            background-color: var(--background-card);
            border: 1px solid var(--primary-color);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .quick-start h3 {
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        .quick-start ol {
            margin: 0;
            padding-left: 1.5rem;
        }

        .quick-start li {
            margin-bottom: 0.5rem;
            color: var(--text-secondary);
        }

        /* Action colors */
        .action-raise { color: var(--success-color) !important; }
        .action-call { color: var(--primary-color) !important; }
        .action-fold { color: var(--danger-color) !important; }

        /* Responsive adjustments */
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

def create_quick_start_guide():
    """Create a collapsible quick start guide"""
    with st.expander("📚 Quick Start Guide", expanded=False):
        st.markdown("""
        <div class="quick-start">
            <h3>How to Use the Poker Assistant</h3>
            <ol>
                <li>Select your hole cards using the top selectors (use number keys 2-9 and T,J,Q,K,A)</li>
                <li>Add community cards as they appear on the table</li>
                <li>Select your position (BTN = Button, CO = Cutoff, etc.)</li>
                <li>Enter the current pot size and amount to call</li>
                <li>Press Enter or click "Get Recommendation" for advice</li>
            </ol>
            <h3>Keyboard Shortcuts</h3>
            <ul>
                <li>Enter: Get recommendation</li>
                <li>Numbers (2-9) & T,J,Q,K,A: Quick card selection</li>
                <li>Tab: Navigate between inputs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def create_quick_hand_selector() -> Tuple[str, str]:
    """Create a quick hand selection interface"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
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

    st.markdown('</div>', unsafe_allow_html=True)
    
    if rank1 and suit1 and rank2 and suit2:
        suit_map = {'♣': 'c', '♦': 'd', '♥': 'h', '♠': 's'}
        return f"{rank1}{suit_map[suit1]}", f"{rank2}{suit_map[suit2]}"
    return "", ""

def create_community_cards_selector() -> List[str]:
    """Create a single-line community cards selector"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Community Cards</div>', unsafe_allow_html=True)
    
    cols = st.columns(5)
    community_cards = []
    
    for i, street in enumerate(['Flop', 'Flop', 'Flop', 'Turn', 'River']):
        with cols[i]:
            rank = st.selectbox(
                f'{street} Card {i+1}',
                [''] + list('23456789TJQKA'),
                key=f'comm_rank{i}',
                help=f"Select the rank of the {street} card"
            )
            suit = st.selectbox(
                f'Suit {i+1}',
                [''] + list('♣♦♥♠'),
                key=f'comm_suit{i}',
                help=f"Select the suit of the {street} card",
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
    st.markdown('<div class="section-title">Betting Information</div>', unsafe_allow_html=True)
    
    cols = st.columns([2, 2, 2])
    
    with cols[0]:
        stack = st.number_input(
            'Stack Size',
            min_value=0.0,
            value=100.0,
            step=1.0,
            key='stack_size',
            help="Your current stack size in big blinds"
        )
        
    with cols[1]:
        pot = st.number_input(
            'Pot Size',
            min_value=0.0,
            value=0.0,
            step=1.0,
            key='pot_size',
            help="Current pot size including all bets"
        )
        
    with cols[2]:
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    return stack, pot, to_call

def create_quick_position_selector() -> str:
    """Create a quick position selector with buttons"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Table Position</div>', unsafe_allow_html=True)
    
    positions = {
        'BTN': ('Button', 'Last to act preflop, best position'),
        'CO': ('Cutoff', 'Second-best position, one before button'),
        'MP': ('Middle', 'Middle position, average playability'),
        'EP': ('Early', 'First positions to act, be cautious'),
        'BB': ('Big Blind', 'Must defend against steals'),
        'SB': ('Small Blind', 'Worst position, act first postflop')
    }
    
    cols = st.columns(len(positions))
    selected_position = None
    
    for i, (pos, (label, tooltip)) in enumerate(positions.items()):
        with cols[i]:
            if st.button(label, key=f'pos_{pos}', help=tooltip):
                selected_position = pos
    
    st.markdown('</div>', unsafe_allow_html=True)
    return selected_position

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
