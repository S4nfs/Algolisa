# 🧠 Knowledge-Based Agents & Logical Inference in AI

This project explains how AI systems can use **formal logic** to represent knowledge and perform **reasoning**. The main focus is on **propositional logic**, **model checking**, and **inference** to create **knowledge-based agents**. Logic-based AI uses formal logic and symbolic rules to draw conclusions, while LLMs use statistical associations in natural language learned from data.

---

## 🔑 Key Concepts

| Concept                   | Summary                                                                          |
| ------------------------- | -------------------------------------------------------------------------------- |
| **Knowledge-Based Agent** | AI that stores facts (knowledge) and uses logic to derive new conclusions.       |
| **Propositional Logic**   | Logic involving true/false statements and connectives (AND, OR, NOT, etc).       |
| **Logical Connectives**   | Tools to combine/modify propositions: ¬ (NOT), ∧ (AND), ∨ (OR), → (IF), ↔ (IFF). |
| **Model**                 | A possible world — an assignment of truth values to all propositions.            |
| **Entailment (⊨)**        | If KB (knowledge base) is true, then a query α is also always true.              |
| **Inference**             | The process of deriving new facts from existing knowledge.                       |
| **Model Checking**        | Exhaustively check all possible models to verify entailment.                     |
| **Knowledge Engineering** | The process of structuring domain knowledge into logic form for AI.              |

---

## 📚 Logical Connectives and Truth Tables

| Connective        | Symbol | Description           | Truth Table                              |
| ----------------- | ------ | --------------------- | ---------------------------------------- |
| **Not**           | ¬P     | Negation              | ¬True = False<br>¬False = True           |
| **And**           | P ∧ Q  | Conjunction           | True only when P = True, Q = True        |
| **Or**            | P ∨ Q  | Inclusive Disjunction | False only when both P and Q are False   |
| **Implication**   | P → Q  | "If P then Q"         | False only when P = True, Q = False      |
| **Biconditional** | P ↔ Q  | "P if and only if Q"  | True when both are the same (T-T or F-F) |

---

## 🔁 Inference Rules

| Rule Name                       | Formal Notation                          | Description                                       |
| ------------------------------- | ---------------------------------------- | ------------------------------------------------- |
| **Modus Ponens**                | P → Q, P ⊢ Q                             | If P implies Q and P is true, then Q is true      |
| **And Elimination**             | P ∧ Q ⊢ P<br>P ∧ Q ⊢ Q                   | From P and Q, you can infer P and Q separately    |
| **Double Negation**             | ¬¬P ⊢ P                                  | Two NOTs cancel out — "not not P" means P is true |
| **Implication Elimination**     | P → Q ⊢ ¬P ∨ Q                           | "If P then Q" is equivalent to "not P or Q"       |
| **(Optional) De Morgan's Laws** | ¬(P ∧ Q) ⊢ ¬P ∨ ¬Q<br>¬(P ∨ Q) ⊢ ¬P ∧ ¬Q | NOT distributes over AND/OR                       |

---

---

## 🛠 Core Operations

| Operation     | Description                                                            |
| ------------- | ---------------------------------------------------------------------- |
| `TELL(KB, φ)` | Adds a sentence φ to the knowledge base (i.e., injects new knowledge). |
| `ASK(KB, α)`  | Queries whether a sentence α logically follows from the KB.            |

> In practice, `ASK` triggers an **inference algorithm** (e.g., model checking or logical deduction) to verify if `KB ⊨ α`.

## KB ⊨ α ⇔ In every model where KB is true, α is also true.

## 💡 Examples from the Project

### Example 1: Harry Potter Logic

- **Facts:**
  - If it didn’t rain, then Harry visited Hagrid.
  - Harry visited either Hagrid or Dumbledore, but not both.
  - Harry visited Dumbledore.
- **Inferred:**
  - Harry did **not** visit Hagrid.
  - Therefore, it **did** rain.

### Example 2: Clue Game

- Represented suspects, weapons, and rooms using logic symbols.
- Encoded knowledge like:
  - Only one suspect, one room, and one weapon is correct.
  - Some cards are known (e.g., “I have the revolver” → revolver is not in the envelope).
- Used inference to deduce the solution.

### Example 3: Logic Puzzle (Harry Potter House Sorting)

- Created 16 propositional symbols for 4 people × 4 houses.
- Encoded constraints: only one house per person, one person per house.
- Added clues and used inference to find each character’s house.

### Example 4: Mastermind Game

- Used logical inference to deduce color positions.
- Built a solver using propositional logic and model checking.

---

## 🧮 Limitation of Model Checking

- Model checking is exhaustive but **inefficient**.
- For `n` propositional variables → `2^n` possible models.
- Not scalable for large knowledge bases.

---
