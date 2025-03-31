from flask import Flask, render_template, request, jsonify
import random
import string
import secrets
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for development

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_password():
    data = request.get_json()
    
    try:
        length = int(data.get('length', 16))
        uppercase = bool(data.get('uppercase', True))
        lowercase = bool(data.get('lowercase', True))
        numbers = bool(data.get('numbers', True))
        symbols = bool(data.get('symbols', True))
        
        # Validate length
        if length < 8 or length > 64:
            return jsonify({
                'error': 'Password length must be between 8 and 64 characters',
                'status': 'error'
            }), 400
        
        # Validate at least one character type is selected
        if not any([uppercase, lowercase, numbers, symbols]):
            return jsonify({
                'error': 'Please select at least one character type',
                'status': 'error'
            }), 400
        
        # Define character sets
        char_sets = []
        if uppercase:
            char_sets.append(string.ascii_uppercase)
        if lowercase:
            char_sets.append(string.ascii_lowercase)
        if numbers:
            char_sets.append(string.digits)
        if symbols:
            char_sets.append('!@#$%^&*()_+-=[]{}|;:,.<>?')
        
        # Ensure at least one character from each selected set is included
        password = []
        for char_set in char_sets:
            password.append(secrets.choice(char_set))
        
        # Fill the rest of the password
        all_chars = ''.join(char_sets)
        password.extend(secrets.choice(all_chars) for _ in range(length - len(password)))
        
        # Shuffle the password
        random.shuffle(password)
        password = ''.join(password)
        
        # Calculate password strength
        strength = calculate_strength(password)
        
        return jsonify({
            'password': password,
            'status': 'success',
            'strength': strength
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def calculate_strength(password):
    """Calculate password strength metrics"""
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    
    # Complexity score (0-100)
    complexity = 0
    
    # Length contributes up to 50 points
    complexity += min(50, (length / 64) * 50)
    
    # Character variety contributes up to 50 points
    variety_score = 0
    if has_upper: variety_score += 10
    if has_lower: variety_score += 10
    if has_digit: variety_score += 10
    if has_symbol: variety_score += 20
    
    complexity += variety_score
    
    # Cap at 100
    complexity = min(100, complexity)
    
    # Determine strength level
    if complexity < 30:
        strength_level = 'Weak'
    elif complexity < 70:
        strength_level = 'Moderate'
    else:
        strength_level = 'Strong'
    
    return {
        'score': complexity,
        'level': strength_level
    }

if __name__ == '__main__':
    app.run(debug=True)