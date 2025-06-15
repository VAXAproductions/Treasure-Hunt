
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
                    "inventory": [],
                    "complete": False
                })

    if len(st.session_state.players) >= 1 and st.button("Start Game"):
        st.session_state.stage = "play"
        st.session_state.rerun = True
        st.stop()

def play_game():
    st.title("🌴 The Hunt Continues")
    show_map()
    players = st.session_state.players

    current_player = players[st.session_state.turn]
    st.subheader(f"🎮 {current_player['name']}'s Turn")
    show_health_bar(current_player)

    # Skip finished players
    if current_player["complete"]:
        st.session_state.turn = (st.session_state.turn + 1) % len(players)
        st.session_state.rerun = True
        st.stop()

    # STAGES
    if current_player["stage"] == "stage_1":
        choice = st.radio("Choose a path:", ["Swamp Trail", "Rocky Pass", "Dense Vines"], key=f"path_{st.session_state.turn}")
        if st.button("Confirm Choice", key=f"confirm_{st.session_state.turn}"):
            damage = {"Swamp Trail": 5, "Rocky Pass": 10, "Dense Vines": 15}[choice]
            current_player["health"] -= damage
            current_player["stage"] = "stage_2"
            st.session_state.turn = (st.session_state.turn + 1) % len(players)
            st.session_state.rerun = True
            st.stop()

    elif current_player["stage"] == "stage_2":
        st.markdown("**Riddle: What has to be broken before you can use it?**")
        answer = st.text_input("Your answer", key=f"riddle1_{st.session_state.turn}")
        if st.button("Submit", key=f"submit1_{st.session_state.turn}"):
            if answer.strip().lower() == "egg":
                current_player["health"] += 5
                current_player["gold"] += 1
                current_player["time"] += 10
                current_player["inventory"].append("Torch")
            else:
                current_player["health"] -= 10
                current_player["time"] -= 10
            current_player["stage"] = "stage_3"
            st.session_state.turn = (st.session_state.turn + 1) % len(players)
            st.session_state.rerun = True
            st.stop()

    elif current_player["stage"] == "stage_3":
        st.markdown("**Puzzle: I speak without a mouth and hear without ears. What am I?**")
        answer = st.text_input("Your answer", key=f"riddle2_{st.session_state.turn}")
        if st.button("Submit", key=f"submit2_{st.session_state.turn}"):
            if answer.strip().lower() == "echo":
                current_player["health"] += 5
                current_player["gold"] += 2
                current_player["time"] += 10
                current_player["inventory"].append("Map Piece")
            else:
                current_player["health"] -= random.randint(5, 15)
            current_player["stage"] = "stage_4"
            st.session_state.turn = (st.session_state.turn + 1) % len(players)
            st.session_state.rerun = True
            st.stop()

    elif current_player["stage"] == "stage_4":
        st.markdown("**Stormy bridge ahead. Do you cross or wait?**")
        decision = st.radio("Your action:", ["Cross now", "Wait for weather"], key=f"bridge_{st.session_state.turn}")
        if st.button("Go", key=f"bridgebtn_{st.session_state.turn}"):
            if decision == "Cross now":
                result = random.choice(["safe", "injured", "fall"])
                if result == "injured":
                    current_player["health"] -= 10
                elif result == "fall":
                    current_player["health"] = 0
            else:
                current_player["time"] -= 15
            current_player["stage"] = "stage_5"
            st.session_state.turn = (st.session_state.turn + 1) % len(players)
            st.session_state.rerun = True
            st.stop()

    elif current_player["stage"] == "stage_5":
        st.markdown("**Guess the number between 1–5 to unlock the chest**")
        guess = st.number_input("Your guess:", 1, 5, key=f"guess_{st.session_state.turn}")
        if st.button("Try", key=f"guessbtn_{st.session_state.turn}"):
            if guess == random.randint(1, 5):
                current_player["gold"] += 5
                current_player["inventory"].append("Golden Key")
            else:
                current_player["time"] -= 10
            current_player["stage"] = "done"
            st.session_state.turn = (st.session_state.turn + 1) % len(players)
            st.session_state.rerun = True
            st.stop()

    elif current_player["stage"] == "done":
        st.success("✅ Turn complete.")
        current_player["complete"] = True
        st.session_state.turn = (st.session_state.turn + 1) % len(players)
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

# Game controller
if st.session_state.stage == "setup":
    setup_players()
elif st.session_state.stage == "play":
    all_done = all(p.get("complete", False) for p in st.session_state.players)
    if all_done:
        st.session_state.stage = "end"
        st.experimental_rerun()
    else:
        play_game()
elif st.session_state.stage == "end":
    game_over()

# Safe rerun
if st.session_state.get("rerun", False):
    st.session_state.rerun = False
    st.experimental_rerun()
