import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S Conj VP
NP -> N | Det N | Det AP N | AP N | NP PP
VP -> V | V NP | V NP PP | V PP | Adv VP | VP Adv
AP -> Adj | Adj AP
PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # cho p up the sentence into individual tokens using nltk
    chopped_up_words = nltk.word_tokenize(sentence)
    
    clean_word_list = []
    
    for raw_word_token in chopped_up_words:
        # we only care about words that have actual letters in them..
        has_at_least_one_letter = False
        
        for individual_character in raw_word_token:
            if individual_character.isalpha():
                has_at_least_one_letter = True
                break
                
        # if it passed the test make it lowercase and add it
        if has_at_least_one_letter:
            clean_word_list.append(raw_word_token.lower())
            
    return clean_word_list


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    valid_noun_phrase_chunks = []
    
    # hunt for every NP subtree recursively
    for candidate_subtree in tree.subtrees():
        
        if candidate_subtree.label() == "NP":
            found_nested_np = False
            
            # check the chidlren (but need to skip the rooot of this subtree)
            for inner_child in candidate_subtree.subtrees():
                if inner_child == candidate_subtree:
                    continue
                if inner_child.label() == "NP":
                    found_nested_np = True
                    break
                    
            # if its pure (no nested NPs) we keep it
            if not found_nested_np:
                valid_noun_phrase_chunks.append(candidate_subtree)
                
    return valid_noun_phrase_chunks


if __name__ == "__main__":
    main()
