import raylib as rl
import copy

from core import *

class CardHolder:
    def __init__(self, x):
        self.cards = []
        self.x = x
        self.y = RlWindow.n_gap_size
        self.vertical_offset = RlWindow.n_font_size

    def add_card(self, card):
        self.cards.append(card)

    def draw(self):
        # outline
        rl.DrawRectangleLines(self.x, self.y, RlWindow.n_el_width, RlWindow.n_el_height, rl.BLACK)

        i = 0
        for card in self.cards:
            card.set_pos(self.x, self.y + i * self.vertical_offset)
            card.draw()
            i += 1

    def reveal_bottom_card(self):
        if self.cards and (not self.cards[-1].revealed):
            self.cards[-1].set_revealed()

    def is_released(self):
        mouse_pos = RlWindow.GetVirtualMousePosition()

        rect = (self.x, self.y, RlWindow.n_el_width, RlWindow.n_height)
        mouse_rect = (mouse_pos.x, mouse_pos.y, RlWindow.n_gap_size - 1, 2)

        # we're doing a naughty thang here
        # checking collision against the mouse's position works, but it may not be intuitive
        # in all cases, because it only checks the mouse's top left x,y (as intended)
        # however, if the rest of the mouse is hovering over a valid card holder, it should drop
        # the held cards there
        # so we get the smallest width that can only overlap one card holder, which is
        # the global gap size - 1 :D
        # the height doesn't really matter as card holders are infinitely tall anyway
        if rl.CheckCollisionRecs(mouse_rect, rect):
            if rl.IsMouseButtonReleased(rl.MOUSE_LEFT_BUTTON):
                return True

        return False

class HandCardHolder:
    def __init__(self):
        self.cards = []
        self.vertical_offset = RlWindow.n_font_size
        self.occupied = False
        self.card_source_index = -1

        self.card_x_diff = -1
        self.card_y_diff = -1

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

        self.card_x_diff = -1
        self.card_y_diff = -1

    def get_csi(self):
        return self.card_source_index

    def draw_cards(self):
        i = 0

        mouse_pos = RlWindow.GetVirtualMousePosition()
        x = int(mouse_pos.x)
        y = int(mouse_pos.y)

        if self.occupied:
            card0_x = self.cards[0].x
            card0_y = self.cards[0].y

            if self.card_x_diff == -1:
                self.card_x_diff = x - card0_x
                self.card_y_diff = y - card0_y

            for card in self.cards:
                card.set_pos(x - self.card_x_diff, y - self.card_y_diff + i * self.vertical_offset)
                card.draw()
                i += 1

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

        self.height = RlWindow.n_font_size * (current_suits + 1) + RlWindow.n_gap_size
        self.y_pos = RlWindow.n_height - self.height - RlWindow.n_gap_size

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

class GenericButton:
    def __init__(self, _x, _y, _width, _height, _text, _func):
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height
        self.text = _text.encode("utf-8")

        self.func = _func

    def exec_func(self):
        self.func()

    def draw(self):
        rl.DrawRectangle(self.x, self.y, self.width, self.height, rl.GRAY)
        rl.DrawRectangleLines(self.x, self.y, self.width, self.height, rl.BLACK)

        rl.DrawText(self.text, self.x + 1, self.y + 1, RlWindow.n_font_size, rl.WHITE)

    def is_clicked(self):
        rect = (self.x, self.y, self.width, self.height)
        mouse_pos = RlWindow.GetVirtualMousePosition()

        if rl.CheckCollisionPointRec(mouse_pos.get_raw(), rect):
            if rl.IsMouseButtonPressed(rl.MOUSE_LEFT_BUTTON):
                return True

        return False

class DealButton(GenericButton):
    def __init__(self):
        self.remaining_deals = 5

        super().__init__(
            RlWindow.n_width - int(RlWindow.n_el_width * 1.5) - RlWindow.n_gap_size, 
            RlWindow.n_height - RlWindow.n_font_size * 2 - RlWindow.n_gap_size, 
            int(RlWindow.n_el_width * 1.5), 
            RlWindow.n_font_size * 2, 
            f"Deal Cards\n({self.remaining_deals} remaining)",
            None
        )

    def update_text(self):
        self.text = f"Deal Cards\n({self.remaining_deals} remaining)".encode("utf-8")

    def reset(self):
        self.remaining_deals = 5
        self.update_text()

    def update(self):
        self.remaining_deals -= 1
        self.update_text()

    def can_deal(self):
        return self.remaining_deals > 0

