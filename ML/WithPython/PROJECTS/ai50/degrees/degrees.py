import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Map names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Map movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Loads all the necessary CSV data (people, movies, and stars) 
    into our main memory dictionaries so we can search through them quickly.
    """
    # Let's begin by pulling all the people into memory
    with open(f"{directory}/people.csv", encoding="utf-8") as people_csv_file:
        people_csv_reader = csv.DictReader(people_csv_file)
        for current_row_data in people_csv_reader:
            people[current_row_data["id"]] = {
                "name": current_row_data["name"],
                "birth": current_row_data["birth"],
                "movies": set()
            }
            # Keep track of their names in lowercase to handle case-insensitive lookups later
            lowercase_person_name = current_row_data["name"].lower()
            if lowercase_person_name not in names:
                names[lowercase_person_name] = {current_row_data["id"]}
            else:
                names[lowercase_person_name].add(current_row_data["id"])

    # Now let's load all the movie data
    with open(f"{directory}/movies.csv", encoding="utf-8") as movies_csv_file:
        movies_csv_reader = csv.DictReader(movies_csv_file)
        for current_row_data in movies_csv_reader:
            movies[current_row_data["id"]] = {
                "title": current_row_data["title"],
                "year": current_row_data["year"],
                "stars": set()
            }

    # Finally, link the people and movies together using the stars data
    with open(f"{directory}/stars.csv", encoding="utf-8") as stars_csv_file:
        stars_csv_reader = csv.DictReader(stars_csv_file)
        for current_row_data in stars_csv_reader:
            try:
                # Add the movie to the person's list of movies
                people[current_row_data["person_id"]]["movies"].add(current_row_data["movie_id"])
                # Add the person to the movie's list of stars
                movies[current_row_data["movie_id"]]["stars"].add(current_row_data["person_id"])
            except KeyError:
                # If we encounter an ID that wasn't in our earlier files, just ignore it
                pass


def main():
    # Make sure the user provided the correct number of arguments
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    
    # Decide which directory to use (defaults to 'large' if none provided)
    target_data_directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Start the loading process
    print("Loading data...")
    load_data(target_data_directory)
    print("Data loaded.")

    # Get the starting person
    starting_actor_id = person_id_for_name(input("Name: "))
    if starting_actor_id is None:
        sys.exit("Person not found.")
        
    # Get the destination person
    target_actor_id = person_id_for_name(input("Name: "))
    if target_actor_id is None:
        sys.exit("Person not found.")

    # Find the path between them
    found_connection_path = shortest_path(starting_actor_id, target_actor_id)

    if found_connection_path is None:
        print("Not connected.")
    else:
        total_degrees_of_separation = len(found_connection_path)
        print(f"{total_degrees_of_separation} degrees of separation.")
        
        # We add a dummy 'None' movie at the beginning just so it aligns perfectly with the path
        found_connection_path = [(None, starting_actor_id)] + found_connection_path
        
        for path_index_num in range(total_degrees_of_separation):
            first_person_name = people[found_connection_path[path_index_num][1]]["name"]
            second_person_name = people[found_connection_path[path_index_num + 1][1]]["name"]
            shared_movie_title = movies[found_connection_path[path_index_num + 1][0]]["title"]
            print(f"{path_index_num + 1}: {first_person_name} and {second_person_name} starred in {shared_movie_title}")


def shortest_path(source, target):
    """
    This function searches for the shortest sequence of movies and actors 
    to connect our starting actor (source) to the destination actor (target).
    It returns a list of tuples containing (movie_id, person_id).
    If they are not connected at all, it simply returns None.
    """

    # If the starting person is the exact same as the target, there's no path needed.
    if source == target:
        return []

    # We'll use a queue to do a Breadth-First Search (BFS) so we find the shortest path first.
    exploration_queue_frontier = QueueFrontier()
    
    # Initialize the starting point of our search
    initial_search_node = Node(state=source, parent=None, action=None)
    exploration_queue_frontier.add(initial_search_node)

    # Keep track of actors we have already investigated to avoid infinite loops
    already_investigated_actors = set()

    while not exploration_queue_frontier.empty():
        # Grabing the next actor to process from our queue
        currently_evaluating_node = exploration_queue_frontier.remove()
        already_investigated_actors.add(currently_evaluating_node.state)

        # Going through all the movies this actor has been in, and their co-stars
        for shared_movie_id, co_star_person_id in neighbors_for_person(currently_evaluating_node.state):
            
            # We only care about co-stars we haven't seen or queued up yet
            if co_star_person_id not in already_investigated_actors and not exploration_queue_frontier.contains_state(co_star_person_id):
                
                # Create a new node representing this connection
                newly_discovered_connection_node = Node(
                    state=co_star_person_id, 
                    parent=currently_evaluating_node, 
                    action=shared_movie_id
                )

                # Did we just find the target person? If so, build the path backwards!
                if co_star_person_id == target:
                    final_connection_path = []
                    current_backtracking_node = newly_discovered_connection_node
                    
                    while current_backtracking_node.parent is not None:
                        final_connection_path.append((current_backtracking_node.action, current_backtracking_node.state))
                        current_backtracking_node = current_backtracking_node.parent
                        
                    # Reverse it since we built it from the target back to the source
                    final_connection_path.reverse()
                    return final_connection_path

                # Otherwise, add this co-star to the queue so we can search their connections later
                exploration_queue_frontier.add(newly_discovered_connection_node)

    # If we run out of people to check and never found the target, there's no connection.
    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    potential_person_ids_list = list(names.get(name.lower(), set()))
    
    if len(potential_person_ids_list) == 0:
        return None
    elif len(potential_person_ids_list) > 1:
        print(f"Which '{name}'?")
        for current_ambiguous_id in potential_person_ids_list:
            fetched_person_data = people[current_ambiguous_id]
            retrieved_person_name = fetched_person_data["name"]
            retrieved_person_birth = fetched_person_data["birth"]
            print(f"ID: {current_ambiguous_id}, Name: {retrieved_person_name}, Birth: {retrieved_person_birth}")
        try:
            chosen_intended_id = input("Intended Person ID: ")
            if chosen_intended_id in potential_person_ids_list:
                return chosen_intended_id
        except ValueError:
            pass
        return None
    else:
        return potential_person_ids_list[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    actor_associated_movie_ids = people[person_id]["movies"]
    discovered_neighboring_costars = set()
    
    for current_associated_movie_id in actor_associated_movie_ids:
        for costar_person_id_in_movie in movies[current_associated_movie_id]["stars"]:
            discovered_neighboring_costars.add((current_associated_movie_id, costar_person_id_in_movie))
            
    return discovered_neighboring_costars


if __name__ == "__main__":
    main()
