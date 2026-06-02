import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    overall_calculated_joint_probability = 1.0

    # go thru family members
    for family_member_name in people:
        
        # how many genes we assume for them
        if family_member_name in two_genes:
            assumed_gene_count_for_member = 2
        elif family_member_name in one_gene:
            assumed_gene_count_for_member = 1
        else:
            assumed_gene_count_for_member = 0

        # check if they show trait
        shows_physical_trait_flag = family_member_name in have_trait

        mother_of_member = people[family_member_name]["mother"]
        father_of_member = people[family_member_name]["father"]

        if mother_of_member is None and father_of_member is None:
            # missing parents so use baseline prob
            chance_of_getting_these_genes = PROBS["gene"][assumed_gene_count_for_member]
        else:
            # got parents so find inheritance chance
            parent_passing_chances = {}
            
            for parental_figure in [mother_of_member, father_of_member]:
                # parent gene count
                if parental_figure in two_genes:
                    genes_for_parent = 2
                elif parental_figure in one_gene:
                    genes_for_parent = 1
                else:
                    genes_for_parent = 0

                # chance of passing gene
                if genes_for_parent == 0:
                    # 0 genes so must be mutation
                    passing_probability = PROBS["mutation"]
                elif genes_for_parent == 1:
                    # 50/50 then add mutation
                    passing_probability = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                else:
                    # passed it unless mutation happens
                    passing_probability = 1 - PROBS["mutation"]

                parent_passing_chances[parental_figure] = passing_probability

            # combine for the kid
            if assumed_gene_count_for_member == 0:
                # both missed
                chance_of_getting_these_genes = (1 - parent_passing_chances[mother_of_member]) * (1 - parent_passing_chances[father_of_member])
            elif assumed_gene_count_for_member == 1:
                # from mom not dad OR from dad not mom
                got_from_mom_only = parent_passing_chances[mother_of_member] * (1 - parent_passing_chances[father_of_member])
                got_from_dad_only = parent_passing_chances[father_of_member] * (1 - parent_passing_chances[mother_of_member])
                chance_of_getting_these_genes = got_from_mom_only + got_from_dad_only
            else:
                # both passed it down
                chance_of_getting_these_genes = parent_passing_chances[mother_of_member] * parent_passing_chances[father_of_member]

        # get trait prob
        chance_of_showing_trait = PROBS["trait"][assumed_gene_count_for_member][shows_physical_trait_flag]

        # multiply to running total
        overall_calculated_joint_probability *= (chance_of_getting_these_genes * chance_of_showing_trait)

    return overall_calculated_joint_probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person_in_the_family in probabilities:
        
        # get their gene count here
        if person_in_the_family in two_genes:
            gene_amount_for_update = 2
        elif person_in_the_family in one_gene:
            gene_amount_for_update = 1
        else:
            gene_amount_for_update = 0

        # got trait?
        exhibits_the_trait = person_in_the_family in have_trait

        # add p to totals
        probabilities[person_in_the_family]["gene"][gene_amount_for_update] += p
        probabilities[person_in_the_family]["trait"][exhibits_the_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person_record in probabilities.values():
        
        # normalize genes to sum to 1
        total_sum_of_raw_gene_probabilities = sum(person_record["gene"].values())
        for amount_of_genes in person_record["gene"]:
            person_record["gene"][amount_of_genes] /= total_sum_of_raw_gene_probabilities

        # same for trait dist
        total_sum_of_raw_trait_probabilities = sum(person_record["trait"].values())
        for trait_status_flag in person_record["trait"]:
            person_record["trait"][trait_status_flag] /= total_sum_of_raw_trait_probabilities


if __name__ == "__main__":
    main()
