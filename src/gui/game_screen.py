from __future__ import annotations

import pygame
import threading

from engine.board import Color, PieceType
from engine.gamestate import GameOutcome, GameResult, get_game_outcome, play_move
from engine.move import Move
from engine.movegen import generate_legal_moves
from engine.positions import make_starting_board
from gui.assets import get_sprite
from gui.constants import (
    ACCENT,
    BG,
    BOARD_DARK,
    BOARD_LIGHT,
    BOARD_PX,
    BOARD_X,
    BOARD_Y,
    BORDER,
    CARD_BG,
    CLOCK_ACTIVE_BG,
    CLOCK_ACTIVE_FG,
    CLOCK_INACTIVE_BG,
    CLOCK_INACTIVE_FG,
    FILE_NAMES,
    HIGHLIGHT_LAST_FROM,
    HIGHLIGHT_LAST_TO,
    HIGHLIGHT_LEGAL,
    HIGHLIGHT_SEL,
    HIST_W,
    HIST_X,
    INFO_W,
    INFO_X,
    PROMO_CIRCLE_BG,
    PROMO_HOVER_BG,
    RANK_LABEL_W,
    SQ_SIZE,
    TEXT_DARK,
    TEXT_MUTED,
    WINDOW_H,
    WINDOW_W,
    get_font,
)
from gui.main_menu import GameConfig
from bots.progress import BotProgress

_BOT_MOVE_EVENT = pygame.USEREVENT + 1
_BOT_DELAY_MS = 300


def _is_evaluating_bot(bot) -> bool:
    from bots.random_bot import RandomBot
    return bot is not None and not isinstance(bot, RandomBot)


def _net_captured_count(board, color: Color, pt: PieceType) -> int:
    """Returns how many more pieces of type pt `color` has remaining than the opponent.

    A positive result means the opponent has lost more of that piece type,
    so the info panel shows that many opponent-colored icons next to `color`.
    """
    opp = Color(1 - int(color))
    color_remaining = bin(board.pieces[color][pt]).count("1")
    opp_remaining = bin(board.pieces[opp][pt]).count("1")
    return max(0, color_remaining - opp_remaining)


def _next_selection(
    selected_sq: int | None,
    sq: int,
    piece_info: tuple[Color, PieceType] | None,
    color: Color,
) -> int | None:
    """Returns the square to select after a board click, or None to deselect.

    Selecting the already-selected square deselects it. Clicking a different
    own piece switches the selection. Clicking an empty square or opponent
    piece deselects.
    """
    if piece_info is not None and piece_info[0] == color:
        if sq == selected_sq:
            return None
        return sq
    return None