class NewGameButton(GenericButton):
    def __init__(self, _x, _y, new_game_func, _n_suits):
        self.n_suits = _n_suits

        super().__init__(
            _x, 
            _y, 
            RlWindow.n_el_width, 
            RlWindow.n_font_size * 2, 
            f"New Game\n({self.n_suits} suits)", 
            new_game_func
        )

    def exec_func(self):
        self.func(self.n_suits)

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

        self.new_game_buttons = []

        self.new_game_buttons.append(NewGameButton(
            self.completed_label.width + RlWindow.n_gap_size * 2,
            RlWindow.n_height - RlWindow.n_font_size * 2 - RlWindow.n_gap_size,
            self.new_game,
            1
        ))

        self.new_game_buttons.append(NewGameButton(
            self.completed_label.width + RlWindow.n_el_width + RlWindow.n_gap_size * 3,
            RlWindow.n_height - RlWindow.n_font_size * 2 - RlWindow.n_gap_size,
            self.new_game,
            2
        ))

        self.new_game_buttons.append(NewGameButton(
            self.completed_label.width + RlWindow.n_el_width * 2 + RlWindow.n_gap_size * 4,
            RlWindow.n_height - RlWindow.n_font_size * 2 - RlWindow.n_gap_size,
            self.new_game,
            4
        ))

        self.undo_button = GenericButton(
            self.completed_label.width + RlWindow.n_el_width * 3 + RlWindow.n_gap_size * 5,
            RlWindow.n_height - RlWindow.n_font_size - RlWindow.n_gap_size,
            RlWindow.n_el_width,
            RlWindow.n_font_size,
            "Undo",
            self.set_last_state
        )

        self.new_game(_n_suits)

    def save_state(self):
        self.v_states.append((
            copy.deepcopy(self.card_holders),
            copy.deepcopy(self.all_cards),
            copy.deepcopy(self.deal_button),
            copy.deepcopy(self.completed_label)
        ))

    # gotta pop twice cause the first popped one is the current state
    def set_last_state(self):
        if len(self.v_states) > 1:
            self.v_states.pop()

            last_state = self.v_states[-1]

            self.card_holders    = copy.deepcopy(last_state[0])
            self.all_cards       = copy.deepcopy(last_state[1])
            self.deal_button     = copy.deepcopy(last_state[2])
            self.completed_label = copy.deepcopy(last_state[3])

    def new_game(self, _n_suits):
        self.n_suits = _n_suits

        self.hand.reset()
        self.card_holders.clear()
        self.all_cards.clear()
        self.deal_button.reset()
        self.completed_label.reset(_n_suits)

        self.v_states.clear()

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

        for ch in self.card_holders:
            ch.reveal_bottom_card()

        self.save_state()

    def game_over(self):
        return self.completed_label.get_total_completed == 8

    def deal_cards(self):
        for i in range(len(self.card_holders)):
            self.card_holders[i].add_card(self.all_cards.pop())

    def remove_complete_series(self, complete_series):
        for chi, ci in complete_series:
            self.completed_label.complete(self.card_holders[chi].cards[ci].suit)
            self.card_holders[chi].cards = self.card_holders[chi].cards[:-13]

    def draw(self):
        b_moved = False

        # logic
        if not self.game_over():
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

                            # i.e. it was dropped back where it came from
                            if self.hand.get_csi() != self.card_holders.index(ch):
                                b_moved = True

                            self.hand.set_unoccupied()

                            break

                # if the hand is still occupied
                # pass the cards back over to the original card holder
                if self.hand.occupied:
                    self.hand.cards.reverse()

                    while len(self.hand.cards):
                        self.card_holders[self.hand.get_csi()].add_card(self.hand.cards.pop())

                    self.hand.set_unoccupied()

            complete_series = check_holders_complete_series(self.card_holders)

            if len(complete_series) > 0:
                self.remove_complete_series(complete_series)
                b_moved = True

            # we can only deal with an unoccupied hand
            if not self.hand.occupied:
                if self.deal_button.is_clicked() and self.deal_button.can_deal():
                    self.deal_cards()
                    self.deal_button.update()
                    b_moved = True

                for new_game_btn in self.new_game_buttons:
                    if new_game_btn.is_clicked():
                        new_game_btn.exec_func()

                if self.undo_button.is_clicked():
                    self.undo_button.exec_func()

        if b_moved:
            self.save_state()

        # the actual drawing
        for ch in self.card_holders:
            ch.draw()

            if not self.hand.occupied:
                ch.reveal_bottom_card()

        self.completed_label.draw()
        
        for new_game_btn in self.new_game_buttons:
            new_game_btn.draw()

        self.undo_button.draw()

        self.deal_button.draw()

        self.hand.draw_cards()