import raylib as rl

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

class RlWindow:
    n_width = 1280
    n_height = 720

    # for card, deck, etc.
    n_el_width = n_width // 11
    n_el_height = n_height // 4

    # qol
    n_font_size = n_width // 60
    n_gap_size = n_width // 128

    def __init__(self):
        pass

class GameTemplate:
    def __init__(self):
        pass

    def draw(self):
        pass

    def start(self):
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
            rl.ClearBackground(rl.BLACK)

            rl.DrawTexturePro(target.texture, source, dest, (0, 0), 0.0, rl.WHITE)

            rl.EndDrawing()

        rl.CloseWindow()