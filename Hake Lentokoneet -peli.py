"""
Tekijä: Shuang Fan
Sähköposti: fanshuang99@gmail.com
Projekti GUI - Aircraft Head Hunting Game

This is a project to play a game, which name is "Aircraft Head Hunting".
There is two players: player 1 and player 2. The players need to play one by
one. The player, who has found all of the aircraft heads faster than the
other, can win the game. If the two players have found all of the heads in
same rounds. Then the game is a draw.

In the GUI-surface, the players can choose the level of the game difficalty
from easy to hard. The default level is "EASY" and the player can also
change to "MEDIUM" or "HARD" modes. If the player has any question about the
game, there is an inside HELP button which can show the game instruction in
another pop-up window.

The program wouldn't quit automatically. If there is any error during the
game is running, the programme will restart automatically or give a warning and
make a choice to restart the game.
"""

from multiprocessing import Process, Queue
import random

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import *
from tkinter.font import *
from functools import partial

# Here is global constants.
SIZE_EASY = 8
SIZE_MEDIUM = 10
SIZE_HARD = 12
ROW = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split()
PLANEHEAD = " X"
PLANEBODY = " *"
BLANKSPACE = "  "
RED = "#EC1C24"
BLUE = "#00A8F3"
WHITE = "#FFFFFF"
GRAY = "#C3C3C3"


#===== class Aircraft =========================================================
# This class is used to record the information of an aircraft. Including the
# head's coordinates and the body's coordinates. X-coordinate's name is
# str-type and Y-coordinate's name is int-type.
class Aircraft:
    """
    Defines an aircraft.
    """
    def __init__(self, coordinates):
        """
        Initializes the aircraft's.
        :param coordinates: list, the coordinates of a plane, the first
                            element should be the plane's head.
        """
        self.__coordinates = {}
        self.__set_initial_coordinates(coordinates)

    def __set_initial_coordinates(self, coordinates):
        """
        Initializes the aircraft's coordinates in a dict in dict.
        * This is an private method.
        :param coordinates: list, the coordinates of a plane, the first
                            element should be the plane's head.
        """
        head = coordinates[0]
        body = coordinates[1:]

        # Sets planehead.
        try:
            x = head[0].upper()
            y = int(head[1:])
            self.__coordinates.update({x:{y:PLANEHEAD}})
        except:
            return

        # Sets planebody.
        for element in body:
            try:
                x = element[0].upper()
                y = int(element[1:])
                if x in self.__coordinates.keys():
                    self.__coordinates[x].update({y:PLANEBODY})
                else:
                    self.__coordinates.update({x:{y:PLANEBODY}})
            except:
                return

    def get_coordinates(self):
        """
        Gets the plane's coordinates.
        :return: dict in dict, the plane's coordinates used in class.
        """
        return self.__coordinates


#===== class Gameboard ========================================================
# This class is used to set the gameboard with the given size. The default
# gameboard is without any aircraft. Needs to add the valid aircraft into the
# board. The amount of aircrafts in the gameboard depends on the level of the
# game.
#
# Level-Easy: 8 x 8, with 2 aircrafts.
# Level-Medium: 10 x 10, with 3 aircrafts.
# Level-Hard: 12 x 12, with 4 aircrafts.
class Gameboard:
    """
    This is a gameboard with the given size.
    """
    def __init__(self, boardsize):
        """
        Sets a gameboard.
        :param boardsize: int, the size of gameboard
        """
        self.__size = boardsize
        self.__board = {}
        self.__initial_board()

    def __initial_board(self):
        """
        Initialize the gameboard.
        * This is an private method.
        """
        for x in ROW[0 : self.__size]:
            for y in range(self.__size):
                if x in self.__board.keys():
                    self.__board[x].update({y:BLANKSPACE})
                else:
                    self.__board.update({x:{y:BLANKSPACE}})

    def add_aircraft(self, plane_coordinates):
        """
        Adds an new aircraft to this board.
        :param plane_coordinates: dict in dict, the plane's coordinates.
        :return: bool, True: if it is successfully added;
                       False: if it cannot be added.
        """
        if not self.__overlapping(plane_coordinates):
            for x in plane_coordinates.keys():
                for y in plane_coordinates[x].keys():
                    self.__board[x][y] = plane_coordinates[x][y]
            return True
        else:
            return

    def __overlapping(self, plane_coordinates):
        """
        Checks the new aircraft is overlapping.
        * This is an private method.
        :param plane_coordinates: dict in dict, the new plane's coordinates.
        :return: bool, True: if it is overlapping;
                       False: if it isn't overlapping.
        """
        for x in plane_coordinates.keys():
            for y in plane_coordinates[x].keys():
                if self.__board[x][y] != BLANKSPACE:
                    return True
        return False

    def get_board(self):
        """
        Gets the gameboard information.
        :return: dict in dict, the information of the gameboard.
        """
        return self.__board

    def print(self):
        """
        * Prints the gameboard on screen. Just used to print the answer on
        Python screen for debugging.
        """
        print("-"*(self.__size+2)*2)
        for Y in range(self.__size):
            print("|", end="")
            for X in ROW[0:self.__size]:
                print(self.__board[X][Y], end="")
            print(" |")
        print("-"*(self.__size+2)*2)


