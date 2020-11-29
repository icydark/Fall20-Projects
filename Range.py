from sat_utils import solve_one, from_dnf, one_of, solve_all
# ref:https://rhettinger.github.io/einstein.html#essential-utilities-for-humanization
from sys import intern
from itertools import product
import time
from _collections import deque
from copy import deepcopy


# pycosat package can only run with python 3.7 interpreter under my local environment


class ClueCell:
    def __init__(self, coordinate, value, board):
        self.position, self.value, self.board = coordinate, value, board
        self.left, self.right, self.up, self.down = [], [], [], []  # available white cells in each direction
        self.permutation_box = []  # black boxes permutation
        self.permutation_white = []  # white cells permutation

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
                            new_comb_box, new_combo_white = {}, {}
                            new_combo_white['middle'] = [self.position]
                            if self.left and i < len(self.left):
                                new_comb_box['left'] = self.left[i]
                                new_combo_white['left'] = self.left[:i]
                            else:
                                new_comb_box['left'] = ()
                                new_combo_white['left'] = self.left[:]

                            if self.right and j < len(self.right):
                                new_comb_box['right'] = self.right[j]
                                new_combo_white['right'] = self.right[:j]
                            else:
                                new_comb_box['right'] = ()
                                new_combo_white['right'] = self.right[:]

                            if self.up and m < len(self.up):
                                new_comb_box['up'] = self.up[m]
                                new_combo_white['up'] = self.up[:m]
                            else:
                                new_comb_box['up'] = ()
                                new_combo_white['up'] = self.up[:]

                            if self.down and n < len(self.down):
                                new_comb_box['down'] = self.down[n]
                                new_combo_white['down'] = self.down[:n]
                            else:
                                new_comb_box['down'] = ()
                                new_combo_white['down'] = self.down[:]

                            self.permutation_box.append(new_comb_box)
                            self.permutation_white.append(new_combo_white)

        # print(self.permutation_box)
        # print(self.permutation_white)