class GameScreen:
    def __init__(self, surface: pygame.Surface, config: GameConfig) -> None:
        self._surf = surface
        self._config = config
        self._board = make_starting_board(config.starting_mode)
        self._legal_moves: list[Move] = generate_legal_moves(self._board)
        self._selected_sq: int | None = None
        self._move_history: list[tuple[str, str]] = []  # list of (white_pgn, black_pgn)
        self._current_half: str = ""  # white pgn waiting for black response
        # Clocks
        use_clock = config.time_seconds > 0
        self._clocks = {
            Color.WHITE: config.time_seconds if use_clock else -1.0,
            Color.BLACK: config.time_seconds if use_clock else -1.0,
        }
        self._increment = config.increment_seconds
        self._use_clock = use_clock
        # Game outcome
        self._outcome: GameOutcome | None = None
        # Promotion state
        self._promo_move_base: Move | None = None   # move without promotion set
        self._promo_sq: int | None = None           # the destination square
        self._promo_hover: int | None = None        # 0=Q, 1=R, 2=N
        self._last_move: tuple[int, int] | None = None  # (from_sq, to_sq)
        # Rects set by draw() — initialised here so handle_event() can safely reference them
        self._back_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._new_game_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._menu_from_over_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        # Bot threading
        self._bot_thread: threading.Thread | None = None
        self._bot_progress: BotProgress | None = None
        self._bot_result: list[Move | None] = [None]
        self._last_eval: dict[Color, float | None] = {
            Color.WHITE: None,
            Color.BLACK: None,
        }
        # Schedule bot if it moves first
        self._maybe_schedule_bot()

    # ------------------------------------------------------------------
    # Public interface

    def handle_event(self, event: pygame.event.Event):
        from gui.main_menu import MainMenuScreen
        if self._outcome is not None:
            return self._handle_game_over_event(event)
        if self._promo_sq is not None:
            self._handle_promo_event(event)
            return None
        if event.type == _BOT_MOVE_EVENT:
            pygame.time.set_timer(_BOT_MOVE_EVENT, 0)
            self._start_bot_thread()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._back_rect.collidepoint(event.pos):
                return MainMenuScreen(self._surf)
            self._handle_board_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self._promo_hover = None
        return None

    def update(self, dt: float) -> None:
        if self._outcome is not None:
            return
        if self._promo_sq is not None:
            return
        # Poll bot thread for completion
        if self._bot_thread is not None and not self._bot_thread.is_alive():
            move = self._bot_result[0]
            color = self._board.side_to_move
            if self._bot_progress is not None and self._bot_progress.eval is not None:
                self._last_eval[color] = self._bot_progress.eval
            self._bot_thread = None
            self._bot_progress = None
            if move is not None:
                self._make_move(move)
        # Clock
        if self._use_clock:
            color = self._board.side_to_move
            self._clocks[color] -= dt
            if self._clocks[color] <= 0:
                self._clocks[color] = 0
                loser = color
                winner_result = (
                    GameResult.BLACK_WINS if loser == Color.WHITE
                    else GameResult.WHITE_WINS
                )
                from engine.gamestate import _side_has_insufficient_material
                winner_color = Color(1 - int(loser))
                if _side_has_insufficient_material(self._board, winner_color):
                    self._outcome = GameOutcome(GameResult.DRAW, "Unzureichendes Material")
                else:
                    self._outcome = GameOutcome(winner_result, "Zeit abgelaufen")

    def draw(self) -> None:
        self._surf.fill(BG)
        self._draw_board()
        self._draw_info_panel()
        self._draw_history_panel()
        if self._promo_sq is not None:
            self._draw_promotion_overlay()
        if self._outcome is not None:
            self._draw_game_over_overlay()

    # ------------------------------------------------------------------
    # Board drawing

    def _sq_to_pixel(self, sq: int) -> tuple[int, int]:
        rank = sq // 6
        file = sq % 6
        # White at bottom: rank 0 = bottom row
        screen_row = 5 - rank
        x = BOARD_X + file * SQ_SIZE
        y = BOARD_Y + screen_row * SQ_SIZE
        return x, y

    def _pixel_to_sq(self, pos: tuple[int, int]) -> int | None:
        bx, by = pos[0] - BOARD_X, pos[1] - BOARD_Y
        if not (0 <= bx < BOARD_PX and 0 <= by < BOARD_PX):
            return None
        file = bx // SQ_SIZE
        screen_row = by // SQ_SIZE
        rank = 5 - screen_row
        return rank * 6 + file

    def _draw_board(self) -> None:
        surf = self._surf
        board = self._board

        # Rank labels
        font = get_font("serif", 13)
        for rank in range(6):
            screen_row = 5 - rank
            y = BOARD_Y + screen_row * SQ_SIZE + SQ_SIZE // 2
            t = font.render(str(rank + 1), True, TEXT_MUTED)
            surf.blit(t, (BOARD_X - RANK_LABEL_W + 2, y - t.get_height() // 2))

        # Legal move destinations for selected piece
        legal_dests = set()
        capture_dests = set()
        if self._selected_sq is not None:
            for m in self._legal_moves:
                if m.from_sq == self._selected_sq:
                    if m.captured is not None:
                        capture_dests.add(m.to_sq)
                    else:
                        legal_dests.add(m.to_sq)

        for sq in range(36):
            x, y = self._sq_to_pixel(sq)
            rank, file = divmod(sq, 6)
            base_color = BOARD_LIGHT if (rank + file) % 2 == 0 else BOARD_DARK

            # Background color
            if sq == self._selected_sq:
                color = HIGHLIGHT_SEL
            elif sq in legal_dests or sq in capture_dests:
                color = HIGHLIGHT_LEGAL
            elif self._last_move and sq == self._last_move[1]:
                color = HIGHLIGHT_LAST_TO
            elif self._last_move and sq == self._last_move[0]:
                color = HIGHLIGHT_LAST_FROM
            else:
                color = base_color
            pygame.draw.rect(surf, color, (x, y, SQ_SIZE, SQ_SIZE))

            # Legal move dot for empty squares
            if sq in legal_dests:
                cx, cy = x + SQ_SIZE // 2, y + SQ_SIZE // 2
                r = SQ_SIZE // 7
                pygame.draw.circle(surf, (0, 0, 0, 80), (cx, cy), r)

            # Piece sprite
            piece_info = board.get_piece_at(sq)
            if piece_info is not None:
                sprite = get_sprite(piece_info[0], piece_info[1])
                surf.blit(sprite, (x, y))

        # File labels
        for file in range(6):
            x = BOARD_X + file * SQ_SIZE + SQ_SIZE // 2
            y = BOARD_Y + BOARD_PX + 2
            t = font.render(FILE_NAMES[file], True, TEXT_MUTED)
            surf.blit(t, (x - t.get_width() // 2, y))

    # ------------------------------------------------------------------
    # Click handling

    def _handle_board_click(self, pos: tuple[int, int]) -> None:
        sq = self._pixel_to_sq(pos)
        if sq is None:
            self._selected_sq = None
            return
        if self._is_bot_turn():
            return

        color = self._board.side_to_move
        piece_info = self._board.get_piece_at(sq)

        # Clicking a legal destination
        if self._selected_sq is not None:
            matching = [m for m in self._legal_moves
                        if m.from_sq == self._selected_sq and m.to_sq == sq]
            if matching:
                if matching[0].promotion is not None:
                    self._promo_move_base = matching[0]
                    self._promo_sq = sq
                    self._selected_sq = None
                    return
                self._make_move(matching[0])
                self._selected_sq = None
                return

        # Select own piece (deselects on re-click)
        self._selected_sq = _next_selection(self._selected_sq, sq, piece_info, color)

    def _make_move(self, move: Move) -> None:
        pgn = move.to_pgn()
        play_move(self._board, move)
        self._last_move = (move.from_sq, move.to_sq)
        if self._use_clock:
            moved_color = Color(1 - int(self._board.side_to_move))
            self._clocks[moved_color] = max(0, self._clocks[moved_color] + self._increment)
        self._record_pgn(pgn)
        self._legal_moves = generate_legal_moves(self._board)
        self._outcome = get_game_outcome(self._board)
        if self._outcome is None:
            self._maybe_schedule_bot()

    def _record_pgn(self, pgn: str) -> None:
        if self._board.side_to_move == Color.WHITE:
            # Black just moved (after apply, side flipped)
            self._move_history.append((self._current_half, pgn))
            self._current_half = ""
        else:
            self._current_half = pgn

    # ------------------------------------------------------------------
    # Promotion

    def _handle_promo_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._promo_hover = self._promo_circle_index(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self._promo_circle_index(event.pos)
            if idx is not None:
                promo_types = [PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT]
                base = self._promo_move_base
                assert base is not None
                move = Move(base.from_sq, base.to_sq, base.piece, base.color,
                            captured=base.captured, promotion=promo_types[idx])
                self._promo_sq = None
                self._promo_move_base = None
                self._promo_hover = None
                self._make_move(move)
            else:
                self._promo_sq = None
                self._promo_move_base = None
                self._promo_hover = None

    def _promo_circle_rects(self) -> list[pygame.Rect]:
        assert self._promo_sq is not None
        x, y = self._sq_to_pixel(self._promo_sq)
        rects = []
        color = self._board.side_to_move  # promo move not yet applied
        # For white, pawn just reached rank 5 (top) — circles go downward
        for i in range(3):
            dy = i * SQ_SIZE if color == Color.WHITE else -i * SQ_SIZE
            rects.append(pygame.Rect(x, y + dy, SQ_SIZE, SQ_SIZE))
        return rects

    def _promo_circle_index(self, pos: tuple[int, int]) -> int | None:
        for i, r in enumerate(self._promo_circle_rects()):
            if r.collidepoint(pos):
                return i
        return None

    def _draw_promotion_overlay(self) -> None:
        surf = self._surf
        # Dim the board
        dim = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        surf.blit(dim, (BOARD_X, BOARD_Y))

        promo_pieces = [PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT]
        color = self._board.side_to_move
        rects = self._promo_circle_rects()

        for i, (r, pt) in enumerate(zip(rects, promo_pieces)):
            bg = PROMO_HOVER_BG if i == self._promo_hover else PROMO_CIRCLE_BG
            pygame.draw.circle(surf, bg, r.center, SQ_SIZE // 2 - 4)
            sprite = get_sprite(color, pt)
            surf.blit(sprite, r.topleft)

    # ------------------------------------------------------------------
    # Bot

    def _is_bot_turn(self) -> bool:
        color = self._board.side_to_move
        if color == Color.WHITE:
            return self._config.white_bot is not None
        return self._config.black_bot is not None

    def _maybe_schedule_bot(self) -> None:
        if self._is_bot_turn() and self._outcome is None:
            pygame.time.set_timer(_BOT_MOVE_EVENT, _BOT_DELAY_MS)

    def _start_bot_thread(self) -> None:
        if self._outcome is not None:
            return
        if self._bot_thread is not None:
            return  # already thinking
        color = self._board.side_to_move
        bot = self._config.white_bot if color == Color.WHITE else self._config.black_bot
        if bot is None or not self._legal_moves:
            return
        from bots.personalities import calculate_time_budget
        remaining = self._clocks[color] if self._use_clock else None
        move_number = self._board.ply // 2 + 1
        budget = calculate_time_budget(remaining, move_number, self._increment)
        board_copy = self._board.copy()
        self._bot_result = [None]
        self._bot_progress = BotProgress()
        result_holder = self._bot_result
        progress = self._bot_progress

        def _run() -> None:
            result_holder[0] = bot.choose_move(board_copy, budget, progress)

        self._bot_thread = threading.Thread(target=_run, daemon=True)
        self._bot_thread.start()

    # ------------------------------------------------------------------
    # Info panel

    def _draw_info_panel(self) -> None:
        surf = self._surf
        font_sm = get_font("serif", 11)
        font_md = get_font("serif", 14)
        font_clock = get_font("monospace", 16)
        font_label = get_font("serif", 10)
        font_eval = get_font("monospace", 24)

        panel_rect = pygame.Rect(INFO_X, 0, INFO_W, WINDOW_H)
        pygame.draw.rect(surf, CARD_BG, panel_rect)
        pygame.draw.line(surf, BORDER, (INFO_X, 0), (INFO_X, WINDOW_H), 1)
        pygame.draw.line(surf, BORDER, (INFO_X + INFO_W, 0), (INFO_X + INFO_W, WINDOW_H), 1)

        active = self._board.side_to_move
        y = 12

        def draw_player(color: Color, name: str, bot_label: str, evaluating: bool) -> None:
            nonlocal y
            is_active = (color == active and self._outcome is None)
            # Name + type
            nt = font_md.render(name, True, TEXT_DARK)
            surf.blit(nt, (INFO_X + 8, y))
            y += nt.get_height() + 2
            bt = font_sm.render(bot_label, True, TEXT_MUTED)
            surf.blit(bt, (INFO_X + 8, y))
            y += bt.get_height() + 4
            # Clock
            if self._use_clock:
                secs = max(0, self._clocks[color])
                mins_left = int(secs) // 60
                secs_left = int(secs) % 60
                clock_str = f"{mins_left}:{secs_left:02d}"
                cb = CLOCK_ACTIVE_BG if is_active else CLOCK_INACTIVE_BG
                cf = CLOCK_ACTIVE_FG if is_active else CLOCK_INACTIVE_FG
                cr = pygame.Rect(INFO_X + INFO_W - 72, y - 22, 64, 24)
                pygame.draw.rect(surf, cb, cr, border_radius=3)
                ct = font_clock.render(clock_str, True, cf)
                surf.blit(ct, (cr.centerx - ct.get_width() // 2,
                               cr.centery - ct.get_height() // 2))
            y += 6
            # Captured pieces as sprite images (no +N text)
            self._draw_captured_images(surf, INFO_X + 8, y, color)
            y += 20
            # Eval: only for evaluating bots
            if evaluating:
                lbl = font_label.render(
                    f"EVAL {'WEISS' if color == Color.WHITE else 'SCHWARZ'}",
                    True, TEXT_MUTED
                )
                surf.blit(lbl, (INFO_X + 8, y))
                y += lbl.get_height() + 3

                is_thinking = (
                    self._bot_thread is not None
                    and self._board.side_to_move == color
                )
                if is_thinking and self._bot_progress is not None:
                    current_eval = self._bot_progress.eval
                else:
                    current_eval = self._last_eval[color]

                self._draw_eval_bar(
                    surf, pygame.Rect(INFO_X + 8, y, INFO_W - 16, 8), color, current_eval
                )
                y += 14

                if current_eval is not None:
                    sign = "+" if current_eval > 0 else ""
                    eval_str = f"{sign}{current_eval:.2f}"
                    if current_eval > 0:
                        eval_color = ACCENT
                    elif current_eval < 0:
                        eval_color = (160, 60, 60)
                    else:
                        eval_color = TEXT_MUTED
                else:
                    eval_str = "—"
                    eval_color = TEXT_MUTED
                et = font_eval.render(eval_str, True, eval_color)
                surf.blit(et, (INFO_X + INFO_W // 2 - et.get_width() // 2, y))
                y += et.get_height() + 2

                # Depth / sims during thinking
                if is_thinking and self._bot_progress is not None:
                    from bots.minimax_bot import MinimaxBot
                    from bots.mcts_bot import MCTSBot
                    bot = self._config.white_bot if color == Color.WHITE else self._config.black_bot
                    if isinstance(bot, MinimaxBot) and self._bot_progress.depth is not None:
                        status_str = f"Tiefe {self._bot_progress.depth}"
                    elif isinstance(bot, MCTSBot) and self._bot_progress.sims is not None:
                        status_str = f"{self._bot_progress.sims:,} Sims".replace(",", " ")
                    else:
                        status_str = None
                    if status_str is not None:
                        st = font_label.render(status_str, True, TEXT_MUTED)
                        surf.blit(st, (INFO_X + INFO_W // 2 - st.get_width() // 2, y))
                        y += st.get_height() + 4
                    else:
                        y += 4
                else:
                    y += 4

        # Black at top
        black_bot = self._config.black_bot
        black_bot_label = (
            f"{type(black_bot).__name__} · Schwarz"
            if black_bot
            else "Mensch · Schwarz"
        )
        draw_player(Color.BLACK,
                    self._config.black_name,
                    black_bot_label,
                    evaluating=_is_evaluating_bot(black_bot))

        # White
        white_bot = self._config.white_bot
        white_bot_label = (
            f"{type(white_bot).__name__} · Weiß"
            if white_bot
            else "Mensch · Weiß"
        )
        draw_player(Color.WHITE,
                    self._config.white_name,
                    white_bot_label,
                    evaluating=_is_evaluating_bot(white_bot))

        # Back button pinned to panel bottom
        back_rect = pygame.Rect(INFO_X + 8, WINDOW_H - 44, INFO_W - 16, 28)
        pygame.draw.rect(surf, CARD_BG, back_rect, border_radius=3)
        pygame.draw.rect(surf, BORDER, back_rect, 1, border_radius=3)
        bt2 = font_sm.render("← Zurück zum Menü", True, TEXT_MUTED)
        surf.blit(bt2, (back_rect.centerx - bt2.get_width() // 2,
                        back_rect.centery - bt2.get_height() // 2))
        self._back_rect = back_rect

    def _draw_eval_bar(self, surf: pygame.Surface, rect: pygame.Rect,
                       color: Color, eval_value: float | None) -> None:
        if eval_value is None:
            white_frac = 0.5
        else:
            clamped = max(-5.0, min(5.0, eval_value))
            white_frac = (clamped + 5.0) / 10.0

        pygame.draw.rect(surf, (90, 58, 26), rect, border_radius=3)
        white_w = int(rect.width * white_frac)
        if white_w > 0:
            pygame.draw.rect(surf,
                             (240, 217, 181),
                             pygame.Rect(rect.x, rect.y, white_w, rect.height),
                             border_radius=3)

    def _draw_captured_images(self, surf: pygame.Surface, x: int, y: int,
                               color: Color, icon_size: int = 16) -> None:
        from gui.assets import get_small_sprite
        opp = Color(1 - int(color))
        cursor_x = x
        for pt in (PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT, PieceType.PAWN):
            net = _net_captured_count(self._board, color, pt)
            for _ in range(net):
                img = get_small_sprite(opp, pt, icon_size)
                surf.blit(img, (cursor_x, y))
                cursor_x += icon_size + 1

    # ------------------------------------------------------------------
    # Move history panel

    def _draw_history_panel(self) -> None:
        surf = self._surf
        font_label = get_font("serif", 10)
        font_hist = get_font("monospace", 11)
        panel_rect = pygame.Rect(HIST_X, 0, HIST_W, WINDOW_H)
        pygame.draw.rect(surf, CARD_BG, panel_rect)

        lbl = font_label.render("ZUGHISTORIE", True, TEXT_MUTED)
        surf.blit(lbl, (HIST_X + 6, 10))

        panel_top = 30
        row_h = font_hist.get_height() + 4
        available_h = WINDOW_H - panel_top - 66
        max_rows = max(1, available_h // row_h)

        # Build the full list of rows to display (completed pairs + optional half-move)
        all_rows: list[tuple[int, str, str]] = []
        for i, (white_pgn, black_pgn) in enumerate(self._move_history):
            all_rows.append((i + 1, white_pgn, black_pgn))
        if self._current_half:
            all_rows.append((len(self._move_history) + 1, self._current_half, ""))

        # Show only the last max_rows rows so the latest move is always visible
        visible = all_rows[-max_rows:]

        y = panel_top
        for idx, (move_num, white_pgn, black_pgn) in enumerate(visible):
            is_last_row = (idx == len(visible) - 1)
            num = font_hist.render(f"{move_num}.", True, TEXT_MUTED)
            surf.blit(num, (HIST_X + 4, y))
            w_color = ACCENT if (is_last_row and black_pgn == "") else TEXT_DARK
            wt = font_hist.render(white_pgn, True, w_color)
            surf.blit(wt, (HIST_X + 26, y))
            if black_pgn:
                b_color = ACCENT if is_last_row else TEXT_DARK
                bt = font_hist.render(black_pgn, True, b_color)
                surf.blit(bt, (HIST_X + 66, y))
            y += row_h

        # 50-move rule counter
        y_counter = WINDOW_H - 60
        lbl_50 = font_label.render("50-ZÜGE-REGEL", True, TEXT_MUTED)
        surf.blit(lbl_50, (HIST_X + 6, y_counter))
        remaining = 100 - self._board.halfmove_clock
        val_50 = font_hist.render(f"{remaining} Halbzüge", True, TEXT_MUTED)
        surf.blit(val_50, (HIST_X + 6, y_counter + lbl_50.get_height() + 2))

    # ------------------------------------------------------------------
    # Game over overlay

    def _draw_game_over_overlay(self) -> None:
        assert self._outcome is not None
        surf = self._surf
        dim = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        surf.blit(dim, (0, 0))

        box_w, box_h = 260, 160
        box = pygame.Rect((WINDOW_W - box_w) // 2, (WINDOW_H - box_h) // 2, box_w, box_h)
        pygame.draw.rect(surf, CARD_BG, box, border_radius=8)
        pygame.draw.rect(surf, BORDER, box, 2, border_radius=8)

        font_title = get_font("serif", 18)
        font_reason = get_font("serif", 12)
        font_btn = get_font("serif", 13)

        result = self._outcome.result
        title = ("Weiß gewinnt" if result == GameResult.WHITE_WINS else
                 "Schwarz gewinnt" if result == GameResult.BLACK_WINS else "Remis")

        from gui.assets import get_small_sprite
        y = box.y + 14
        if result == GameResult.WHITE_WINS:
            it = get_small_sprite(Color.WHITE, PieceType.KING, 32)
        elif result == GameResult.BLACK_WINS:
            it = get_small_sprite(Color.BLACK, PieceType.KING, 32)
        else:
            it = get_font("serif", 32).render("½", True, ACCENT)
        surf.blit(it, (box.centerx - it.get_width() // 2, y))
        y += it.get_height() + 4
        tt = font_title.render(title, True, TEXT_DARK)
        surf.blit(tt, (box.centerx - tt.get_width() // 2, y))
        y += tt.get_height() + 4
        rt = font_reason.render(self._outcome.reason, True, TEXT_MUTED)
        surf.blit(rt, (box.centerx - rt.get_width() // 2, y))
        y += rt.get_height() + 12

        # Buttons
        btn_w = 100
        new_rect = pygame.Rect(box.centerx - btn_w - 6, y, btn_w, 30)
        menu_rect = pygame.Rect(box.centerx + 6, y, btn_w, 30)
        pygame.draw.rect(surf, ACCENT, new_rect, border_radius=3)
        pygame.draw.rect(surf, CARD_BG, menu_rect, border_radius=3)
        pygame.draw.rect(surf, BORDER, menu_rect, 1, border_radius=3)
        nt = font_btn.render("Neues Spiel", True, (255, 255, 255))
        surf.blit(nt, (new_rect.centerx - nt.get_width() // 2,
                       new_rect.centery - nt.get_height() // 2))
        mt = font_btn.render("← Menü", True, TEXT_DARK)
        surf.blit(mt, (menu_rect.centerx - mt.get_width() // 2,
                       menu_rect.centery - mt.get_height() // 2))
        self._new_game_rect = new_rect
        self._menu_from_over_rect = menu_rect

    def _handle_game_over_event(self, event: pygame.event.Event):
        from gui.main_menu import MainMenuScreen
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, "_new_game_rect") and self._new_game_rect.collidepoint(event.pos):
                return GameScreen(self._surf, self._config)
            if (hasattr(self, "_menu_from_over_rect")
                    and self._menu_from_over_rect.collidepoint(event.pos)):
                return MainMenuScreen(self._surf)
            if hasattr(self, "_back_rect") and self._back_rect.collidepoint(event.pos):
                return MainMenuScreen(self._surf)
        return None
