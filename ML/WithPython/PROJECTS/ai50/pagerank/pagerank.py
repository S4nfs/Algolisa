import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Hmm we need to figure out the exact chances of going to any other page next.
    calculated_probabilities_for_next_pages = {}
    total_number_of_pages_in_entire_corpus = len(corpus)
    pages_linked_from_current = corpus[page]
    
    # What if this page is a dead end and links nowhere?lets just assume it secretly links to everywhere (including itself) with equal chance....
    if len(pages_linked_from_current) == 0:
        for every_single_page_name in corpus:
            calculated_probabilities_for_next_pages[every_single_page_name] = 1 / total_number_of_pages_in_entire_corpus
        return calculated_probabilities_for_next_pages
        
    # if they have links calculate the baseline random chance of landing on any page
    baseline_random_jumping_chance = (1 - damping_factor) / total_number_of_pages_in_entire_corpus
    
    # Give every page its baseline chance first
    for every_single_page_name in corpus:
        calculated_probabilities_for_next_pages[every_single_page_name] = baseline_random_jumping_chance
        
    # Now, let's distribute the damping factor probability equally among the actual links!
    chance_of_following_a_specific_link = damping_factor / len(pages_linked_from_current)
    
    for linked_page_destination in pages_linked_from_current:
        calculated_probabilities_for_next_pages[linked_page_destination] += chance_of_following_a_specific_link
        
    return calculated_probabilities_for_next_pages


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    tally_of_visits_per_page = {page_name_key: 0 for page_name_key in corpus}
    
    # First drop of the surfer is completely random anywhere in the corpus!
    currently_visited_web_page = random.choice(list(corpus.keys()))
    tally_of_visits_per_page[currently_visited_web_page] += 1
    
    # lready did 1 sample, so let's do the remaining n - 1 samples
    for current_simulation_step in range(1, n):
        # Let's see what the probabilities are from the current page
        probabilities_for_next_jump = transition_model(corpus, currently_visited_web_page, damping_factor)
        
        # We need to separate the page names from their probabilities to feed them into random.choices
        list_of_possible_destinations = list(probabilities_for_next_jump.keys())
        list_of_chances_for_destinations = list(probabilities_for_next_jump.values())
        
        # random.choices returns a list, so we grab the first (and only) element
        currently_visited_web_page = random.choices(list_of_possible_destinations, weights=list_of_chances_for_destinations, k=1)[0]
        
        # Mark down that we visited this page!!!!!!!
        tally_of_visits_per_page[currently_visited_web_page] += 1
        
    # Finally, convert the raw visit counts into percentages (which represent the PageRank)
    final_estimated_pageranks_from_sampling = {}
    for specific_page_name, total_visit_count in tally_of_visits_per_page.items():
        final_estimated_pageranks_from_sampling[specific_page_name] = total_visit_count / n
        
    return final_estimated_pageranks_from_sampling


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    total_amount_of_pages = len(corpus)
    
    # Start everyone off with an equal piece of the pie
    current_calculated_page_ranks = {page_name: 1 / total_amount_of_pages for page_name in corpus}
    
    # We will keep going until things settle down and stop changing significantly
    we_are_still_crunching_numbers = True
    
    while we_are_still_crunching_numbers:
        we_are_still_crunching_numbers = False
        newly_calculated_page_ranks_for_this_round = {}
        
        # calculate the new rank for every single page
        for target_destination_page in corpus:
            
            # The baseline rank that every page gets no matter what
            accumulated_rank_score_so_far = (1 - damping_factor) / total_amount_of_pages
            
            # look at who is actually linking TO this target page
            for potential_linking_source_page in corpus:
                links_on_source_page = corpus[potential_linking_source_page]
                
                # If a page has NO links, it's considered to link to EVERYONE (incluing our target)
                if len(links_on_source_page) == 0:
                    accumulated_rank_score_so_far += damping_factor * (current_calculated_page_ranks[potential_linking_source_page] / total_amount_of_pages)
                
                # Otherwise, if it literally links to our target page, we grab a share of its rank
                elif target_destination_page in links_on_source_page:
                    accumulated_rank_score_so_far += damping_factor * (current_calculated_page_ranks[potential_linking_source_page] / len(links_on_source_page))
            
            # Save the new score
            newly_calculated_page_ranks_for_this_round[target_destination_page] = accumulated_rank_score_so_far
            
        # Before we update our main dictionary let's check if any values swung wildly (more than 0.001)
        for page_name_to_check in corpus:
            difference_between_old_and_new = abs(current_calculated_page_ranks[page_name_to_check] - newly_calculated_page_ranks_for_this_round[page_name_to_check])
            if difference_between_old_and_new > 0.001:
                we_are_still_crunching_numbers = True
                
        # Now it's safe to update the master list for the next round
        current_calculated_page_ranks = newly_calculated_page_ranks_for_this_round.copy()
        
    return current_calculated_page_ranks


if __name__ == "__main__":
    main()
