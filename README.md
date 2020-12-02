# Fall20-Project -  Range with Mirror
Final project from the Fall 2020 semester  

Xinyu Huang - xinyuh10  

## Introduction
*Range* is a puzzle game from *Simon Tatham's Portable Puzzle Collection*.  
The game is published on: https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/range.html  

Credit for this puzzle goes to Nikoli, who created this puzzle and called it whether "Kurodoko" or "Kuromasu".  
An overview of *Kuromasu*: https://en.wikipedia.org/wiki/Kuromasu  

The puzzle board is a rectangular grid consists of white cells, numbered cells and hidden black cells.  

The puzzle has four basic rules:  
1. Each number on the board represents the number of white cells that can be seen from that cell in four directions (vertically and horizontally), including itself.  
2. No two black cells are orthogonally adjacent.  
3. No group of white cells is seperated by black cells.  
4. Numbered cells are white cells.  

To solve the puzzle, players should guess the positions of the hidden black cells, or in other words, place the black cells in the right cells to make the board status conform all the rules above.  

My variation: Mirror.  
Beside the numbered cells, there is another kind of "mirror" cell. In stead of going straightly, the sight will be reflected when meet a mirror. (like the mirror works in "Undead" puzzle from Simon Tatham's Portable Puzzle Collection)  
The mirror cells are also counted as white cells.  

## Programming Design & Logic
Since the number of black cells is not explicitly provided, it is not effective to apply the backtrack strategy to search the right positions. An alternative way is to start from the exist conditions and use the deductive logic to infer the positions of the black cells. To implement this idea, this project applied Pycosat package. Each possible condition is translated to a CNF clause. The hidden cells can be found by solving the combination of all CNF clauses.  

Two classes are included in the code: range board and numbered cells.  
Range board represents the whole game board, includes the board status and several interactive functions.  
Cell represents each numbered cells, includes the cell value, the path from four directions and some path-searching functions.  

The steps of creating CNF clauses:  
1. Each cell can be white or black. (General rule)  
2. Numbered cells and mirror cells are white. (Rule 4)  
3. For each numbered cell, we can list the possible permutations of black cells according to its condition. I use "or"s to combine these different permutations, and use "and"s to combine the cells together. (Rule 1)  
4. For each black cell, its adjacent cells are exactly white. (Rule 2)  

It's difficult to translate rule 3 to a CNF clause. To verify this rule, the strategy is to collect possible solutions, then check the connectivity of white cells by a simplified Seed-Filling algorithm.  

## Big-O Complexity Analysis
w - width of the game board     h - height of the game board  
n - number of numbered cells    m - number on the numbered cell  
\*This analysis will not take mirrors into consider since the mirrors can make a sight path very long or very short.  

#### For each numbered cell
Search one path: O(w) or O(h)  
Find possible permutation will traverse the four paths in a nested loop, so when the cell is in the middle (worst condition):  
(h/2)\*(w/2)\*(h/2)\*(w/2) => O((w\*h)^2)  

#### Read all clues
Each clue need a find permutation process: O(n\*(w\*h)^2)  

#### CNF clauses and Check Connectivity
Assign the general value (step 1): twice for each cell, 2\*w\*h => O(w\*h)  
Assign value to Numbered cells (step 2): O(n)  
Possible permutations (step 3): assume each permutation is possible (worst condition), so it becomes the problem to split a number to the sum of four numbers. We can calculate it by looking at the partition problem: partition m balls in 4 groups. => (m\*m\*m)/(3\*2\*1) => O(m^3)
Adjacent cells (step 4): O(w\*h)  
from_dnf(): the length of DNF clause will be (O(m^3) ors) \* n ands, the complexity depends on how this function works, but this is why my program run very slow.  
Check connectivity: Scan the game board twice: O(w*\h)  

So, to solve a puzzle, the complexity would be O(n\*(w\*h)^2 + O(from_dnf(m^3\*n groups)) + O(solve_all())), from the runtime coverage, it seems from_dnf() runs most of the time.  

#### Generator
List all coordinate (empty cells): O(w\*h)  
Place black cells, randomly select several empty cells, place black boxes on it, then check Rule 2 and Rule 3 once, discard this choice if this boxes does not fit the rule: (w\*h cells)\*(w\*h check rules) => O((w\*h)^2)  
Place mirrors: simply select several empty cells, O(w\*h)  
Place numbered cells: O(w\*h) candidate cells, then try to solve this temporary puzzle to guarantee there is only one solution, add one more clue if there are two or more solutions. => O(w\*h\*O(solve the puzzle))  