class Range:
    def __init__(self, width=3, height=3):
        self.width, self.height = width, height
        self.board = [[' '] * width for _ in range(height)]
        self.clues = []
        self.candidate = []
        self.cnf = []

    def read_clue(self, board):
        self.board = board
        self.height, self.width = len(board), len(board[0])
        for i in range(len(board)):
            for j in range(len(board[i])):
                if self.board[i][j].isdigit():
                    new_clue = ClueCell((i, j), int(board[i][j]), board)
                    new_clue.search_candidates()
                    self.clues.append(new_clue)

    def find_adjacency(self, point: tuple):
        """
        For a given coordinate, find all coordinates adjacent to it
        """
        x = point[0]
        y = point[1]
        if x == 0:
            if y == 0:
                return [(0, 1), (1, 0)]
            elif y == self.width - 1:
                return [(0, self.width - 2), (1, self.width - 1)]
            else:
                return [(x, y - 1), (x, y + 1), (x + 1, y)]
        elif x == self.height - 1:
            if y == 0:
                return [(self.height - 1, 1), (self.height - 2, 0)]
            elif y == self.width - 1:
                return [(self.height - 1, self.width - 2), (self.height - 2, self.width - 1)]
            else:
                return [(x, y - 1), (x, y + 1), (x - 1, y)]
        else:
            if y == 0:
                return [(x, y + 1), (x - 1, y), (x + 1, y)]
            elif y == self.width - 1:
                return [(x, y - 1), (x - 1, y), (x + 1, y)]
            else:
                return [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]

    def check_connectivity(self, black_boxes: list):
        """
        Label the white cells as 2 and black boxes as 0; scan the answer board twice,
        In the first scan , start a bfs when reach the first white cell, convert all the connect cells to 1, then stop
        scanning.
        In the second scan, find out is there any 2s left, if not, valid answer, else, invalid answer
        :param black_boxes: the cells to put black boxes
        :return:
        """

        label_board = [[2] * self.width for _ in range(self.height)]
        for point in black_boxes:
            x, y = point
            label_board[x][y] = 0

        flag = False
        for row in range(self.height):
            for col in range(self.width):
                if label_board[row][col] == 2:
                    # meet the first white cell
                    q = deque()
                    q.append((row, col))
                    while q:
                        x, y = q.popleft()
                        label_board[x][y] = 1
                        neighbors = self.find_adjacency((x, y))
                        for neighbor in neighbors:
                            n_x, n_y = neighbor
                            if label_board[n_x][n_y] == 2:
                                q.append(neighbor)
                    flag = True
                    break
            if flag:
                break

        for row in range(self.height):
            for col in range(self.width):
                if label_board[row][col] == 2:
                    return False
        return True

    def solve_range(self):

        def comb(point, value):
            """Format how a value is shown at a given coordinate"""
            return intern(f'{point} {value}')

        values = ['W', 'B']
        all_coords = list(product(range(self.height), range(self.width)))

        for coord in all_coords:
            # assign a "White" or "Black Box" value to each cell
            self.cnf += one_of(comb(coord, value) for value in values)

            # TODO: No two black squares are orthogonally adjacent.
            neighbor_coord = self.find_adjacency(coord)
            neighbor_dnf = [comb(coord, 'B')]
            for p in neighbor_coord:
                neighbor_dnf.append(comb(p, 'W'))
            self.cnf += from_dnf([neighbor_dnf, [comb(coord, 'W')]])

        for clue in self.clues:
            # for each clue (numbered cell), assign a valid permutation of black boxes
            permutation_len = len(clue.permutation_box)
            p_dnf = []
            for i in range(permutation_len):
                # different possible permutations for each clue
                temp = []
                for direction in clue.permutation_box[i].keys():
                    if clue.permutation_box[i][direction]:
                        temp.append(comb(clue.permutation_box[i][direction], 'B'))

                for direction in clue.permutation_white[i].keys():
                    for cell in clue.permutation_white[i][direction]:
                        temp.append(comb(cell, 'W'))

                p_dnf.append(temp)
            self.cnf += from_dnf(p_dnf)

        possible_solution = solve_all(self.cnf)
        for solution_facts in possible_solution:
            ans = deepcopy(self.board)
            box_list = []
            for fact_str in solution_facts:
                if fact_str[-1] == 'B':
                    row, col = eval(fact_str[:-2])
                    box_list.append((row, col))
                    ans[row][col] = 'B'

            if self.check_connectivity(box_list):
                # Verify the connectivity of white cells
                return ans

    def new_game(self):
        pass


if __name__ == '__main__':
    r = Range()
    r.read_clue([['4', ' ', '4', ' '],
                 [' ', '4', ' ', ' '],
                 [' ', ' ', '5', ' '],
                 [' ', '6', ' ', '6']])

    start = time.process_time()
    solution = r.solve_range()
    end = time.process_time()
    for line in solution:
        print(line)
    print('Solved in {} seconds'.format(end - start))

    """
    r = Range()
    r.read_clue([[' ', '9', ' ', ' ', ' ', ' '],
                 ['5', ' ', ' ', '3', ' ', ' '],
                 [' ', ' ', '3', ' ', ' ', '2'],
                 [' ', ' ', ' ', ' ', '5', ' ']])

    start = time.process_time()
    solution = r.solve_range()
    end = time.process_time()
    for line in solution:
        print(line)
    print('Solved in {} seconds'.format(end - start))

    r = Range()
    r.read_clue([['3', ' ', ' ', ' ', ' ', ' '],
                 [' ', ' ', ' ', '8', ' ', ' '],
                 ['3', ' ', ' ', '7', ' ', ' '],
                 [' ', ' ', '11', ' ', ' ', '11'],
                 [' ', ' ', '7', ' ', ' ', ' '],
                 [' ', ' ', ' ', ' ', ' ', '7']])

    start = time.process_time()
    solution = r.solve_range()
    end = time.process_time()
    for line in solution:
        print(line)
    print('Solved in {} seconds'.format(end - start))
    """