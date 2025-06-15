
import streamlit as st
import random

st.set_page_config(page_title="🏝️ Treasure Hunt Expanded", page_icon="💰")

if "players" not in st.session_state:
    st.session_state.players = []
    st.session_state.turn = 0
    st.session_state.stage = "setup"
    st.session_state.rerun = False
    st.session_state.log = []

MAX_PLAYERS = 3
MAX_HEALTH = 100

def reset_game():
    st.session_state.players = []
    st.session_state.turn = 0
    st.session_state.stage = "setup"
    st.session_state.rerun = False
    st.session_state.log = []

def log_event(text):
    st.session_state.log.append(text)

def show_log():
    st.markdown("### 📜 Adventure Log")
    for entry in reversed(st.session_state.log[-15:]):
        st.markdown(f"- {entry}")

def show_map(image="static/island_map.jpg", location=None):
    st.image(image, caption="🗺️ Treasure Island Map", use_container_width=True)
    if location:
        st.markdown(f"**📍 Location: {location}**")

def show_health_bar(player):
    health_capped = min(100, max(0, player["health"]))
    st.markdown(f"**💪 {player['name']} - Health: {health_capped}%**")
    st.progress(health_capped / 100.0)
    st.markdown(f"**⏱️ Time: {player['time']}  💰 Gold: {player['gold']}**")

def show_inventory(player):
    if player["inventory"]:
        items = " ".join(player["inventory"])
        st.markdown(f"**🎒 Inventory:** {items}")

def setup_players():
    st.title("🏝️ Treasure Hunt - Expanded Edition")
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
    st.title("🌴 Your Adventure Awaits")
    players = st.session_state.players
    current_player = players[st.session_state.turn]

    st.subheader(f"🎮 {current_player['name']}'s Turn")
    show_map(location=current_player.get("location", "Unknown"))
    show_health_bar(current_player)
    show_inventory(current_player)

    if current_player["complete"]:
        st.session_state.turn = (st.session_state.turn + 1) % len(players)
        st.session_state.rerun = True
        st.stop()

    # --- STAGES ---
    stage = current_player["stage"]

    if stage == "stage_1":
        st.markdown("You reach a fork in the jungle.")
        choice = st.radio("Choose your path:", ["Cliffside Trail", "Swamp Crossing", "Old Rope Bridge"])
        if st.button("Continue"):
            penalty = {"Cliffside Trail": 10, "Swamp Crossing": 5, "Old Rope Bridge": 15}[choice]
            current_player["health"] -= penalty
            current_player["location"] = choice
            log_event(f"{current_player['name']} chose {choice} and lost {penalty}% health.")
            current_player["stage"] = "stage_2"
            next_turn()

    elif stage == "stage_2":
        st.markdown("🧠 Riddle: What can run but never walks, has a bed but never sleeps?")
        answer = st.text_input("Your answer:")
        if st.button("Submit Answer"):
            if answer.lower().strip() == "river":
                current_player["gold"] += 2
                current_player["inventory"].append("Map Piece")
                log_event(f"{current_player['name']} solved the riddle and gained a map piece.")
            else:
                current_player["health"] -= 10
                log_event(f"{current_player['name']} failed the riddle and lost 10% health.")
            current_player["stage"] = "stage_3"
            next_turn()

    elif stage == "stage_3":
        st.markdown("🔥 A dark cave lies ahead. Do you use a torch?")
        if "Torch" in current_player["inventory"]:
            use = st.radio("Use Torch?", ["Yes", "No"])
            if st.button("Proceed"):
                if use == "Yes":
                    current_player["gold"] += 3
                    log_event(f"{current_player['name']} used a torch and found gold!")
                else:
                    current_player["health"] -= 15
                    log_event(f"{current_player['name']} entered the cave blind and was hurt.")
                current_player["stage"] = "stage_4"
                next_turn()
        else:
            st.warning("You have no torch and must continue in the dark.")
            current_player["health"] -= 10
            current_player["stage"] = "stage_4"
            next_turn()

    elif stage == "stage_4":
        st.markdown("🗝️ You discover a locked chest.")
        if "Golden Key" in current_player["inventory"]:
            if st.button("Use Key to Unlock"):
                current_player["gold"] += 5
                log_event(f"{current_player['name']} unlocked a treasure chest!")
        else:
            st.info("You don't have the key. Maybe you'll find it later.")
        current_player["stage"] = "stage_5"
        next_turn()

    elif stage == "stage_5":
        st.markdown("🔐 Final Puzzle: Solve this to win bonus time.")
        st.code("I am always in front of you but never here. What am I?")
        final = st.text_input("Your answer:", key="final_puzzle")
        if st.button("Submit"):
            if final.lower().strip() == "future":
                current_player["time"] += 20
                log_event(f"{current_player['name']} solved the final puzzle and gained +20 time!")
            else:
                current_player["health"] -= 5
            current_player["complete"] = True
            next_turn()

def next_turn():
    st.session_state.turn = (st.session_state.turn + 1) % len(st.session_state.players)
    st.session_state.rerun = True
    st.stop()

def game_over():
    st.title("🏁 Journey Complete")
    show_map()
    scores = []
    for p in st.session_state.players:
        bonus = 3 if p["health"] > 50 and p["time"] > 50 else (1 if p["health"] > 25 else 0)
        p["gold"] += bonus
        scores.append((p["name"], p["gold"]))

    scores.sort(key=lambda x: x[1], reverse=True)
    winner = scores[0][0]
    for name, gold in scores:
        st.markdown(f"**{name}**: {gold} gold")
    st.success(f"🏆 The winner is **{winner}**!")
    if st.button("Play Again"):
        reset_game()

# Main flow
if st.session_state.stage == "setup":
    setup_players()
elif st.session_state.stage == "play":
    if all(p["complete"] for p in st.session_state.players):
        st.session_state.stage = "end"
        st.experimental_rerun()
    else:
        play_game()
        show_log()
elif st.session_state.stage == "end":
    game_over()

# Controlled rerun
if st.session_state.rerun:
    st.session_state.rerun = False
    st.experimental_rerun()
