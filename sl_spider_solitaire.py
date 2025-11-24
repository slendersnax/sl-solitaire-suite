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

g_window_width = 1280
g_window_height = 720
g_font_size = int(g_window_width / 60)
g_gap_size = int(g_window_width / 128)

# for card, deck, etc.
g_element_width = int(g_window_width / 11)
g_element_height = int(g_window_height / 4)

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

        rl.DrawRectangle(self.x, self.y, g_element_width, g_element_height, card_background)
        rl.DrawRectangleLines(self.x, self.y, g_element_width, g_element_height, rl.BLACK)
        
        if self.revealed:
            rl.DrawText(card_text, self.x + 1, self.y + 1, g_font_size, suit_colours[self.suit])

    def set_revealed(self):
        self.revealed = True

    def set_hidden(self):
        self.revealed = False

    def is_clicked(self):
        rect = (self.x, self.y, g_element_width, g_element_height)
        mouse_pos = rl.GetMousePosition()

        if self.revealed:
            if rl.CheckCollisionPointRec(mouse_pos, rect):
                if rl.IsMouseButtonPressed(rl.MOUSE_LEFT_BUTTON):
                    return True

        return False


class CardHolder:
    def __init__(self, x):
        self.cards = []
        self.x = x
        self.y = g_gap_size
        self.vertical_offset = g_font_size

    def add_card(self, card):
        self.cards.append(card)

    def draw_cards(self):
        i = 0
        for card in self.cards:
            card.set_pos(self.x, self.y + i * self.vertical_offset)
            card.draw()
            i += 1

    def reveal_bottom_card(self):
        if self.cards and (not self.cards[-1].revealed):
            self.cards[-1].set_revealed()

    # TODO: check if card rectangles collide instead of mouse pointer
    def is_released(self):
        rect = (self.x, self.y, g_element_width, g_window_height)
        mouse_pos = rl.GetMousePosition()

        if rl.CheckCollisionPointRec(mouse_pos, rect):
            if rl.IsMouseButtonReleased(rl.MOUSE_LEFT_BUTTON):
                return True

        return False

class HandCardHolder:
    def __init__(self):
        self.cards = []
        self.vertical_offset = g_font_size
        self.occupied = False
        self.card_source_index = -1

    def add_card(self, card):
        self.cards.append(card)

    def set_occupied(self, csi):
        self.occupied = True
        self.card_source_index = csi

    def set_unoccupied(self):
        self.occupied = False
        self.card_source_index = -1

    def get_csi(self):
        return self.card_source_index

    def draw_cards(self):
        i = 0

        mouse_pos = rl.GetMousePosition()
        x = int(mouse_pos.x)
        y = int(mouse_pos.y)

        for card in self.cards:
            card.set_pos(x, y + i * self.vertical_offset)
            card.draw()
            i += 1

class DealButton:
    def __init__(self):
        self.remaining_deals = 5
        self.width = int(g_element_width * 1.5)
        self.height = int(g_element_height / 4)
        self.x_pos = g_window_width - self.width - g_gap_size
        self.y_pos = g_window_height - self.height - g_gap_size

    def draw(self):
        deal_text = f"Deal Cards\n({self.remaining_deals} remaining)".encode("utf-8")

        rl.DrawRectangle(self.x_pos, self.y_pos, self.width, self.height, rl.GRAY)
        rl.DrawRectangleLines(self.x_pos, self.y_pos, self.width, self.height, rl.BLACK)

        rl.DrawText(deal_text, self.x_pos + 1, self.y_pos + 1, g_font_size, rl.WHITE)

    def can_deal(self):
        return self.remaining_deals > 0

    def deal(self):
        self.remaining_deals -= 1

    def is_clicked(self):
        rect = (self.x_pos, self.y_pos, self.width, self.height)
        mouse_pos = rl.GetMousePosition()

        if rl.CheckCollisionPointRec(mouse_pos, rect):
            if rl.IsMouseButtonPressed(rl.MOUSE_LEFT_BUTTON):
                return True

        return False

def generate_standard_deck(nSuits):
    global suits
    global ranks

    deck_suits = []

    if nSuits == 1:
        for i in range(4):
            deck_suits.append(0)
    elif nSuits == 2:
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

# for picking up multiple cards
def is_valid_series(cards):
    for i in range(len(cards) - 1):
        if cards[i].suit != cards[i + 1].suit or cards[i].rank - 1 != cards[i + 1].rank:
            return False

    return True


# rl.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE | rl.FLAG_WINDOW_MAXIMIZED)
rl.InitWindow(g_window_width, g_window_height, b"sl spider solitaire")
rl.SetTargetFPS(60)

hand = HandCardHolder()
card_holders = []
all_cards = []
deal_button = DealButton()

for ch_i in range(10):
    card_holders.append(CardHolder(ch_i * g_element_width + (ch_i + 1) * g_gap_size))

all_cards.extend(generate_standard_deck(2))
all_cards.extend(generate_standard_deck(2))
shuffle(all_cards)

ch_i = 0
while len(all_cards) > 50:
    if ch_i >= len(card_holders):
        ch_i = 0

    card_holders[ch_i].add_card(all_cards.pop())
    ch_i += 1

ch_i = 0

for ch in card_holders:
    ch.reveal_bottom_card()

while not rl.WindowShouldClose():
    rl.BeginDrawing()
    rl.ClearBackground(rl.DARKGREEN)

    selected_card_index = -1
    selected_holder_index = -1

    # check if we have any cards selected
    if not hand.occupied:
        for ch in card_holders:
            for ci in range(len(ch.cards) - 1, 0, -1):
                if ch.cards[ci].is_clicked():
                    hand.set_occupied(card_holders.index(ch))

                    selected_card_index = ci
                    selected_holder_index = card_holders.index(ch)
                    break

        if selected_card_index > -1 and is_valid_series(card_holders[selected_holder_index].cards[selected_card_index:]):
            for ci in range(selected_card_index, len(card_holders[selected_holder_index].cards)):
                hand.add_card(card_holders[selected_holder_index].cards.pop())

            hand.cards.reverse()
            selected_card_index = -1
        else:
            hand.set_unoccupied()
            selected_card_index = -1

    # if the hand is occupied but we released the the mouse button
    # the cards must be released too
    if hand.occupied and rl.IsMouseButtonReleased(rl.MOUSE_LEFT_BUTTON):
        for ch in card_holders:
            if ch.is_released():
                if len(ch.cards) == 0 or (ch.cards[-1].rank - 1 == hand.cards[0].rank):
                    hand.cards.reverse()

                    while len(hand.cards):
                        ch.add_card(hand.cards.pop())

                    hand.set_unoccupied()

        # if the hand is still occupied
        # pass the cards back over to the original card holder
        if hand.occupied:
            hand.cards.reverse()

            while len(hand.cards):
                card_holders[hand.get_csi()].add_card(hand.cards.pop())

            hand.set_unoccupied()

    for ch in card_holders:
        ch.draw_cards()

        if not hand.occupied:
            ch.reveal_bottom_card()

    deal_button.draw()

    hand.draw_cards()

    if deal_button.is_clicked() and deal_button.can_deal():
        deal_button.deal()
        for i in range(10):
            card_holders[i].add_card(all_cards.pop())

    rl.EndDrawing()
rl.CloseWindow()