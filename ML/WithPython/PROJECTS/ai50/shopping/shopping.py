import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # mapping first heere months strings to int index (jan = 0, dec = 11)
    month_str_to_int_map = {
        "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5, 
        "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11
    }

    all_evidence_features = []
    all_target_labels = []

    # load data
    with open(filename, newline='') as csv_data_file:
        spreadsheet_reader = csv.reader(csv_data_file)
        next(spreadsheet_reader) 

        for individual_row_data in spreadsheet_reader:
            # build the feature list for this specific user session
            current_user_evidence = []
            
            # extract basic page counts (ints)
            current_user_evidence.append(int(individual_row_data[0]))
            current_user_evidence.append(float(individual_row_data[1]))
            current_user_evidence.append(int(individual_row_data[2]))
            current_user_evidence.append(float(individual_row_data[3]))
            current_user_evidence.append(int(individual_row_data[4]))
            current_user_evidence.append(float(individual_row_data[5]))
            
            # extract analytics metrics (floats)
            current_user_evidence.append(float(individual_row_data[6]))
            current_user_evidence.append(float(individual_row_data[7]))
            current_user_evidence.append(float(individual_row_data[8]))
            current_user_evidence.append(float(individual_row_data[9]))
            
            # month mapping
            month_string_value = individual_row_data[10]
            current_user_evidence.append(month_str_to_int_map.get(month_string_value, 0))
            
            # operating system, browser, etc
            current_user_evidence.append(int(individual_row_data[11]))
            current_user_evidence.append(int(individual_row_data[12]))
            current_user_evidence.append(int(individual_row_data[13]))
            current_user_evidence.append(int(individual_row_data[14]))
            
            # visitor type checking (1 if returning, 0 otherwise)
            is_returning_visitor = 1 if individual_row_data[15] == "Returning_Visitor" else 0
            current_user_evidence.append(is_returning_visitor)
            
            # weekend flag (1 if True, 0 if False)
            is_weekend_visit = 1 if individual_row_data[16] == "TRUE" else 0
            current_user_evidence.append(is_weekend_visit)

            all_evidence_features.append(current_user_evidence)
            
            # check if they actually bought something
            did_they_purchase = 1 if individual_row_data[17] == "TRUE" else 0
            all_target_labels.append(did_they_purchase)

    return (all_evidence_features, all_target_labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # useing knn classifier with k=1
    nearest_neighbor_classifier_model = KNeighborsClassifier(n_neighbors=1)
    
    # fit it to our training data
    nearest_neighbor_classifier_model.fit(evidence, labels)
    
    return nearest_neighbor_classifier_model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    total_actual_purchases = 0
    correctly_guessed_purchases = 0
    
    total_actual_non_purchases = 0
    correctly_guessed_non_purchases = 0
    
    # compare every prediction to reality
    for actual_ground_truth, predicted_result in zip(labels, predictions):
        if actual_ground_truth == 1:
            # this user really bought something
            total_actual_purchases += 1
            if predicted_result == 1:
                correctly_guessed_purchases += 1
        else:
            # this user just browsed and left
            total_actual_non_purchases += 1
            if predicted_result == 0:
                correctly_guessed_non_purchases += 1
                
    # calc final rates
    model_sensitivity_score = correctly_guessed_purchases / total_actual_purchases
    model_specificity_score = correctly_guessed_non_purchases / total_actual_non_purchases
    
    return (model_sensitivity_score, model_specificity_score)


if __name__ == "__main__":
    main()
