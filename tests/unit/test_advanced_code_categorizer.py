import unittest
from utils.advanced_code_categorizer import AdvancedCodeCategorizer

class TestAdvancedCodeCategorizer(unittest.TestCase):
    """Test cases for the AdvancedCodeCategorizer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.categorizer = AdvancedCodeCategorizer()
    
    def test_data_analysis_categorization(self):
        """Test categorization of data analysis code."""
        code = """
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('data.csv')

# Analyze data
summary = df.describe()
print(summary)

# Create visualization
plt.figure(figsize=(10, 6))
df['value'].plot(kind='hist')
plt.title('Distribution of Values')
plt.savefig('histogram.png')
"""
        category, confidence, scores = self.categorizer.categorize(code)
        self.assertEqual(category, "data_analysis")
        self.assertGreater(confidence, 0.5)
    
    def test_web_development_categorization(self):
        """Test categorization of web development code."""
        code = """
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['POST'])
def api_data():
    data = request.json
    return {'status': 'success', 'received': data}

if __name__ == '__main__':
    app.run(debug=True)
"""
        category, confidence, scores = self.categorizer.categorize(code)
        self.assertEqual(category, "web_development")
        self.assertGreater(confidence, 0.5)
    
    def test_machine_learning_categorization(self):
        """Test categorization of machine learning code."""
        code = """
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Prepare data
X = np.random.rand(100, 5)
y = np.random.randint(0, 2, 100)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy:.2f}")
"""
        category, confidence, scores = self.categorizer.categorize(code)
        self.assertEqual(category, "machine_learning")
        self.assertGreater(confidence, 0.5)
    
    def test_general_utility_categorization(self):
        """Test categorization of general utility code."""
        code = """
def greet(name):
    return f"Hello, {name}!"

def calculate_average(numbers):
    return sum(numbers) / len(numbers)

def is_palindrome(text):
    text = text.lower().replace(" ", "")
    return text == text[::-1]

print(greet("World"))
print(calculate_average([1, 2, 3, 4, 5]))
print(is_palindrome("A man a plan a canal Panama"))
"""
        category, confidence, scores = self.categorizer.categorize(code)
        # This could be categorized as "general" or "algorithms" depending on implementation
        self.assertIn(category, ["general", "algorithms"])
    
    def test_multiple_categories(self):
        """Test getting multiple category suggestions."""
        code = """
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Load and prepare data
df = pd.read_csv('data.csv')
X = df[['feature1', 'feature2']]
y = df['target']

# Train model
model = LinearRegression()
model.fit(X, y)

# Visualize results
plt.scatter(df['feature1'], y)
plt.plot(df['feature1'], model.predict(X), color='red')
plt.title('Linear Regression Model')
plt.savefig('model.png')
"""
        suggestions = self.categorizer.get_category_suggestions(code, top_n=3)
        categories = [cat for cat, _ in suggestions]
        
        # Should suggest both data_analysis and machine_learning
        self.assertTrue(
            ("data_analysis" in categories and "machine_learning" in categories) or
            ("data_analysis" in categories and "data_analysis" == suggestions[0][0])
        )

if __name__ == '__main__':
    unittest.main()
