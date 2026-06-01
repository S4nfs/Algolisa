from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Every person on this island has to be strictly one of the two types
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    
    # If A is a knight, then this impossible statement must be true (which is a parado x)
    # Therefore, A has to be a lying knave!
    Biconditional(AKnight, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    #rules of the island for both A and B
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    
    # A claims that they are both knaves.
    # If A is telling the truth, then both A and B are knaves
    Biconditional(AKnight, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Setting up the basic rules ---
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    
    # Character A thinks they are both identical in their nature
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    
    # Character B strongly disagrees and says they are opposite
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # It's getting crowded.. establish the ground rules for A, B, and C first.
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),
    
    # A said either they are a knight or a knave. any posibilities
    Or(Biconditional(AKnight, AKnight), Biconditional(AKnight, AKnave)),
    
    # B is trying to tell us what A supposedly said. 
    # If B is telling the truth, A claimed to be a knave.
    Biconditional(BKnight, Biconditional(AKnight, AKnave)),
    
    # B also throws C under the bus by calling them a knave.
    Biconditional(BKnight, CKnave),
    
    # Meanwhile, C is vouching for A, saying A is definitely a knight.
    Biconditional(CKnight, AKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