#===== Called by class Random_aircraft_SIMPLE and Random_aircraft_COMPLEX======
def is_valid_Aircraft(coordinates, boardsize):
    """
    Checks the aircraft has the valid coordinates on gameboard.
    :param coordinates: dict in dict, the plane's coordinates.
    :param boardsize: int, the size of whole gameboard.
    :return: bool, True: if the plane is valid;
                   False: if the plane is invalid.
    """
    for element in coordinates:
        x = element[0]
        y = int(element[1:])
        if (x > ROW[boardsize-1]) or (y > (boardsize - 1) or (y < 0)):
            return False
    return True

#===== class Random_aircraft_SIMPLE ===========================================
# This class is used to create a new random aircraft in simple model.
class Random_aircraft_SIMPLE:
    """
    Creates a random SIMPLE aircraft.
    :param self.__plane: Aircraft, a simple aircraft.
    :param self.__size: int, the size of given gameboard.
    :param self.__x_head: str, the planehead's x-coordinate on board.
    :param self.__y_head: int, the planehead's y-coordinate on board.
    """
    def __init__(self, boardsize):
        """
        Initializes the class.
        :param boardsize: int, the size of gameboard.
        """
        self.__plane = None
        self.__size = boardsize
        self.__x_head = None
        self.__y_head = None
        self.__create()

    def __create(self):
        """
        Sets a random aircraft like this model:
            "W"-direction:   "E"-direction:   "N"-direction:   "S"-direction:
                   *                  *             X               * * *
                   *   *          *   *         * * * * *             *
                 X * * *          * * * X           *             * * * * *
                   *   *          *   *           * * *               X
                   *                  *
        * This is a private method.
        """
        Directions = ["W", "E", "N", "S"]

        while self.__plane == None:
            self.__x_head = random.choice( ROW[0 : self.__size - 1] )
            self.__y_head = random.randint(0, self.__size - 1)
            direction = random.choice(Directions)

            if direction == "W":
                self.__simple_W_direction()
            elif direction == "E":
                self.__simple_E_direction()
            elif direction == "N":
                self.__simple_N_direction()
            else: # direction == "S"
                self.__simple_S_direction()


    def __simple_W_direction(self):
        """
        Sets a aircraft, which head forwards to west.
                   *
                   *   *
                 X * * *
                   *   *
                   *
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.__x_head)
            for diff in [-2, -1, 0, 1, 2]:
                coordinates.append( ROW[index + 1] + str(self.__y_head + diff))
            coordinates.append( ROW[index + 2] + str(self.__y_head))
            for diff in [-1, 0, 1]:
                coordinates.append( ROW[index + 3] + str(self.__y_head + diff))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def __simple_E_direction(self):
        """
        Sets a aircraft, which head forwards to east.
                    *
                *   *
                * * * X
                *   *
                    *
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.self.__x_head)
            for diff in [-2, -1, 0, 1, 2]:
                coordinates.append(ROW[index - 1] + str(self.__y_head + diff))
            coordinates.append(ROW[index - 2] + str(self.__y_head))
            for diff in [-1, 0, 1]:
                coordinates.append(ROW[index - 3] + str(self.__y_head + diff))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def __simple_N_direction(self):
        """
        Sets a aircraft, which head forwards to north.
                  X
              * * * * *
                  *
                * * *
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.__x_head)
            for diff in [-2, -1, 0, 1, 2]:
                coordinates.append( ROW[index + diff] + str(self.__y_head + 1))
            coordinates.append( ROW[index] + str(self.__y_head + 2))
            for diff in [-1, 0, 1]:
                coordinates.append( ROW[index + diff] + str(self.__y_head + 3))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def __simple_S_direction(self):
        """
        Sets a aircraft, which head forwards to south.
                 * * *
                   *
               * * * * *
                   X
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.__x_head)
            for diff in [-2, -1, 0, 1, 2]:
                coordinates.append( ROW[index + diff] + str(self.__y_head - 1))
            coordinates.append( ROW[index] + str(self.__y_head - 2))
            for diff in [-1, 0, 1]:
                coordinates.append( ROW[index + diff] + str(self.__y_head - 3))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def get_aircraft(self):
        """
        Gets the plane's informations.
        :return: Aircraft, the information of the plane.
        """
        return self.__plane

