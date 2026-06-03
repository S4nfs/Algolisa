# Analysis

## Layer 8, Head 9

This attention head appears to be paying attention to adjectives and the specific nouns they are modifying. It creates a strong link between descriptive words and their subjects.

Example Sentences:
- "The bright [MASK] shone in the sky." -> The word "bright" attended very strongly to the predicted word "sun".
- "He wore a heavy [MASK] in the winter." -> The word "heavy" attended almost exclusively to the predicted word "coat".

## Layer 9, Head 1

This attention head seems to be mapping pronouns back to the specific proper nouns (people or entities) they are referring to earlier in the sentence, effectively resolving coreferences.

Example Sentences:
- "John dropped the box because [MASK] was clumsy." -> The word "he" (the predicted mask) attended heavily back to "john".
- "Sarah went to the store and [MASK] bought some milk." -> The predicted word "she" attended strongly back to "sarah" across the sentence.

