import streamlit as st
from poker.evaluator import HandEvaluator
from poker.calculator import PokerCalculator
from poker.recommendations import RecommendationEngine
from components.ui_elements import (
    create_card_selector,
    create_position_input,
    create_stack_input,
    display_recommendation
)

def main():
    st.title("Poker Assistant")
    st.write("Get mathematically-sound poker recommendations in real-time")

    # Initialize session state
    if 'community_cards' not in st.session_state:
        st.session_state.community_cards = []

    # Create sidebar for hole cards
    with st.sidebar:
        st.header("Your Hand")
        hole_card1 = create_card_selector('hole1')
        hole_card2 = create_card_selector('hole2')
        
        if hole_card1 and hole_card2:
            st.session_state.hole_cards = [hole_card1, hole_card2]
        else:
            st.session_state.hole_cards = []

    # Main area for community cards
    st.header("Community Cards")
    cols = st.columns(5)
    community_cards = []
    
    for i in range(5):
        with cols[i]:
            card = create_card_selector(f'community{i}')
            if card:
                community_cards.append(card)

    # Player position and stack sizes
    st.header("Position and Stacks")
    position = create_position_input()
    stack, pot, to_call = create_stack_input()

    # Generate recommendation
    if st.button("Get Recommendation"):
        if not st.session_state.hole_cards:
            st.error("Please select your hole cards first!")
            return

        engine = RecommendationEngine()
        recommendation = engine.get_recommendation(
            st.session_state.hole_cards,
            community_cards,
            position,
            pot,
            to_call,
            stack
        )
        
        display_recommendation(recommendation)

    # Display basic stats
    with st.expander("Basic Statistics"):
        if st.session_state.hole_cards:
            evaluator = HandEvaluator()
            calculator = PokerCalculator()
            
            strength = evaluator.evaluate_hand_strength(
                st.session_state.hole_cards,
                community_cards
            )
            
            pot_odds = calculator.calculate_pot_odds(to_call, pot)
            
            st.write(f"Raw Hand Strength: {strength:.2%}")
            st.write(f"Pot Odds: {pot_odds:.2%}")
            
            if len(community_cards) < 5:
                positive_potential, negative_potential = evaluator.calculate_hand_potential(
                    st.session_state.hole_cards,
                    community_cards
                )
                st.write(f"Positive Potential: {positive_potential:.2%}")
                st.write(f"Negative Potential: {negative_potential:.2%}")

if __name__ == "__main__":
    main()
