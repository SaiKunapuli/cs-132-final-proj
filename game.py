import random
import time

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

TITLE = r"""
 ____              _
/ ___| _ __   __ _| | _____  ___   _ __
\___ \| '_ \ / _` | |/ / _ \/ __| | '_ \
 ___) | | | | (_| |   <  __/\__ \ | | | |
|____/|_| |_|\__,_|_|\_\___||___/ |_| |_|
 _              _     _
| |    __ _  __| | __| | ___ _ __ ___
| |   / _` |/ _` |/ _` |/ _ \ '__/ __|
| |__| (_| | (_| | (_| |  __/ |  \__ \
|_____\__,_|\__,_|\__,_|\___|_|  |___/
"""


class Player:
    COLORS = {
        "P1": "bold cyan",
        "P2": "bold bright_magenta",
        "P3": "bold bright_blue",
        "P4": "bold orange1",
    }

    def __init__(self, name, marker, is_computer=False):
        """
        Initializes a new player with a name marker and computer flag
        Args:
            name: The player name
            marker: The player marker shown on the board
            is_computer: Whether the player is controlled by the computer
        Returns:
            None
        """
        self.name = name
        self.marker = marker
        self.position = 0
        self.turns = 0
        self.is_computer = is_computer

    @property
    def style(self):
        """
        Returns the rich color style associated with the player marker
        Args:
            None
        Returns:
            The color style string for the player
        """
        return Player.COLORS[self.marker]

    def styled_name(self):
        """
        Wraps the player name in their color markup
        Args:
            None
        Returns:
            A formatted string showing the player marker and name in color
        """
        tag = "" if self.is_computer else ""
        return f"[{self.style}]{self.marker} {self.name}{tag}[/{self.style}]"


MIN_FEATURE_LENGTH = 3

DIFFICULTY_RATIOS = {
    "easy":   (18, 8),
    "medium": (12, 12),
    "hard":   (8, 18),
}


