import argparse
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


def train_and_predict(input_file, input_column, output_column, model_type, condition_columns, plot_graph, new_batch_size):
    """
    Train a regression model and make predictions.

    Args:
        input_file (str): Path to the input CSV file.
        input_column (str): Name of the input column.
        output_column (str): Name of the output column.
        model_type (str): Type of regression model to use ('linear', 'ridge', 'lasso', 'random_forest').
        condition_column (dict): Dictionary containing condition columns and their values as key-value pairs.
        plot_graph (bool): Whether to plot the graph of actual vs predicted values.
        new_batch_size (float): New batch size for prediction.

    Returns:
        None
    """
    # Read data from CSV into a DataFrame
    data = pd.read_csv(input_file)

    # Filter data based on condition columns
    for column, value in condition_columns.items():
        if column in data.columns:
            data = data[data[column].astype(str) == value]
        else:
            print(f"WARNING: Condition column '{column}' does not exist in the data.")

    # Remove rows with Nan values in both input and output columns
    data = data.dropna(subset=[input_column, output_column])

    # Extract input and output data
    X = data[[input_column]]    # Input features
    y = data[output_column]     # Output target

    # Check if there is enough data left for training
    if len(X) < 2:
        print("Not enough data for training after applying conditions.")
        return

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Select the regression model based onthe specified type
    if model_type == 'linear':
        model = LinearRegression()
    elif model_type == 'ridge':
        model = Ridge()
    elif model_type == 'lasso':
        model = Lasso()
    elif model_type == 'random_forest':
        model = RandomForestRegressor()
    else:
        print("Invalid model type. Please choose from 'linear', 'ridge', 'lasso', or 'random_forest'. Using Linear Regression as default.")
        model = LinearRegression()  # Default to Linear Regression if invalid model type is specified

    # Fit the selected model
    model.fit(X_train, y_train)

    # Predict throughput for a new batch size
    predicted_throughput = model.predict([[new_batch_size]])

    print("Predicted throughput for batch size {}: {:.2f}".format(new_batch_size, predicted_throughput[0]))

    # Plot the graph if specified
    if plot_graph:
        # Preict throughput for test data
        predicted_throughputs = model.predict(X_test)

        # Plot the predicted vs. actual values for the test data
        plt.scatter(X_test, y_test, color='blue', label='Actual')
        plt.scatter(X_test, predicted_throughputs, color='red', label='Predicted')
        plt.xlabel(input_column)
        plt.ylabel(output_column)
        plt.title('Actual vs Predicted Throughput (Test Data)')
        plt.legend()
        plt.grid(True)
        # plt.show()

        # Save the graph as a PNG file
        plt.savefig('plot.png')

        # Cloe the plot to prevent showing it in the script's output
        plt.close()

        # Display the graph using xdg-open
        # import subprocess
        # subprocess.run(['xdg-open', 'plot.png'])


if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Train a linear regression model and make predictions.')

    # Add arguments with detailed descriptions
    parser.add_argument('-i', '--input_file', type=str, help='path to the input CSV file', required=True)
    parser.add_argument('-c', '--input_column', type=str, help='Name of the input column', required=True)
    parser.add_argument('-o', '--output_column', type=str, help='Name of the output column', required=True)
    parser.add_argument('-m', '--model_type', type=str, help='Type of regression model to use (linear, ridge, lasso, random_forest)', default='linear')
    parser.add_argument('-p', '--plot', action='store_true', help='Plot the graph')
    # Optional condition columns with detailed description
    parser.add_argument('--conditions', nargs='+', type=str, help='List of condition columns in the format colum=value', default=[])
    # New batch size for prediction
    parser.add_argument('-b', '--new_batch_size', type=float, help='New batch size for prediction', required=True)

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Parse the condition columns and values
    condition_columns = {}
    if args.conditions:
        for condition in args.conditions:
            column, value = condition.split('=')
            condition_columns[column] = value

    # Call the train_and_predict function with the parsed arguments
    train_and_predict(args.input_file, args.input_column, args.output_column, args.model_type, condition_columns, args.plot, args.new_batch_size)
