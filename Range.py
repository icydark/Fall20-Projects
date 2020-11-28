from sat_utils import solve_one, from_dnf, one_of, solve_all
# ref:https://rhettinger.github.io/einstein.html#essential-utilities-for-humanization
from sys import intern
from itertools import product


# pycosat package can only run under python 3.7 interpreter on my local environment


class ClueCell:
    def __init__(self, coordinate, value, board):
        self.position, self.value, self.board = coordinate, value, board
        self.left, self.right, self.up, self.down = [], [], [], []
        # TODO: maybe need another left/right... to store while cells
        self.permutation = []

    def search_left(self):
        row, col = self.position
        if col == 0:
            # on the edge, nothing on the left
            return 0
        count = 0
        while True:
            col -= 1
            if not 0 <= row < len(self.board) or not 0 <= col < len(self.board[0]):
                break
            self.left.append((row, col))
            count += 1
        return count

    def search_right(self):
        row, col = self.position
        if col == len(self.board[0]) - 1:
            # on the edge, nothing on the right
            return 0
        count = 0
        while True:
            col += 1
            if not 0 <= row < len(self.board) or not 0 <= col < len(self.board[0]):
                break
            self.right.append((row, col))
            count += 1
        return count

    def search_up(self):
        row, col = self.position
        if row == 0:
            # on the edge, nothing on the up side
            return 0
        count = 0
        while True:
            row -= 1
            if not 0 <= row < len(self.board) or not 0 <= col < len(self.board[0]):
                break
            self.up.append((row, col))
            count += 1
        return count

    def search_down(self):
        row, col = self.position
        if row == len(self.board) - 1:
            # on the edge, nothing on the left
            return 0
        count = 0
        while True:
            row += 1
            if not 0 <= row < len(self.board) or not 0 <= col < len(self.board[0]):
                break
            self.down.append((row, col))
            count += 1
        return count

    def search_candidates(self):
        l_count = self.search_left()
        r_count = self.search_right()
        u_count = self.search_up()
        d_count = self.search_down()

        # TODO: Here is a naive method to find out the permutation of black boxes for each numbered cell
        #       Might exist a more advanced algorithm
        for i in range(l_count + 1):
            if self.left and i < len(self.left):
                row, col = self.left[i]
                if self.board[row][col] != ' ':
                    # the cell is numbered cell, cannot place a box, skip over
                    continue
            for j in range(r_count + 1):
                if self.right and j < len(self.right):
                    row, col = self.right[j]
                    if self.board[row][col] != ' ':
                        continue
                for m in range(u_count + 1):
                    if self.up and m < len(self.up):
                        row, col = self.up[m]
                        if self.board[row][col] != ' ':
                            continue
                    for n in range(d_count + 1):
                        if self.down and n < len(self.down):
                            row, col = self.down[n]
                            if self.board[row][col] != ' ':
                                continue
                        if i + j + m + n == self.value - 1:
                            # a valid permutation of black boxes for this clue (numbered cell)
                            new_comb = {}
                            if self.left and i < len(self.left):
                                new_comb['left'] = self.left[i]
                            else:
                                new_comb['left'] = ()
                            if self.right and j < len(self.right):
                                new_comb['right'] = self.right[j]
                            else:
                                new_comb['right'] = ()
                            if self.up and m < len(self.up):
                                new_comb['up'] = self.up[m]
                            else:
                                new_comb['up'] = ()
                            if self.down and n < len(self.down):
                                new_comb['down'] = self.down[n]
                            else:
                                new_comb['down'] = ()
                            self.permutation.append(new_comb)

        print(self.permutation)


class Range:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.board = [[' '] * width for _ in range(height)]
        self.clues = []
        self.candidate = []
        self.cnf = []

    def read_clue(self, board):
        self.board = board
        for i in range(len(board)):
            for j in range(len(board[i])):
                if self.board[i][j].isdigit():
                    new_clue = ClueCell((i, j), int(board[i][j]), board)
                    new_clue.search_candidates()
                    self.clues.append(new_clue)

    def solve_range(self):

        def comb(point, value):
            """Format how a value is shown at a given coordinate"""
            return intern(f'{point} {value}')

        values = ['W', 'B']
        all_coords = list(product(range(self.height), range(self.width)))

        for coord in all_coords:
            # assign a "White" or "Black Box" value to each cell
            self.cnf += one_of(comb(coord, value) for value in values)

        for clue in self.clues:
            # TODO: for each clue (numbered cell), assign a valid permutation of black boxes
            for p in clue.permutation:
                for direction in p.keys:
                    if p[direction]:
                        comb(p[direction], "B")

            pass

    def new_game(self):
        pass


if __name__ == '__main__':
    r = Range(4, 4)
    r.read_clue([['4', ' ', ' ', ' '],
                 ['7', ' ', ' ', ' '],
                 [' ', ' ', ' ', '4'],
                 [' ', ' ', ' ', '6']])
