import sys
import random

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # TESTED
        # Self.domains is a dictionary mapping variables to set of values
        for variable in self.domains:
            temp_values = list(self.domains[variable])

            for value in temp_values:
                if len(value) != variable.length:
                    self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # TESTED
        revision = False

        if self.crossword.overlaps[x, y] == None:
            return revision
        
        (a, b) = self.crossword.overlaps[x, y]
        temp_values = list(self.domains[x])

        for value_x in temp_values:
            x_consistent = False

            for value_y in self.domains[y]:
                if value_x[a] == value_y[b] and value_x != value_y:
                    x_consistent = True
                    break

            # If a certain value in x domain (value_x) is not arc consistent 
            # with any value in y domain (value_y), delete value_x
            if x_consistent == False:
                self.domains[x].remove(value_x)
                revision = True
        
        return revision
            
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs is None, start with an initial queue of all of the arcs 
        if arcs == None:
            arcs = []

            for var0 in self.domains:
                for var1 in self.crossword.neighbors(var0):
                    arcs.append((var0, var1))

        while len(arcs) > 0:
            var0, var1 = arcs.pop(0)
            if self.revise(var0, var1):
                if len(self.domains[var0]) == 0:
                    return False

                # Check if arc consistency with var0 still holds if var0 domains have been changed
                for neighbour in self.crossword.neighbors(var0):
                    if neighbour != var1:
                        arcs.append((neighbour, var0))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
            if assignment[variable] not in self.crossword.words:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        word_assigned = []

        # assignment is a dictionary mapping every variable to a value
        for variable in assignment:
            word = assignment[variable]

            # Make sure all words are distinct
            if word not in word_assigned:
                word_assigned.append(word)
            else:
                return False

            # Make sure all words are the correct length
            if len(word) != variable.length:
                return False

            # Make sure all words are arc consistent
            for neighbour in self.crossword.neighbors(variable):
                if neighbour not in assignment:
                    continue

                (x, y) = self.crossword.overlaps[variable, neighbour]

                if word[x] != assignment[neighbour][y]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        eliminated_by_value = {}

        for value in self.domains[var]:
            eliminated_by_value[value] = 0

            for neighbour in self.crossword.neighbors(var):
                if neighbour not in assignment and value == self.domains[neighbour]:
                    eliminated_by_value[value] += 1

        sorted_ebv = dict(sorted(eliminated_by_value.items(), key=lambda value: value[1]))
        return list(sorted_ebv.keys())

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # TESTED
        unassigned_variable = {}

        for variable in self.domains:
            if variable not in assignment:
                unassigned_variable[variable] = len(self.domains[variable])

        min_value = min(unassigned_variable.values())
        min_variable = []

        # Choose a variable with the fewest amount of values on its domain
        for variable in unassigned_variable:
            if unassigned_variable[variable] == min_value:
                min_variable.append(variable)

        if len(min_variable) > 1:
            # If there's a tie, sort by degree (amount of neighbour) and choose the highest
            neighbour_amount = (self.crossword.neighbors(variable) for variable in min_variable)
            max_neighbour = max(neighbour_amount)

            for variable in min_variable:
                if self.crossword.neighbors(variable) == max_neighbour:
                    return variable
        else:
            return min_variable[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(variable, assignment):
            temp_assignment = dict(assignment)
            temp_assignment[variable] = value

            if self.consistent(temp_assignment):
                result = self.backtrack(temp_assignment)
                if result != None:
                    return result

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
