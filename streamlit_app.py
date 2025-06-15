
import streamlit as st
import random

st.set_page_config(page_title="Treasure Hunt", page_icon="🏝️")

if "players" not in st.session_state:
    st.session_state.players = []
    st.session_state.turn = 0
    st.session_state.stage = "setup"
    st.session_state.rerun = False

MAX_PLAYERS = 3
MAX_HEALTH = 100

def reset_game():
    st.session_state.players = []
    st.session_state.turn = 0
    st.session_state.stage = "setup"
    st.session_state.rerun = False

def show_map(image="static/island_map.jpg"):
    st.image(image, caption="🗺️ Treasure Island Map", use_container_width=True)

def show_health_bar(player):
    health_capped = min(100, max(0, player["health"]))
    st.markdown(f"**💪 {player['name']} - Health: {health_capped}%**")
    st.progress(health_capped / 100.0)
    st.markdown(f"**⏱️ Time: {player['time']}  💰 Gold: {player['gold']}**")

def setup_players():
    st.title("🏝️ Treasure Hunt - Multiplayer Adventure")
    st.markdown("Enter names for up to 3 players:")
    show_map()

    for i in range(MAX_PLAYERS):
        name = st.text_input(f"Player {i+1} Name", key=f"name_{i}")
        if name:
            if i >= len(st.session_state.players):
                st.session_state.players.append({
                    "name": name,
                    "health": MAX_HEALTH,
                    "gold": 0,
                    "time": 100,
                    "stage": "stage_1",
                    "done": False
                })

    if len(st.session_state.players) >= 1 and st.button("Start Game"):
        st.session_state.stage = "play"
        st.session_state.rerun = True
        st.stop()

def play_game():
    st.title("🌴 The Hunt Continues")
    show_map()
    players = st.session_state.players
    turn = st.session_state.turn

    if turn >= len(players):
        st.session_state.stage = "end"
        st.session_state.rerun = True
        st.stop()

    player = players[turn]
    if player["done"]:
        st.session_state.turn += 1
        st.session_state.rerun = True
        st.stop()

    st.subheader(f"🎮 {player['name']}'s Turn")
    show_health_bar(player)

    # Optional media placeholder:
    media_slot = st.empty()

    if player["stage"] == "stage_1":
        choice = st.radio("Choose a path:", ["Swamp Trail", "Rocky Pass", "Dense Vines"], key=f"path_{turn}")
        if st.button("Confirm Choice", key=f"confirm_{turn}"):
            damage = {"Swamp Trail": 5, "Rocky Pass": 10, "Dense Vines": 15}[choice]
            player["health"] -= damage
            player["stage"] = "stage_2"
            media_slot.image("static/swamp.jpg") if choice == "Swamp Trail" else None
            st.session_state.rerun = True
            st.stop()

    elif player["stage"] == "stage_2":
        st.markdown("**Riddle 1: What has to be broken before you can use it?**")
        answer = st.text_input("Your answer", key=f"riddle1_{turn}")
        if st.button("Submit", key=f"riddle1_btn_{turn}"):
            if answer.strip().lower() == "egg":
                player["health"] += 5
                player["gold"] += 1
                player["time"] += 10
            else:
                penalty = random.choice([5, 10])
                player["health"] -= penalty
                player["time"] -= 10
            player["stage"] = "stage_3"
            st.session_state.rerun = True
            st.stop()

    elif player["stage"] == "stage_3":
        st.markdown("**Puzzle 2: I speak without a mouth and hear without ears. What am I?**")
        answer = st.text_input("Your answer", key=f"riddle2_{turn}")
        if st.button("Submit", key=f"riddle2_btn_{turn}"):
            if answer.strip().lower() == "echo":
                player["health"] += 5
                player["gold"] += 2
                player["time"] += 10
            else:
                loss = random.randint(5, 15)
                player["health"] -= loss
            player["stage"] = "stage_4"
            st.session_state.rerun = True
            st.stop()

    elif player["stage"] == "stage_4":
        st.markdown("**You cross a rickety bridge in a storm. Proceed or wait?**")
        decision = st.radio("Choose:", ["Cross now", "Wait for weather to clear"], key=f"bridge_{turn}")
        if st.button("Go", key=f"bridge_btn_{turn}"):
            if decision == "Cross now":
                result = random.choice(["safe", "injured", "fall"])
                if result == "injured":
                    player["health"] -= 10
                elif result == "fall":
                    player["health"] = 0
            else:
                player["time"] -= 15
            player["stage"] = "stage_5"
            st.session_state.rerun = True
            st.stop()

    elif player["stage"] == "stage_5":
        st.markdown("**Final Challenge: Guess the number between 1 and 5 to unlock the treasure.**")
        guess = st.number_input("Your guess:", 1, 5, key=f"guess_{turn}")
        if st.button("Try", key=f"guess_btn_{turn}"):
            secret = random.randint(1, 5)
            if guess == secret:
                player["gold"] += 5
            else:
                player["time"] -= 10
            player["stage"] = "done"
            st.session_state.rerun = True
            st.stop()

    elif player["stage"] == "done":
        st.success("✅ Turn complete.")
        player["done"] = True
        st.session_state.turn += 1
        st.session_state.rerun = True
        st.stop()

def game_over():
    st.title("❄️ Final Stage: Cold Journey Back")
    show_map()
    results = []
    for player in st.session_state.players:
        if player["health"] > 50 and player["time"] > 50:
            player["gold"] += 3
            msg = f"{player['name']} was strong and quick! +3 gold."
        elif player["health"] > 25:
            player["gold"] += 1
            msg = f"{player['name']} barely made it back. +1 gold."
        else:
            player["gold"] = 0
            msg = f"{player['name']} didn't survive the return."
        results.append((player['name'], player['gold'], msg))

    results.sort(key=lambda x: x[1], reverse=True)
    for name, gold, msg in results:
        st.markdown(f"**{name}**: {gold} gold – {msg}")

    winner = results[0][0]
    st.success(f"🏆 The winner is **{winner}**!")
    if st.button("Play Again"):
        reset_game()

# Game flow controller
if st.session_state.stage == "setup":
    setup_players()
elif st.session_state.stage == "play":
    play_game()
elif st.session_state.stage == "end":
    game_over()

# Delayed rerun (safe)
if "rerun" in st.session_state and st.session_state.rerun:
    st.session_state.rerun = False
    st.experimental_rerun()
