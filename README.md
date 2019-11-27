# Cortex-GUI

#### Homework 5 & 6 CIS 4930 Brain-Computer Interfaces

Program is built using Dash (https://plot.ly/dash/)

The GUI consists of two graphs:

- The first is for channel **AF3**.

- The second is for channel **AF4**.

Graphs are not recording data by default. Click 'Start Recording' button on the right side of screen to begin recording data. After 1 second both graphs will begin to update. 

To isolate one or more traces on the graph, click / double-click on the values in the legend.

To see what each value is at any particular point in time, hover over any of the data points on the graph.

## GUI Screenshots
[GUI Screenshot 1](https://i.imgur.com/6jKRA2e.png)

## Running Instructions

Download and install **Python >= 3.5**

To run this program, first set up a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html) (highly recommended):

- **py -m venv env** *(Windows)* / **python3 -m venv env** *(Linux/Mac)*

Activate the virtual environment:

- **./env/Scripts/activate** (Windows) /**source env/bin/activate** (Linux/Mac)

Install the dependencies:

- **pip install -r requirements.txt**

Then to run the program simply type in a terminal:

- **python app.py**

Go to **localhost:8050** in your internet browser. 

### Members
William Walsh

Erick Orozco

Muhammed Tuzcu

Loubyn Sineus
