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
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)

        evidence = []
        labels = []
        for row in reader:
            row_evidence = [int(row[0])]
            row_evidence.append(float(row[1]))
            row_evidence.append(int(row[2]))
            row_evidence.append(float(row[3]))
            row_evidence.append(int(row[4]))
            row_evidence.append(float(cell) for cell in row[5:10])
            row_evidence.append(
                0 if row[10] == "Jan" 
                else 1 if row[10] == "Feb"
                else 2 if row[10] == "Mar"
                else 3 if row[10] == "Apr"
                else 4 if row[10] == "May"
                else 5 if row[10] == "Jun"
                else 6 if row[10] == "Jul"
                else 7 if row[10] == "Aug"
                else 8 if row[10] == "Sep"
                else 9 if row[10] == "Oct"
                else 10 if row[10] == "Nov"
                else 11)
            row_evidence.append(int(cell) for cell in row[11:15])
            row_evidence.append(1 if row[15] == "Returning_Visitor" else 0)
            row_evidence.append(1 if row[16] == "TRUE" else 0)

            evidence.append(row_evidence)
            labels.append(row[17])

        return evidence, labels
            

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    x_training, x_testing, y_training, y_testing = train_test_split(evidence, labels, test_size=0.5)

    return model.fit(x_training, y_training)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    for i in range(len(labels)):
        positive = 0
        positive_identified = 0
        negative = 0
        negative_identified = 0

        if labels[i] == 1:
            positive += 1
            # True positive rate
            if predictions[i] == 1:
                positive_identified += 1

        else:
            negative += 1
            if predictions[i] == 0:
                negative_identified += 1

    return positive_identified / positive, negative_identified / negative


if __name__ == "__main__":
    main()
