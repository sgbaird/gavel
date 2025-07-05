#!/usr/bin/env python3
"""
Simple test script to run Gavel for testing markdown functionality.
This bypasses some dependencies like Celery and Flask-Assets that aren't needed for basic testing.
"""

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# Add the current directory to the path so we can import gavel modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import template filter dependencies and create our filter
import markdown
import html

@app.template_filter('markdown')
def _jinja2_filter_markdown(text):
    if text is None:
        return ''
    # Escape HTML to prevent XSS attacks before processing markdown
    escaped_text = html.escape(text)
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['nl2br'])
    html_output = md.convert(escaped_text)
    return html_output

# Define simple models for testing
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, name, location, description):
        self.name = name
        self.location = location
        self.description = description

# Routes
@app.route('/')
def index():
    items = Item.query.filter_by(active=True).all()
    return render_template('test_index.html', items=items)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('test_item.html', item=item)

@app.route('/admin')
def admin():
    items = Item.query.all()
    return render_template('test_admin.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        
        item = Item(name=name, location=location, description=description)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('test_add_item.html')

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add some test data with markdown if there are no items
        if Item.query.count() == 0:
            print("Adding test data with markdown...")
            
            test_items = [
                Item(
                    name="AI Chatbot",
                    location="Building A, Room 101",
                    description="""# AI Chatbot Project

This is a **smart** chatbot with advanced features:

## Key Features
- *Natural Language Processing* capabilities
- Multi-language support  
- Real-time conversation
- Machine learning integration

### Technical Details
- Built with `Python` and `TensorFlow`
- Uses **BERT** for language understanding
- RESTful API with `Flask`

> This project demonstrates cutting-edge AI technology.

Visit our [documentation](https://example.com/docs) for more details!"""
                ),
                Item(
                    name="E-commerce Platform",
                    location="Building B, Room 205",
                    description="""# Modern E-commerce Solution

A **full-stack** e-commerce platform built for scalability.

## Features
1. User authentication & authorization
2. Product catalog with search
3. Shopping cart functionality
4. Payment processing integration
5. Order management system

### Technology Stack
- **Frontend**: React.js, TypeScript
- **Backend**: Node.js, Express
- **Database**: PostgreSQL
- **Payment**: Stripe API

```javascript
// Example API endpoint
app.get('/api/products', async (req, res) => {
  const products = await Product.findAll();
  res.json(products);
});
```

*Perfect for modern businesses!*"""
                ),
                Item(
                    name="Simple Weather App",
                    location="Building C, Room 301",
                    description="A basic weather application that displays current weather conditions. Built with vanilla JavaScript and OpenWeatherMap API."
                ),
                Item(
                    name="Data Visualization Dashboard",
                    location="Building D, Room 150",
                    description="""# Interactive Data Dashboard

## Overview
This dashboard provides **real-time** data visualization for business metrics.

### Supported Chart Types
- Line charts for trends
- Bar charts for comparisons  
- Pie charts for distributions
- Heat maps for correlations

#### Technologies Used
- `D3.js` for visualizations
- **React** for UI components
- *WebSocket* for real-time updates

| Feature | Status |
|---------|--------|
| Real-time updates | ✅ |
| Export to PDF | ✅ |
| Custom themes | 🚧 |

> "Data is the new oil" - But only if you can visualize it effectively!"""
                )
            ]
            
            for item in test_items:
                db.session.add(item)
            
            db.session.commit()
            print("Test data added successfully!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)