#===== class Random_aircraft_COMPLEX ==========================================
# This class is used to create a new random aircraft in complex model.
class Random_aircraft_COMPLEX:
    """
    Creates a random COMPLEX aircraft.
    :param self.__plane: Aircraft, a complex aircraft.
    :param self.__size: int, the size of given gameboard.
    :param self.__x_head: str, the planehead's x-coordinate on board.
    :param self.__y_head: int, the planehead's y-coordinate on board.
    """
    def __init__(self, boardsize):
        """
        Initializes the class.
        :param boardsize: int, the size of gameboard.
        """
        self.__plane = None
        self.__size = boardsize
        self.__x_head = None
        self.__y_head = None
        self.__create()

    def __create(self):
        """
        Sets a random aircraft like this model:
            "W"-direction:   "E"-direction:   "N"-direction:   "S"-direction:
                  *                 *               X              * * *
                *     *         *     *           * * *              *
              X * * * *         * * * * X       *   *   *        *   *   *
                *     *         *     *             *              * * *
                  *                 *             * * *              X
        * This is a private method.
        """
        Directions = ["W", "E", "N", "S"]
        while self.__plane == None:
            self.__x_head = random.choice(ROW[0: self.__size - 1])
            self.__y_head = random.randint(0, self.__size - 1)
            direction = random.choice(Directions)

            if direction == "W":
                self.__complex_W_direction()
            elif direction == "E":
                self.__complex_E_direction()
            elif direction == "N":
                self.__complex_N_direction()
            else:  # direction == "S"
                self.__complex_S_direction()

    def __complex_W_direction(self):
        """
        Sets a aircraft, which head forwards to west.
                     *
                   *     *
                 X * * * *
                   *     *
                     *
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.__x_head)
            for diff in [-1, 0, 1]:
                coordinates.append(ROW[index + 1] + str(self.__y_headead+diff))
                coordinates.append(ROW[index + 4] + str(self.__y_head + diff))
            for diff in [-2, 0, 2]:
                coordinates.append(ROW[index + 2] + str(self.__y_head + diff))
            coordinates.append(ROW[index + 3] + str(self.__y_head))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def __complex_E_direction(self):
        """
        Sets a aircraft, which head forwards to east.
                    *
                *     *
                * * * * X
                *     *
                    *
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.__x_head)
            for diff in [-1, 0, 1]:
                coordinates.append(ROW[index - 1] + str(self.__y_head + diff))
                coordinates.append(ROW[index - 4] + str(self.__y_head + diff))
            for diff in [-2, 0, 2]:
                coordinates.append(ROW[index - 2] + str(self.__y_head + diff))
            coordinates.append(ROW[index - 3] + str(self.__y_head))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def __complex_N_direction(self):
        """
        Sets a aircraft, which head forwards to north.
                  X
                * * *
              *   *   *
                  *
                * * *
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.__x_head)
            for diff in [-1, 0, 1]:
                coordinates.append(ROW[index + diff] + str(self.__y_head + 1))
                coordinates.append(ROW[index + diff] + str(self.__y_head + 4))
            for diff in [-2, 0, 2]:
                coordinates.append(ROW[index + diff] + str(self.__y_head + 2))
            coordinates.append(ROW[index] + str(self.__y_head + 3))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def __complex_S_direction(self):
        """
        Sets a aircraft, which head forwards to south.
                 * * *
                   *
               *   *   *
                 * * *
                   X
        * This is a private method.
        """
        coordinates = [self.__x_head + str(self.__y_head)]
        try:
            index = ROW.index(self.__x_head)
            for diff in [-1, 0, 1]:
                coordinates.append(ROW[index + diff] + str(self.__y_head - 1))
                coordinates.append(ROW[index + diff] + str(self.__y_head - 4))
            for diff in [-2, 0, 2]:
                coordinates.append(ROW[index + diff] + str(self.__y_head - 2))
            coordinates.append(ROW[index] + str(self.__y_head - 3))
        except:
            self.__plane = None
            return

        # Checkes all coordinates is valid on the given gameboard.
        if is_valid_Aircraft(coordinates, self.__size):
            self.__plane = Aircraft(coordinates)
        else:
            self.__plane = None

    def get_aircraft(self):
        """
        Gets the plane's informations.
        :return: Aircraft, the information of the plane.
        """
        return self.__plane


#===== class Find_Aircraft_Head_Game ==========================================
# This class is used to design the main game window. When the class is
# running, the players can create/start a new game, choose the game level,
# read the help file, play the game one by one and find the author information
# about the game. The game window shows the game status during the game.
class Find_Aircraft_Head_Game:
    """
    GUI-surface defination.
    """
    def __init__(self, level):
        """
        Initializes the whole window.
        :param level: str, the level of the game. The level should be "EASY",
                      "MEDIUM" or "HARD".
        """
        self.__level = level

        # Creates a new main window.
        self.__mainwindow = Tk()

        # Sets the position of the main window.
        x = self.__mainwindow.winfo_screenwidth() // 3
        y = self.__mainwindow.winfo_screenheight() // 3
        self.__mainwindow.geometry("+{}+{}".format(x, y))

        # Sets the window's title and icon.
        self.__mainwindow.title("Aircraft Head Hunting Game")
        self.__mainwindow.iconbitmap("icon.ico")

        # Creates the main menu.
        self.__create_menu()

        # Creates the gameboard in main window.
        try:
            self.__create_board()
        except:
            showerror(title = "Error",
                      message = "Please, take a new game again!")

    def __create_menu(self):
        """
        Creates the main menu bar. In this bar, there is 'File', 'Level
        Choice' and 'Help' menu. Inside 'File' menu, the user can create a
        new game or leave this game. Inside 'Level Choice' menu, the user
        can choose the game level. Inside 'Help' menu, the user can choose to
        read help information in a new window at '? Help' command and find the
        author's information at 'About...' command.
        * This is a private method.
        """
        # ====== Menu Bar =================================
        self.__menu = Menu(self.__mainwindow)
        self.__mainwindow.config(menu=self.__menu)
        # ------ Start / Stop Menu --------------------
        filemenu = Menu(self.__menu, tearoff=False)
        self.__menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New Game", command=self.__new_game)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.quit)

        # ------ Level Choice Menu --------------------
        self.__levelVar = StringVar()
        levelmenu = Menu(self.__menu, tearoff=False)
        self.__menu.add_cascade(label="Level Choice", menu=levelmenu)
        levelmenu.add_radiobutton(label='EASY', variable=self.__levelVar,
                                  command=self.level_choice, value="EASY")
        levelmenu.add_radiobutton(label='MEDIUM', variable=self.__levelVar,
                                  command=self.level_choice, value="MEDIUM")
        levelmenu.add_radiobutton(label='HARD', variable=self.__levelVar,
                                  command=self.level_choice, value="HARD")

        # ------ Help Menu -----------------------------
        helpmenu = Menu(self.__menu, tearoff=False)
        self.__menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="? Help", command=self.__open_Help_Window)
        helpmenu.add_separator()
        helpmenu.add_command(label="About...", command=self.author_info)

    def __create_board(self):
        """
        Sets an initial gameboard. Depends on the game level, the gameboard
        size is different. The gameboard layout is designed by frame. There
        is one main frame, two gameboard frames, one game model frame and one
        info Frame.

        This method is the most important one in this class. All of the
        intial gameboard information is added by this method, including the
        aircrafts information and the tip about aircraft model.

        Level EASY: gameboard 8x8, 2 random aircrafts for each player.
        Level MEDIUM: gameboard 10x10, 3 random aircrafts for each player.
        Level HARD: gameboard 12x12, 4 random aircrafts for each player.
        * This is a private method.
        """
        # Takes 2 random boards. If the board's creating process has any
        # problem (the return value is None), trys to get the board again.
        board_1 = game_main(self.__level)
        while board_1 == None:
            board_1 = game_main(self.__level)
        board_2 = game_main(self.__level)
        while board_2 == None:
            board_2 = game_main(self.__level)
        self.__boards = [board_1, board_2]

        # -- If needs to check the answer, can use the next print commands. --
        # All of the printing in on Python run screen.
        # print("Player 1's solution is:")
        # board_1.print()
        # print("Player 2's solution is:")
        # board_2.print()
        # print("-*-" * 15)
        # print()

        # Sets the boardsize and the amount of aircrafts by level.
        if self.__level == "EASY":
            self.__size = 8
            self.__finding_head = [2, 2]
        elif self.__level == "MEDIUM":
            self.__size = 10
            self.__finding_head = [3, 3]
        elif self.__level == "HARD":
            self.__size = 12
            self.__finding_head = [4, 4]

        # ====== Display Window =============================
        # The pictures, which are used in the main window.
        self.__easy_plane = PhotoImage(file="easy_plane.png")
        self.__hard_plane = PhotoImage(file="hard_plane.png")
        self.__emoji_draw = PhotoImage(file="00.gif")
        self.__emoji_bad1 = PhotoImage(file="B1.gif")
        self.__emoji_bad2 = PhotoImage(file="B2.gif")
        self.__emoji_lose = PhotoImage(file="B3.gif")
        self.__emoji_good1 = PhotoImage(file="G1.gif")
        self.__emoji_good2 = PhotoImage(file="G2.gif")
        self.__emoji_win = PhotoImage(file="G3.gif")

        # ------- Main frame design --------
        self.__mainFrame = Frame(self.__mainwindow)
        self.__startButton = Button(self.__mainFrame, text="Start Game",
                                    command=self.__startgame, state=NORMAL,
                                    font=Font(size=16), bg="#C4FF0E")
        self.__mainLabel = Label(self.__mainFrame, font=Font(size=12))

        player_1_label = Label(self.__mainFrame, text="Player 1",
                               font=("Calibri", 15, "bold"))
        player_2_label = Label(self.__mainFrame, text="Player 2",
                               font=("Calibri", 15, "bold"))

        self.__players_turn = [Label(self.__mainFrame, fg="#88001B",
                                     font=Font(size=13, weight="bold")),
                               Label(self.__mainFrame, fg="#88001B",
                                     font=Font(size=13, weight="bold"))]
        self.__players_state = [Label(self.__mainFrame, font=("times", 12)),
                                Label(self.__mainFrame, font=("times", 12))]

        self.__players_emoji = [Label(self.__mainFrame,
                                      image=self.__emoji_draw),
                                Label(self.__mainFrame,
                                      image=self.__emoji_draw)]

        # ------- Gameboard frames design --------
        self.__gameboardFrames = [Frame(self.__mainFrame),
                                  Frame(self.__mainFrame)]
        self.__gamemodelFrame = Frame(self.__mainFrame)
        gamemodelLabel = Label(self.__gamemodelFrame, text="Aircraft Model:",
                               font=("Calibri", 13, "bold"))
        if self.__level == "HARD":
            gamemodel_picLabel = Label(self.__gamemodelFrame,
                                       image=self.__hard_plane)
        else:
            gamemodel_picLabel = Label(self.__gamemodelFrame,
                                       image=self.__easy_plane)

        # Sets the gameboard squares by buttons. All buttons can return the
        # coordinates to the method.
        boardButtons_1 = {}
        for x in range(self.__size):
            for y in range(self.__size):
                if x not in boardButtons_1.keys():
                    boardButtons_1.update \
                        ({x: {y: Button(self.__gameboardFrames[0],
                                        bg = GRAY, width=3, height=1,
                                        command=partial(self.__boardButton,x,y),
                                        state=DISABLED)}})
                else:
                    boardButtons_1[x].update \
                        ({y: Button(self.__gameboardFrames[0],
                                    bg = GRAY, width=3, height=1,
                                    command=partial(self.__boardButton, x, y),
                                    state=DISABLED)})

        boardButtons_2 = {}
        for x in range(self.__size):
            for y in range(self.__size):
                if x not in boardButtons_2.keys():
                    boardButtons_2.update \
                        ({x: {y: Button(self.__gameboardFrames[1],
                                        bg=GRAY, width=3, height=1,
                                        command=partial(self.__boardButton,x,y),
                                        state=DISABLED)}})
                else:
                    boardButtons_2[x].update \
                        ({y: Button(self.__gameboardFrames[1],
                                    bg=GRAY, width=3, height=1,
                                    command=partial(self.__boardButton, x, y),
                                    state=DISABLED)})
        self.__boardButtons = [boardButtons_1, boardButtons_2]

        # Sets extra blank columns around the main gameboard.
        x = self.__size
        for y in range(self.__size):
            Label(self.__gameboardFrames[0], text="      ").grid(row=y + 1,
                                                               column=0)
            Label(self.__gameboardFrames[1], text="      ").grid(row=y + 1,
                                                               column=0)

            Label(self.__gameboardFrames[0], text="      ").grid(row=y + 1,
                                                             column=x + 1)
            Label(self.__gameboardFrames[1], text="      ").grid(row=y + 1,
                                                             column=x + 1)

        # ------- Information display frame design --------
        self.__infoFrame = Frame(self.__mainwindow)
        Label(self.__infoFrame).pack()
        levelDisplayLabel = Label(self.__infoFrame,
                                  text=f"Level: {self.__level}",
                                  font=("Arial", 15),
                                  fg = "#0400FC", bg = "#D5F2FA")
        welcomeLabel = Label(self.__infoFrame,
                                   text = "Welcome to play! Enjoy your game!",
                                   font=("Calibri", 12, "italic"),
                                   fg = "#85021C", bg = "#FAD5DC")

        # All widgets(labels/buttons/frames)' placement.
        self.__mainFrame.pack()
        self.__startButton.grid(row = 0, column = 0, columnspan=7)
        self.__mainLabel.grid(row = 1, column = 0, columnspan=7)
        self.__players_emoji[0].grid(row=2, column=0, rowspan=2)
        self.__players_emoji[1].grid(row=2, column=6, rowspan=2)
        player_1_label.grid(row=2, column=2, sticky=E)
        player_2_label.grid(row=2, column=4, sticky=W)
        self.__players_turn[0].grid(row=3, column=1, columnspan=2)
        self.__players_turn[1].grid(row=3, column=4, columnspan=2)
        self.__players_state[0].grid(row=4, column=0, columnspan=3, sticky=E+W)
        self.__players_state[1].grid(row=4, column=4, columnspan=3, sticky=E+W)
        self.__gameboardFrames[0].grid(row=5, column=0, columnspan=3)
        self.__gameboardFrames[1].grid(row=5, column=4, columnspan=3)
        self.__gamemodelFrame.grid(row=5, column=3, sticky=N)
        gamemodelLabel.grid()
        gamemodel_picLabel.grid()

        for x in range(self.__size):
            for y in range(self.__size):
                self.__boardButtons[0][x][y].grid(row=y + 1, column=x + 1)
                self.__boardButtons[1][x][y].grid(row=y + 1, column=x + 1)

        self.__infoFrame.pack(side=BOTTOM)
        levelDisplayLabel.pack()
        welcomeLabel.pack()

    def __update_board(self):
        """
        When the user opens a new game, the whole gameboard need to update.
        * This is a private method.
        """
        self.__gameboardFrames[0].destroy()
        self.__gameboardFrames[1].destroy()
        self.__gamemodelFrame.destroy()
        self.__mainFrame.destroy()
        self.__infoFrame.destroy()

        try:
            self.__create_board()
        except:
            showerror(title="Error",
                      message="Please, take a new game again!")

    def __new_game(self):
        """
        Creates a new game. Needs to confirm before starting a new game.
        * This is a private method.
        """
        check = messagebox.askokcancel("Confirm",
                   "Are you sure to start a new {} game?".format(self.__level))
        if check == True:
            self.__update_board()
        self.__startButton.configure(state=NORMAL)

    def __startgame(self):
        """
        Starts the game. Makes all of the gameboard buttons into NORMAL state.
        * This is a private method.
        """
        # Resets the round counter into 0.
        self.__round = 0

        # Resets all gameboard buttons into NORMAL state
        for x in range(self.__size):
            for y in range(self.__size):
                self.__boardButtons[0][x][y].configure(state=NORMAL)

        # Shows the game information on the label.
        self.__players_turn[0].configure(text="Your turn!")
        self.__players_state[0].configure(
            text=f"You have {self.__finding_head[0]} heads to find!")
        self.__players_state[1].configure(
            text=f"You have {self.__finding_head[1]} heads to find!")
        self.__mainLabel.configure(text="Round: 0")

        # Sets the start button into DISABLED state after the game already
        # started.
        self.__startButton.configure(state=DISABLED)

    def __boardButton(self, x, y):
        """
        This is the gameboard buttons' event. The button can change the state
        into DISABLED or NORMAL and then change the color to while/red/blue.
        * This is a private method.
        :param x: int, x-coordinate of the given button.
        :param y: int, y-coordinate of the given button.
        """
        # Makes sure which player is playing now.
        player_turn = self.__round % 2

        # Changes the player's gameboard button's outfit.
        board = self.__boards[player_turn].get_board()
        if board[ROW[x]][y] == BLANKSPACE:
            self.__boardButtons[player_turn][x][y].configure(bg=WHITE)
        elif board[ROW[x]][y] == PLANEHEAD:
            self.__boardButtons[player_turn][x][y].configure(bg=RED)
            self.__finding_head[player_turn] -= 1
            self.__players_state[player_turn].configure(
                text=f"You have {self.__finding_head[player_turn]} "
                     f"heads to find!"
            )
            self.__change_emoji()
        elif board[ROW[x]][y] == PLANEBODY:
            self.__boardButtons[player_turn][x][y].configure(bg=BLUE)

        # If the game is over, all of the bottons need to be locked.
        if player_turn == 1 and self.__is_winner():
            self.__disabled_all_buttons()
            return

        # Updates the round's showing.
        round_show = self.__round // 2 + 1
        self.__mainLabel.configure(text = f"Round: {round_show}")

        # When the game isn't over, changes the buttons' state. Makes sure
        # the player can play the game one by one. Continues to count the
        # round number.
        self.__disabled_buttons()
        self.__round += 1

    def __change_emoji(self):
        """
        Changes the emoji depends on the result of the game to take the game
        has more funny.
        * This is a private method.
        """
        player_turn = self.__round % 2
        player_next_turn = (self.__round + 1) % 2

        # Calculates the difference amount of each player's finded aircraft
        # heads. Changes the emoji depending on the error.
        diff = abs(self.__finding_head[0] - self.__finding_head[1])
        if diff == 0:
            self.__players_emoji[0].configure(image=self.__emoji_draw)
            self.__players_emoji[1].configure(image=self.__emoji_draw)
        elif diff == 1:
            self.__players_emoji[player_turn].configure(
                image=self.__emoji_good1)
            self.__players_emoji[player_next_turn].configure(
                image=self.__emoji_bad1)
        else:
            self.__players_emoji[player_turn].configure(
                image=self.__emoji_good2)
            self.__players_emoji[player_next_turn].configure(
                image=self.__emoji_bad2)

    def __disabled_all_buttons(self):
        """
        Locks all the gameboard buttons.
        * This is a private method.
        """
        for x in range(self.__size):
            for y in range(self.__size):
                self.__boardButtons[0][x][y].configure(state=DISABLED)
                self.__boardButtons[1][x][y].configure(state=DISABLED)

    def __disabled_buttons(self):
        """
        Changes the players' gameboard buttons state. If the buttons haven't
        been chose, changes the state from NORMAL to DISABLED or from DISABLED
        to NORMAL. Changes the text of turn-label at the same time.
        * This is a private method.
        """
        player_turn = self.__round % 2
        player_next_turn = (self.__round + 1) % 2
        for x in range(self.__size):
            for y in range(self.__size):
                self.__boardButtons[player_turn][x][y].configure(
                    state=DISABLED)
                state = str(self.__boardButtons[player_next_turn][x][y]["bg"])
                # Changes just gray squares into NORMAL.
                if state == GRAY:
                    self.__boardButtons[player_next_turn][x][y].configure(
                        state=NORMAL)
        self.__players_turn[player_turn].configure(text="")
        self.__players_turn[player_next_turn].configure(text="Your turn!")

    def __is_winner(self):
        """
        The game will be over, when the players are drawing or one of them
        won the game. This method is used to check the game is over or not.
        When the game is over, makes the showinfo-message at the same time.
        * This is a private method.
        :return: bool, True: when the game is over;
                       False: when the game is still playing.
        """
        # When all of the players have found all heads, it is draw.
        if self.__finding_head[0] == 0 and self.__finding_head[1] == 0:
            self.__players_emoji[0].configure(image = self.__emoji_draw)
            self.__players_emoji[1].configure(image = self.__emoji_draw)
            showinfo(title = "GAME IS OVER",
                     message= "Congratulations!\n\nThe game is a draw!")
            return True
        # When only player 1 has found all heads, player 1 is the winner.
        elif self.__finding_head[0] == 0:
            self.__players_emoji[0].configure(image = self.__emoji_win)
            self.__players_emoji[1].configure(image = self.__emoji_lose)
            showinfo(title = "GAME IS OVER",
                     message = "Congratulations!\n\nPlayer 1 won the game!!!")
            return True
        # When only player 2 has found all heads, player 2 is the winner.
        elif self.__finding_head[1] == 0:
            self.__players_emoji[1].configure(image = self.__emoji_win)
            self.__players_emoji[0].configure(image = self.__emoji_lose)
            showinfo(title = "GAME IS OVER",
                     message = "Congratulations!\n\nPlayer 2 won the game!!!")
            return True

        return False

    def level_choice(self):
        """
        This method is used to record the level of the game.
        """
        self.__level = self.__levelVar.get()

    def author_info(self):
        """
        Sets the messagebox's title and text. Shows the author information.
        """
        showinfo(title = "Author Information",
                 message = "Name: Shuang Fan \n"
                           "Email: shuang.fan@tuni.fi\n"
                           "Student number: H255220")

    def __open_Help_Window(self):
        """
        Opens the help window.
        """
        Help_Window().start()

    def start(self):
        """
        Starts the mainloop.
        """
        self.__mainwindow.mainloop()

    def quit(self):
        """
        Ends the execution of the program.
        """
        check = messagebox.askokcancel("Confirm", "Are you sure to quit?")
        if check == True:
            try:
                self.__mainwindow.destroy()
                self.__helpwindow.destroy()
            except:
                None

#===== class Help_Window ======================================================
# This class is used to design the help window. In this window, there is the
# game instruction. The user can use the help file to play the game. This
# window can be opend with the main window at the same time.
class Help_Window:
    """
    The helpwindow's outfit design.
    """
    def __init__(self):
        """
        Initializes the help window.
        """
        # Creates the help window in another window.
        self.__helpwindow = Toplevel()
        self.__helpwindow.geometry("800x500+0+0")
        self.__helpwindow.title("Help")
        self.__helpwindow.iconbitmap("icon.ico")

        # Fonts settings.
        font_title = Font(family="Segoe print", size=20, weight="bold")
        font_text = Font(family="Arial", size=14)
        font_highlight = Font(family="Arial", size=17, slant="italic",
                              weight="bold")

        # Images settings.
        self.__image_1 = PhotoImage(file="help_1.gif")
        self.__image_2 = PhotoImage(file="help_2.gif")
        self.__image_3 = PhotoImage(file="help_3.gif")
        self.__image_4 = PhotoImage(file="help_4.gif")

        # Creates a frame
        main_frame = Frame(self.__helpwindow)
        main_frame.pack(fill=BOTH, expand=1)

        # Creates a canvas
        self.__canvas = Canvas(main_frame)
        self.__canvas.pack(side=LEFT, fill=BOTH, expand=1)

        # add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL,
                              command=self.__canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        # configure the canvas
        self.__canvas.configure(yscrollcommand=scrollbar.set)
        self.__canvas.bind('<Configure>', lambda e: self.__canvas.configure(
            scrollregion = self.__canvas.bbox("all")))
        self.__canvas.bind_all('<MouseWheel>',self.__on_mouse_wheel)

        # Creates a new frame inside the canvas to design all labels and button.
        frame = Frame(self.__canvas)

        # Adds the new frame to a window in the canvas.
        self.__canvas.create_window((0,0), window=frame, anchor="nw")

        # Designs the labels and button.
        label_1 = Label(frame, font=font_title, fg="#3D27FF", bg="#CBFFF6",
                        text="Welcome to play 'Aircraft Head Hunting' Game!")
        label_2 = Label(frame, font=font_text, text="Players: 2")
        label_3 = Label(frame, font=font_text,
                        text="Average time: 5-15 min.\n")
        label_4 = Label(frame, font=font_highlight, fg="#FF7F27", bg="#FFE1EA",
                        text="How to play?")
        label_5 = Label(frame, font=font_text,
                        text="1. Choose the level (default level is EASY) "
                             "and take a New Game.")
        label_6 = Label(frame, image=self.__image_1, relief=RIDGE)
        label_7 = Label(frame, image=self.__image_2, relief=RIDGE)
        label_8 = Label(frame, font=font_text,
                        text="2. Press the \"Start Game\".")
        label_9 = Label(frame, font=font_text, fg="#FF7F27",
                        text="3. On your turn!")
        label_10 = Label(frame, font=font_text, wraplength=750, justify=LEFT,
                         text="  Click a square on your board: \n"
                              "      If the square is the head of an aircraft,"
                              " it will turn to red color. \n"
                              "      If the square is the body of an aircraft,"
                              " it will turn to blue color. \n"
                              "      If the square isn't the head neither the "
                              "body of an aircraft, it will turn to white.")
        label_11 = Label(frame, font=font_text,
                         text="4. Play the game in turn. In one round, each of "
                              "you can click square once.")
        label_12 = Label(frame, image=self.__image_3, relief=RIDGE)
        label_13 = Label(frame, image=self.__image_4, relief=RIDGE)
        label_14 = Label(frame, font=font_highlight, fg="#FF7F27", bg="#FFE1EA",
                         text="How to win?")
        label_15 = Label(frame, font=font_text,
                         text="Find the aircraft head as fast as possible!\n")
        label_16 = Label(frame, font=font_title, fg="#0ED145",
                         text="Good luck! Enjoy the game!")
        # This button is used to close the help window.
        helpCloseButton = Button(frame, text="Close", bg="#FDF395",
                                 command=self.close_help,
                                 font=("Arial", 14, "bold"))

        # Sets the layout about all widgets.
        label_1.grid(row=0, column=0, columnspan=2)
        label_2.grid(row=1, column=0, columnspan=2, sticky=W)
        label_3.grid(row=2, column=0, columnspan=2, sticky=W)
        label_14.grid(row=3, column=0, columnspan=2, sticky=W)
        label_15.grid(row=4, column=0, columnspan=2, sticky=W)
        label_4.grid(row=5, column=0, columnspan=2, sticky=W)
        label_5.grid(row=6, column=0, columnspan=2, sticky=W)
        label_6.grid(row=7, column=0)
        label_7.grid(row=7, column=1)
        label_8.grid(row=8, column=0, columnspan=2, sticky=W)
        label_9.grid(row=9, column=0, columnspan=2, sticky=W)
        label_10.grid(row=10, column=0, columnspan=2, sticky=W)
        label_11.grid(row=11, column=0, columnspan=2, sticky=W)
        label_12.grid(row=12, column=0, columnspan=2)
        label_13.grid(row=13, column=0, columnspan=2)
        label_16.grid(row=14, column=0)
        helpCloseButton.grid(row=14, column=1)

    def __on_mouse_wheel(self, event):
        """
        This method is used to scroll the canvas by mouse wheel.
        :param event: a tkinter event about mouse wheel.
        """
        self.__canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def start(self):
        """
        Starts a new help window mainloop when the user clicks the
        help-command. In the help window, there is game instruction to help
        new player enjoys the game.
        """
        self.__helpwindow.mainloop()

    def close_help(self):
        """
        Closes the help window.
        """
        self.__helpwindow.destroy()


# ----- Creates a new game (event/process) ----------------------------
def create_game(level, out_board):
    """
    Creates a new game with random aircrafts. Sometimes the gameboard cannot
    create at once.
    * This is the real main function for a game.
    """
    if level == "EASY":
        board = Gameboard(8)

        plane_1 = Random_aircraft_SIMPLE(8).get_aircraft()
        board.add_aircraft(plane_1.get_coordinates())

        plane_2 = Random_aircraft_SIMPLE(8).get_aircraft()
        while not board.add_aircraft(plane_2.get_coordinates()):
            plane_2 = Random_aircraft_SIMPLE(8).get_aircraft()

    if level == "MEDIUM":
        board = Gameboard(10)

        plane_1 = Random_aircraft_SIMPLE(10).get_aircraft()
        board.add_aircraft(plane_1.get_coordinates())

        plane_2 = Random_aircraft_SIMPLE(10).get_aircraft()
        while not board.add_aircraft(plane_2.get_coordinates()):
            plane_2 = Random_aircraft_SIMPLE(10).get_aircraft()

        plane_3 = Random_aircraft_SIMPLE(10).get_aircraft()
        while not board.add_aircraft(plane_3.get_coordinates()):
            plane_3 = Random_aircraft_SIMPLE(10).get_aircraft()

    if level == "HARD":
        board = Gameboard(12)

        plane_1 = Random_aircraft_COMPLEX(12).get_aircraft()
        board.add_aircraft(plane_1.get_coordinates())

        plane_2 = Random_aircraft_COMPLEX(12).get_aircraft()
        while not board.add_aircraft(plane_2.get_coordinates()):
            plane_2 = Random_aircraft_COMPLEX(12).get_aircraft()

        plane_3 = Random_aircraft_COMPLEX(12).get_aircraft()
        while not board.add_aircraft(plane_3.get_coordinates()):
            plane_3 = Random_aircraft_COMPLEX(12).get_aircraft()

        plane_4 = Random_aircraft_COMPLEX(12).get_aircraft()
        while not board.add_aircraft(plane_4.get_coordinates()):
            plane_4 = Random_aircraft_COMPLEX(12).get_aircraft()

    # Returns the board value.
    out_board.put(board)

def game_main(level):
    """
    This function is used to terminate the process during it is timeout. The
    function returns the None value, if the game's creating process is timeout.
    :return Gameboard, the gameboard information. If the process is timeout,
            returns None.
    """
    out_board = Queue()
    # Creates a Process
    action_process = Process(target=create_game, args=(level, out_board))

    # Starts the process and blockes for 3 seconds.
    action_process.start()
    action_process.join(timeout=3)

    # Terminates the process.
    action_process.terminate()
    # If the process is timeout, returns None. Otherwise returns the
    # gameboard information.
    if action_process.exitcode != 0:
        return None
    else:
        board = out_board.get()
        return board

def main():
    ui = Find_Aircraft_Head_Game("EASY")
    ui.start()

if __name__ == '__main__':
    main()