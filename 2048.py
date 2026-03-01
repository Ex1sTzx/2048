import streamlit as st
import streamlit.components.v1 as components
import random

# -----------------------------
# Configuration & Constants
# -----------------------------
TILE_COLORS = {
    0: "#2e2e2e", 
    2: "#fff4cc", 
    4: "#ffe066", 
    8: "#ffcc66",
    16: "#ff9933", 
    32: "#ff751a", 
    64: "#ff4d00", 
    128: "#e65c00",
    256: "#cc5200", 
    512: "#b34700", 
    1024: "#993d00", 
    2048: "#7a2e00"
}

# -----------------------------
# Game Logic
# -----------------------------
def initialize_board():
    """Initializes a 4x4 board with two starting tiles."""
    board = [[0] * 4 for _ in range(4)]
    add_new_tile(board)
    add_new_tile(board)
    return board

def add_new_tile(board):
    """Adds a new tile (2 or 4) to a random empty spot."""
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        board[i][j] = 2 if random.random() < 0.9 else 4

def move_left(board):
    """Moves and merges tiles to the left."""
    new_board = [row[:] for row in board]  # faster than copy.deepcopy
    for row in new_board:
        # Remove empty spaces
        row[:] = [x for x in row if x != 0]
        # Merge adjacent equal tiles
        for i in range(len(row) - 1):
            if row[i] == row[i + 1]:
                row[i] *= 2
                row[i + 1] = 0
                st.session_state.score += row[i]
        # Remove empty spaces again and pad with zeros
        row[:] = [x for x in row if x != 0]
        row.extend([0] * (4 - len(row)))
    return new_board

def rotate_board(board):
    """Rotates the board 90 degrees clockwise."""
    return [[board[j][i] for j in range(4)] for i in range(3, -1, -1)]

def move(board, direction):
    """Handles board movement in all 4 directions."""
    old_board = [row[:] for row in board]

    if direction == "LEFT":
        board = move_left(board)
    elif direction == "RIGHT":
        board = rotate_board(rotate_board(board))
        board = move_left(board)
        board = rotate_board(rotate_board(board))
    elif direction == "UP":
        board = rotate_board(board)
        board = move_left(board)
        board = rotate_board(rotate_board(rotate_board(board)))
    elif direction == "DOWN":
        board = rotate_board(rotate_board(rotate_board(board)))
        board = move_left(board)
        board = rotate_board(board)

    # Spawn a new tile only if the board changed
    if board != old_board:
        add_new_tile(board)

    return board

def is_game_over(board):
    """Checks if there are no valid moves left."""
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                return False
            if i < 3 and board[i][j] == board[i + 1][j]:
                return False
            if j < 3 and board[i][j] == board[i][j + 1]:
                return False
    return True

# -----------------------------
# UI Render & Styling
# -----------------------------
def apply_custom_styles():
    """Injects custom CSS for a cleaner UI."""
    st.markdown("""
        <style>
        .block-container {
            padding-top: 1rem;
        }
        div[data-testid="stButton"] > button {
            background-color: #ff8c00;
            color: white;
            border-radius: 12px;
            font-weight: bold;
            width: 100%;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #ff4500;
        }
        </style>
    """, unsafe_allow_html=True)

def add_keyboard_support():
    """Injects JavaScript to map arrow keys to UI buttons."""
    components.html(
        """
        <script>
        const doc = window.parent.document;
        if (!doc.getElementById('keyboard-listener')) {
            const scriptTag = doc.createElement('script');
            scriptTag.id = 'keyboard-listener';
            doc.body.appendChild(scriptTag);
            
            doc.addEventListener('keydown', function(e) {
                let buttonText = '';
                if (e.key === 'ArrowLeft') buttonText = '⬅ Left';
                else if (e.key === 'ArrowUp') buttonText = '⬆ Up';
                else if (e.key === 'ArrowRight') buttonText = '➡ Right';
                else if (e.key === 'ArrowDown') buttonText = '⬇ Down';
                
                if (buttonText) {
                    if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].indexOf(e.code) > -1) {
                        e.preventDefault();
                    }
                    const buttons = Array.from(doc.querySelectorAll('button'));
                    const targetBtn = buttons.find(btn => btn.innerText.includes(buttonText));
                    if (targetBtn) {
                        targetBtn.click();
                    }
                }
            });
        }
        </script>
        """,
        height=0,
        width=0,
    )

def display_board(board):
    """Renders the game board."""
    max_tile = max(max(row) for row in board)
    
    for row in board:
        cols = st.columns(4)
        for i, val in enumerate(row):
            color = TILE_COLORS.get(val, "#3a3a3a")
            
            glow_style = ""
            if val == max_tile and val != 0:
                glow_style = "box-shadow: 0 0 20px gold;"

            if val == 0:
                cols[i].markdown(
                    "<div style='background:#2e2e2e;height:80px;border-radius:15px;'></div>",
                    unsafe_allow_html=True
                )
            else:
                cols[i].markdown(
                    f"<div style='background:{color}; height:80px; border-radius:15px; display:flex; "
                    f"align-items:center; justify-content:center; font-size:22px; font-weight:bold; "
                    f"color:black; {glow_style}'>{val}</div>",
                    unsafe_allow_html=True
                )

# -----------------------------
# Main Application Execution
# -----------------------------
def main():
    st.set_page_config(layout="centered", page_title="2048 Game", page_icon="🧩")
    apply_custom_styles()
    
    st.title("🧩 2048 Game")

    # Initialize Session State
    if "board" not in st.session_state:
        st.session_state.board = initialize_board()
    if "score" not in st.session_state:
        st.session_state.score = 0

    # Display Score & Board
    st.subheader(f"🏆 Score: {st.session_state.score}")
    display_board(st.session_state.board)
    st.markdown("---")

    # Controls
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅ Left"):
            st.session_state.board = move(st.session_state.board, "LEFT")
            st.rerun()

    with col2:
        if st.button("⬆ Up"):
            st.session_state.board = move(st.session_state.board, "UP")
            st.rerun()

    with col3:
        if st.button("➡ Right"):
            st.session_state.board = move(st.session_state.board, "RIGHT")
            st.rerun()

    if st.button("⬇ Down"):
        st.session_state.board = move(st.session_state.board, "DOWN")
        st.rerun()

    if st.button("🔄 Restart Game"):
        st.session_state.board = initialize_board()
        st.session_state.score = 0
        st.rerun()

    # Keyboard Listener
    add_keyboard_support()

    # Game Status Checks
    if any(2048 in row for row in st.session_state.board):
        st.success("🎉 You Win!")
    elif is_game_over(st.session_state.board):
        st.error("Game Over 😢")

if __name__ == "__main__":
    main()