def generate_board(size, difficulty="medium"):
    """
    Randomly generates snakes and ladders for the given board size and difficulty
    Args:
        size: The total number of squares on the board
        difficulty: The chosen difficulty level affecting snake and ladder counts
    Returns:
        A dictionary mapping square numbers to feature tuples
    """
    snake_div, ladder_div = DIFFICULTY_RATIOS[difficulty]
    num_snakes  = max(2, size // snake_div)
    num_ladders = max(2, size // ladder_div)

    board = {}
    available = set(range(2, size))

    for _ in range(num_snakes):
        if len(available) < 2:
            break
        head = random.choice(list(available))
        valid_tails = [s for s in available
                       if s < head and (head - s) >= MIN_FEATURE_LENGTH]
        if not valid_tails:
            available.discard(head)
            continue
        tail = random.choice(valid_tails)
        board[head] = ("snake", tail)
        available.discard(head)
        available.discard(tail)

    for _ in range(num_ladders):
        if len(available) < 2:
            break
        bottom = random.choice(list(available))
        valid_tops = [s for s in available
                      if s > bottom and (s - bottom) >= MIN_FEATURE_LENGTH]
        if not valid_tops:
            available.discard(bottom)
            continue
        top = random.choice(valid_tops)
        board[bottom] = ("ladder", top)
        available.discard(bottom)
        available.discard(top)

    return board


COLS = 10

SYM_SNAKE   = "▼"
SYM_LADDER  = "▲"
SYM_FINISH  = "★"


def make_cell(n, size, board, players):
    """
    Builds the styled Text object for a single board square
    Args:
        n: The square number being rendered
        size: The total number of squares on the board
        board: The dictionary of snake and ladder features
        players: The list of players in the current game
    Returns:
        A styled Text object representing the cell
    """
    text = Text(justify="center")
    here = [p for p in players if p.position == n]

    if here:
        text.append(f"{n}\n", style="white")
        if len(here) > 1:
            text.append(f"x{len(here)}", style="bold yellow")
        else:
            text.append(here[0].marker, style=here[0].style)
        return text

    if n == size:
        text.append(f"{n}\n", style="bold yellow")
        text.append(SYM_FINISH, style="bold yellow")
        return text

    feat = board.get(n)
    if feat is not None:
        kind, value = feat
        if kind == "snake":
            text.append(f"{n}\n", style="red")
            text.append(f"{SYM_SNAKE}{value}", style="bold red")
        else:
            text.append(f"{n}\n", style="green")
            text.append(f"{SYM_LADDER}{value}", style="bold green")
        return text

    text.append(f"{n}\n", style="dim")
    text.append(" ", style="dim")
    return text


def draw_board(size, board, players):
    """
    Renders the entire board as a styled rich Table with status and legend
    Args:
        size: The total number of squares on the board
        board: The dictionary of snake and ladder features
        players: The list of players in the current game
    Returns:
        None
    """
    table = Table(
        show_header=False,
        show_lines=True,
        box=box.SQUARE,
        padding=(0, 1),
    )
    for _ in range(COLS):
        table.add_column(justify="center", min_width=4)

    rows = (size + COLS - 1) // COLS
    for row in range(rows - 1, -1, -1):
        cells = []
        for col in range(COLS):
            if row % 2 == 0:
                n = row * COLS + (col + 1)
            else:
                n = row * COLS + (COLS - col)
            if n > size:
                cells.append("")
            else:
                cells.append(make_cell(n, size, board, players))
        table.add_row(*cells)

    console.print(table)

    for p in players:
        console.print(
            f"  {p.styled_name()}   "
            f"square: [bold]{p.position}[/bold]   "
            f"turns: [bold]{p.turns}[/bold]"
        )

    console.print(
        f"  [dim]Legend:[/dim] "
        f"[bold green]{SYM_LADDER}[/bold green] ladder   "
        f"[bold red]{SYM_SNAKE}[/bold red] snake   "
        f"[bold yellow]{SYM_FINISH}[/bold yellow] finish ({size})   "
        f"[bold yellow]xN[/bold yellow] shared (N players)"
    )
    console.print()


def roll_die(sides):
    """
    Returns a random integer between one and the given number of sides
    Args:
        sides: The number of sides on the die
    Returns:
        A random integer from one to sides inclusive
    """
    return random.randint(1, sides)


def take_turn(player, board, size, die_sides, history):
    """
    Rolls for the player applies the result and appends a log line
    Args:
        player: The player taking the turn
        board: The dictionary of snake and ladder features
        size: The total number of squares on the board
        die_sides: The number of sides on the die
        history: The list collecting move log entries
    Returns:
        None
    """
    if player.is_computer:
        console.print(f"   [dim]{player.styled_name()} is rolling...[/dim]")
        time.sleep(0.6)
    else:
        console.input(f"   {player.styled_name()}, press [bold]Enter[/bold] to roll the die...")

    roll = roll_die(die_sides)
    player.turns += 1
    target = player.position + roll
    msg = (f"Turn [bold]{player.turns:>3}[/bold] | {player.styled_name()} "
           f"rolled [bold]{roll}[/bold]")

    if target > size:
        msg += (f" -- needs exactly {size}, "
                f"[yellow]stays at {player.position}[/yellow].")
    elif target == size:
        player.position = size
        msg += f" -- lands on {size} and [bold yellow]WINS![/bold yellow]"
    else:
        feat = board.get(target)
        if feat is None:
            player.position = target
            msg += f" -- moves to [bold]{target}[/bold]."
        else:
            kind, value = feat
            if kind == "snake":
                player.position = value
                msg += (f" -- lands on {target}, "
                        f"[bold red]snake {SYM_SNAKE} slides down to {value}[/bold red].")
            else:
                player.position = value
                msg += (f" -- lands on {target}, "
                        f"[bold green]ladder {SYM_LADDER} climbs up to {value}[/bold green].")

    history.append(msg)
    console.print("   " + msg)


def play_round(players, board, size, die_sides):
    """
    Runs one full game of snakes and ladders until a player wins
    Args:
        players: The list of players in the game
        board: The dictionary of snake and ladder features
        size: The total number of squares on the board
        die_sides: The number of sides on the die
    Returns:
        A tuple containing the winning player and the move history
    """
    history = []
    turn_idx = 0
    draw_board(size, board, players)

    while True:
        current = players[turn_idx % len(players)]
        bar = f"[{current.style}]" + ("=" * 60) + f"[/{current.style}]"
        console.print(bar)
        console.print(
            f"  {current.styled_name()}'s turn  --  "
            f"square [bold]{current.position}[/bold], "
            f"turns taken [bold]{current.turns}[/bold]"
        )
        console.print(bar)

        take_turn(current, board, size, die_sides, history)
        draw_board(size, board, players)

        if current.position == size:
            return current, history

        turn_idx += 1


def ask_int(prompt, low, high, default=None):
    """
    Prompts the user repeatedly until they enter an integer in the given range
    Args:
        prompt: The text shown to the user
        low: The smallest acceptable integer
        high: The largest acceptable integer
        default: The value returned when the user enters nothing
    Returns:
        The integer chosen by the user
    """
    while True:
        raw = console.input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            console.print(f"   [red]Please enter a whole number "
                          f"between {low} and {high}.[/red]")
            continue
        if not (low <= value <= high):
            console.print(f"   [red]Out of range. "
                          f"Please pick a value in [{low}, {high}].[/red]")
            continue
        return value


def ask_choice(prompt, options):
    """
    Shows a numbered menu and returns the chosen index
    Args:
        prompt: The text shown above the menu
        options: The list of choices presented to the user
    Returns:
        The zero based index of the chosen option
    """
    console.print(prompt)
    for i, opt in enumerate(options, start=1):
        console.print(f"   [bold cyan]{i}[/bold cyan]) {opt}")
    return ask_int("Your choice: ", 1, len(options)) - 1


def ask_yes_no(prompt, default=True):
    """
    Asks a yes or no question and returns the boolean answer
    Args:
        prompt: The text shown to the user
        default: The value returned when the user enters nothing
    Returns:
        True when the user answers yes and False when they answer no
    """
    suffix = " [Y/n] " if default else " [y/N] "
    while True:
        ans = console.input(prompt + suffix).strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        console.print("   [red]Please answer 'y' or 'n'.[/red]")


def setup_game():
    """
    Walks the user through choosing players difficulty board size and die
    Args:
        None
    Returns:
        A tuple of players size die_sides and difficulty
    """
    console.rule("[bold green]Game Setup[/bold green]")

    num_players = ask_choice("Number of players:",
                             ["2 players", "3 players", "4 players"]) + 2

    players = []
    markers = ("P1", "P2", "P3", "P4")
    cpu_count = 0
    for i in range(num_players):
        prompt = (f"Player {i + 1} name "
                  f"[dim](leave blank for CPU)[/dim]: ")
        name = console.input(prompt).strip()
        if name == "":
            cpu_count += 1
            cpu_name = "CPU" if cpu_count == 1 and num_players == 2 else f"CPU {cpu_count}"
            players.append(Player(cpu_name, markers[i], is_computer=True))
        else:
            players.append(Player(name, markers[i], is_computer=False))

    diff_idx = ask_choice("Choose difficulty:",
                          ["Easy   (more ladders, fewer snakes)",
                           "Medium (balanced)",
                           "Hard   (more snakes, fewer ladders)"])
    difficulty = ("easy", "medium", "hard")[diff_idx]

    size_idx = ask_choice("Choose board size:",
                          ["50 squares",
                           "100 squares (classic)"])
    size = 50 if size_idx == 0 else 100

    die_idx = ask_choice("Choose your die:",
                         ["6-sided  (classic)",
                          "12-sided",
                          "20-sided"])
    die_sides = (6, 12, 20)[die_idx]

    return players, size, die_sides, difficulty


def show_history(history):
    """
    Prints every move recorded during the game
    Args:
        history: The list of move log entries
    Returns:
        None
    """
    console.rule("[bold]Move History[/bold]")
    for line in history:
        console.print("  " + line)
    console.print()


def show_high_scores(scoreboard):
    """
    Prints the top five fastest wins recorded so far this session
    Args:
        scoreboard: The list of recorded win entries
    Returns:
        None
    """
    if not scoreboard:
        return
    table = Table(
        title="[bold yellow]Fastest Wins This Session[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("#", justify="right")
    table.add_column("Winner")
    table.add_column("Turns", justify="right")
    table.add_column("Board", justify="right")
    table.add_column("Die", justify="right")
    table.add_column("Diff", justify="right")

    ranked = sorted(scoreboard, key=lambda e: e["turns"])[:5]
    for i, entry in enumerate(ranked, start=1):
        table.add_row(
            str(i),
            entry["name"],
            str(entry["turns"]),
            f"{entry['size']} sq",
            f"d{entry['die']}",
            entry["diff"].capitalize(),
        )
    console.print(table)


def show_title():
    """
    Prints the welcome banner inside a rich Panel
    Args:
        None
    Returns:
        None
    """
    panel = Panel(
        Text(TITLE.strip("\n"), style="bold green", justify="center"),
        title="[bold yellow]CMPSC 132 Project[/bold yellow]",
        subtitle="[dim]press Ctrl+C to quit anytime[/dim]",
        border_style="cyan",
        padding=(1, 4),
    )
    console.print(panel)


def main():
    """
    Runs the main game loop allowing repeated games until the user quits
    Args:
        None
    Returns:
        None
    """
    show_title()

    scoreboard = []

    while True:
        players, size, die_sides, difficulty = setup_game()

        for p in players:
            p.position = 0
            p.turns = 0

        board = generate_board(size, difficulty)
        winner, history = play_round(players, board, size, die_sides)

        console.rule(
            f"[bold yellow]{winner.name} wins in {winner.turns} turns![/bold yellow]"
        )

        scoreboard.append({
            "name":   winner.name,
            "turns":  winner.turns,
            "size":   size,
            "die":    die_sides,
            "diff":   difficulty,
        })

        show_high_scores(scoreboard)

        if ask_yes_no("View move history?", default=False):
            show_history(history)

        if not ask_yes_no("Play another game?", default=True):
            console.print("\n[bold green]Thanks for playing![/bold green]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[dim]Game interrupted. Goodbye![/dim]")
