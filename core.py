import raylib as rl
import random

# global stuff
suits = {
    0: "Spades", 
    1: "Hearts",
    2: "Clubs",
    3: "Diamonds"
}

suit_colours = [rl.BLACK, rl.RED, rl.DARKBLUE, rl.PINK]

ranks = {
    1: "A",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "J",
    12: "Q",
    13: "K"
}

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_raw(self):
        return (self.x, self.y)

class RlWindow:
    n_width = 1280
    n_height = 720

    # for card, deck, etc.
    n_el_width = n_width // 11
    n_el_height = n_height // 4

    # qol
    n_font_size = n_width // 60
    n_gap_size = n_width // 128

    @staticmethod
    def GetVirtualMousePosition():
        screen_w = rl.GetScreenWidth()
        screen_h = rl.GetScreenHeight()

        scale = min(screen_w / RlWindow.n_width, screen_h / RlWindow.n_height)

        draw_w = int(RlWindow.n_width * scale)
        draw_h = int(RlWindow.n_height * scale)

        offset_x = (screen_w - draw_w) // 2
        offset_y = (screen_h - draw_h) // 2

        mouse = rl.GetMousePosition()

        # If in letterbox region, return safe dummy coordinates
        if not (offset_x <= mouse.x <= offset_x + draw_w and offset_y <= mouse.y <= offset_y + draw_h):
            return Vector2(-100, -100)

        # Convert real to virtual
        return Vector2(
            (mouse.x - offset_x) / scale,
            (mouse.y - offset_y) / scale
        )

    def __init__(self):
        pass

class GameTemplate:
    def __init__(self):
        pass

    def draw(self):
        pass

    def game_over(self):
        pass

    def start(self):
        rl.SetTraceLogLevel(rl.LOG_NONE)
        rl.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE)
        rl.InitWindow(RlWindow.n_width, RlWindow.n_height, b"sl spider solitaire")
        rl.SetTargetFPS(rl.GetMonitorRefreshRate(rl.GetCurrentMonitor()))

        target = rl.LoadRenderTexture(RlWindow.n_width, RlWindow.n_height)
        source = (0, 0, target.texture.width, -target.texture.height)

        while not rl.WindowShouldClose():
            # --- Draw at virtual resolution ---
            rl.BeginTextureMode(target)
            rl.ClearBackground(rl.DARKGREEN)

            self.draw()

            rl.EndTextureMode()

            # --- Compute scaling based on window size ---
            screen_w = rl.GetScreenWidth()
            screen_h = rl.GetScreenHeight()

            scale = min(screen_w / RlWindow.n_width, screen_h / RlWindow.n_height)

            draw_w = int(RlWindow.n_width * scale)
            draw_h = int(RlWindow.n_height * scale)

            offset_x = (screen_w - draw_w) // 2
            offset_y = (screen_h - draw_h) // 2

            dest = (offset_x, offset_y, draw_w, draw_h)

            # --- Draw scaled texture to the screen ---
            rl.BeginDrawing()
            rl.ClearBackground(rl.DARKGREEN)

            rl.DrawTexturePro(target.texture, source, dest, (0, 0), 0.0, rl.WHITE)

            rl.EndDrawing()

        rl.CloseWindow()

class Card:
    def __init__(self, suit, rank, x, y):
        self.suit = suit
        self.rank = rank
        self.revealed = False
        self.x = x
        self.y = y

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        card_text = f"{ranks[self.rank]} {suits[self.suit]}".encode("utf-8")
        card_background = rl.GRAY

        if self.revealed:
            card_background = rl.WHITE

        rl.DrawRectangle(self.x, self.y, RlWindow.n_el_width, RlWindow.n_el_height, card_background)
        rl.DrawRectangleLines(self.x, self.y, RlWindow.n_el_width, RlWindow.n_el_height, rl.BLACK)
        
        if self.revealed:
            rl.DrawText(card_text, self.x + 1, self.y + 1, RlWindow.n_font_size, suit_colours[self.suit])

    def set_revealed(self):
        self.revealed = True

    def set_hidden(self):
        self.revealed = False

    def is_clicked(self):
        rect = (self.x, self.y, RlWindow.n_el_width, RlWindow.n_el_height)
        mouse_pos = RlWindow.GetVirtualMousePosition()

        if self.revealed:
            if rl.CheckCollisionPointRec(mouse_pos.get_raw(), rect):
                if rl.IsMouseButtonPressed(rl.MOUSE_LEFT_BUTTON):
                    return True

        return False

def generate_standard_deck(n_suits):
    deck_suits = []

    if n_suits == 1:
        for i in range(4):
            deck_suits.append(0)
    elif n_suits == 2:
        for i in range(2):
            deck_suits.append(0)
            deck_suits.append(1)
    else:
        for i in range(4):
            deck_suits.append(i)

    deck = []

    for suit in deck_suits:
        for rank in ranks:
            deck.append(Card(suit, rank, 0, 0))

    return deck

# deck is a list so no reason to return
def shuffle(deck):
    for i in range(len(deck)):
        r = random.randint(0, len(deck) - 1)

        deck[i], deck[r] = deck[r], deck[i]

def is_valid_series(cards):
    """
    returns if a list of cards is valid, i.e. all cards are of the same suit
    and in decreasing rank order until the last card in the card holder (inclusive)
    """
    if len(cards) > 1:
        for i in range(len(cards) - 1):
            if cards[i].suit != cards[i + 1].suit or cards[i].rank - 1 != cards[i + 1].rank:
                return False

    return True

def check_holders_complete_series(card_holders):
    """
    checks the given card holders to see if they contain complete series
    i.e. a King to an Ace (13 cards) in decreasing rank order one after another of the same suit

    it returns all the found complete series as a list of tuples where each tuple is
    (card_holder_index, series_start_index)
    """
    complete_series = []

    for ch in card_holders:
        current_series = 1

        for ci in range(len(ch.cards) - 1, 0, -1):
            if ch.cards[ci].revealed and ch.cards[ci].suit == ch.cards[ci - 1].suit and ch.cards[ci].rank + 1 == ch.cards[ci - 1].rank:
                current_series += 1
            else:
                current_series = 1

            if current_series == 13:
                complete_series.append((card_holders.index(ch), ci - 12))
                break

    return complete_series