import streamlit as st
from typing import Dict, Optional

def create_tournament_controls() -> Optional[Dict]:
    """Create tournament-specific controls and return tournament information"""
    with st.expander("🏆 Tournament Settings", expanded=False):
        is_tournament = st.toggle("Tournament Mode", value=False, key='tournament_mode')
        
        if not is_tournament:
            return None
            
        col1, col2 = st.columns(2)
        
        with col1:
            total_players = st.number_input(
                "Total Players",
                min_value=2,
                max_value=10000,
                value=100,
                step=1,
                help="Total number of players that started the tournament"
            )
            
            players_left = st.number_input(
                "Players Remaining",
                min_value=2,
                max_value=total_players,
                value=min(50, total_players),
                step=1,
                help="Number of players still in the tournament"
            )
            
            in_money_spots = st.number_input(
                "Paid Positions",
                min_value=1,
                max_value=players_left,
                value=min(9, players_left),
                step=1,
                help="Number of places that get paid"
            )
            
        with col2:
            small_blind = st.number_input(
                "Small Blind",
                min_value=0.0,
                value=50.0,
                step=10.0,
                help="Current small blind amount"
            )
            
            big_blind = st.number_input(
                "Big Blind",
                min_value=small_blind * 2,
                value=small_blind * 2,
                step=20.0,
                help="Current big blind amount"
            )
            
            avg_stack = st.number_input(
                "Average Stack",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                help="Average stack size among remaining players"
            )

        # Calculate and display key tournament metrics
        if st.session_state.stack_size > 0 and big_blind > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                bb_stack = st.session_state.stack_size / big_blind
                st.metric("Stack in BBs", f"{bb_stack:.1f}")
                
            with col2:
                total_blinds = small_blind + big_blind
                m_score = st.session_state.stack_size / total_blinds
                st.metric("M-Score", f"{m_score:.1f}")
                
            with col3:
                stack_pressure = "High" if bb_stack < 10 else (
                    "Medium" if bb_stack < 20 else "Low"
                )
                st.metric("Stack Pressure", stack_pressure)

        return {
            'total_players': total_players,
            'players_left': players_left,
            'in_money_spots': in_money_spots,
            'total_blinds': small_blind + big_blind,
            'avg_stack': avg_stack,
            'stack_size': st.session_state.stack_size
        }
