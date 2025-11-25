import raylib as rl
import random
from core import *

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
        self.y = RlWindow.n_gap_size
        self.vertical_offset = RlWindow.n_font_size

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
        rect = (self.x, self.y, RlWindow.n_el_width, RlWindow.n_height)
        mouse_pos = rl.GetMousePosition()

        if rl.CheckCollisionPointRec(mouse_pos, rect):
            if rl.IsMouseButtonReleased(rl.MOUSE_LEFT_BUTTON):
                return True

        return False

class HandCardHolder:
    def __init__(self):
        self.cards = []
        self.vertical_offset = RlWindow.n_font_size
        self.occupied = False
        self.card_source_index = -1

    def reset(self):
        self.cards.clear()
        self.set_unoccupied()

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
        self.width = int(RlWindow.n_el_width * 1.5)
        self.height = int(RlWindow.n_el_height / 4)
        self.x_pos = RlWindow.n_width - self.width - RlWindow.n_gap_size
        self.y_pos = RlWindow.n_height - self.height - RlWindow.n_gap_size

    def reset(self):
        self.remaining_deals = 5

    def draw(self):
        deal_text = f"Deal Cards\n({self.remaining_deals} remaining)".encode("utf-8")

        rl.DrawRectangle(self.x_pos, self.y_pos, self.width, self.height, rl.GRAY)
        rl.DrawRectangleLines(self.x_pos, self.y_pos, self.width, self.height, rl.BLACK)

        rl.DrawText(deal_text, self.x_pos + 1, self.y_pos + 1, RlWindow.n_font_size, rl.WHITE)

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

# traditionally you show the completed series with a king from
# the respective suit
# but we're cheap here
class CompletedLabel:
    def __init__(self, current_suits):
        self.suits = { suit: 0 for suit in range(current_suits) }
        self.width = RlWindow.n_el_width * 2
        self.height = RlWindow.n_font_size * (current_suits + 1) + RlWindow.n_gap_size

        self.x_pos = RlWindow.n_gap_size
        self.y_pos = RlWindow.n_height - self.height - RlWindow.n_gap_size

    def reset(self, current_suits):
        self.suits = { suit: 0 for suit in range(current_suits) }

    def complete(self, suit):
        self.suits[suit] += 1

    def get_total_completed(self):
        return sum([completed for completed in self.suits.values()])

    def draw(self):
        text = "Completed:\n"

        for index, n in self.suits.items():
            text += f"{suits[index]}: {n}\n"

        text = text.encode("utf-8")

        rl.DrawRectangle(self.x_pos, self.y_pos, self.width, self.height, rl.GRAY)
        rl.DrawRectangleLines(self.x_pos, self.y_pos, self.width, self.height, rl.BLACK)

        rl.DrawText(text, self.x_pos + 1, self.y_pos + 1, RlWindow.n_font_size, rl.WHITE)

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

# for picking up multiple cards
def is_valid_series(cards):
    if len(cards) > 1:
        for i in range(len(cards) - 1):
            if cards[i].suit != cards[i + 1].suit or cards[i].rank - 1 != cards[i + 1].rank:
                return False

    return True

def check_holders_complete_series(card_holders):
    for ch in card_holders:
        current_series = 1

        for ci in range(len(ch.cards) - 1, 0, -1):
            if ch.cards[ci].revealed and ch.cards[ci].suit == ch.cards[ci - 1].suit and ch.cards[ci].rank + 1 == ch.cards[ci - 1].rank:
                current_series += 1
            else:
                break

            if current_series == 13:
                completed_label.complete(ch.cards[ci].suit)
                ch.cards = ch.cards[:-13]
                break

class SpiderSolitaire(GameTemplate):
    def __init__(self, _n_suits):
        super().__init__()

        self.n_suits = _n_suits

        self.hand = HandCardHolder()
        self.card_holders = []
        self.all_cards = []
        self.deal_button = DealButton()
        self.completed_label = CompletedLabel(_n_suits)

        self.b_gameover = False

        self.v_states = []

        self.new_game(_n_suits)

    def new_game(self, _n_suits):
        self.n_suits = _n_suits

        self.hand.reset()
        self.card_holders.clear()
        self.all_cards.clear()
        self.deal_button.reset()
        self.completed_label.reset(_n_suits)

        for ch_i in range(10):
            self.card_holders.append(CardHolder(ch_i * RlWindow.n_el_width + (ch_i + 1) * RlWindow.n_gap_size))

        self.all_cards.extend(generate_standard_deck(self.n_suits))
        self.all_cards.extend(generate_standard_deck(self.n_suits))
        shuffle(self.all_cards)

        ch_i = 0
        while len(self.all_cards) > 50:
            if ch_i >= len(self.card_holders):
                ch_i = 0

            self.card_holders[ch_i].add_card(self.all_cards.pop())
            ch_i += 1

        ch_i = 0

        for ch in self.card_holders:
            ch.reveal_bottom_card()

        self.b_gameover = False

    def draw(self):
        if self.completed_label.get_total_completed == 8:
            self.b_gameover = True

        # logic
        if not self.b_gameover:
            selected_card_index = -1
            selected_holder_index = -1

            # check if we have any cards selected
            if not self.hand.occupied:
                for ch in self.card_holders:
                    for ci in range(len(ch.cards) - 1, -1, -1):
                        if ch.cards[ci].is_clicked():
                            self.hand.set_occupied(self.card_holders.index(ch))

                            selected_card_index = ci
                            selected_holder_index = self.card_holders.index(ch)
                            break

                if selected_card_index > -1 and is_valid_series(self.card_holders[selected_holder_index].cards[selected_card_index:]):
                    for ci in range(selected_card_index, len(self.card_holders[selected_holder_index].cards)):
                        self.hand.add_card(self.card_holders[selected_holder_index].cards.pop())

                    self.hand.cards.reverse()
                    selected_card_index = -1
                else:
                    self.hand.set_unoccupied()
                    selected_card_index = -1

            # if the hand is occupied but we released the the mouse button
            # the cards must be released too
            if self.hand.occupied and rl.IsMouseButtonReleased(rl.MOUSE_LEFT_BUTTON):
                for ch in self.card_holders:
                    if ch.is_released():
                        if len(ch.cards) == 0 or (ch.cards[-1].rank - 1 == self.hand.cards[0].rank):
                            self.hand.cards.reverse()

                            while len(self.hand.cards):
                                ch.add_card(self.hand.cards.pop())

                            self.hand.set_unoccupied()

                # if the hand is still occupied
                # pass the cards back over to the original card holder
                if self.hand.occupied:
                    self.hand.cards.reverse()

                    while len(self.hand.cards):
                        self.card_holders[self.hand.get_csi()].add_card(self.hand.cards.pop())

                    self.hand.set_unoccupied()

            # we can only deal with an unoccupied hand
            if not self.hand.occupied:
                if self.deal_button.is_clicked() and self.deal_button.can_deal():
                    self.deal_button.deal()
                    for i in range(10):
                        self.card_holders[i].add_card(self.all_cards.pop())

            check_holders_complete_series(self.card_holders)

        # the actual drawing
        for ch in self.card_holders:
            ch.draw_cards()

            if not self.hand.occupied:
                ch.reveal_bottom_card()

        self.completed_label.draw()
        self.deal_button.draw()

        self.hand.draw_cards()