from flask import Flask, render_template, request, jsonify
import random
import string
from collections import defaultdict

app = Flask(__name__)

def generate_password(length=12, options=None):
    if options is None:
        options = {}
    
    # Validate length
    if length < 8:
        return "Password must be at least 8 characters long."
    if length > 32:
        return "Maximum allowed length is 32 characters."

    # Define all possible character sets with their types
    char_sets = {
        'lower': ('abcdefghijklmnopqrstuvwxyz', 'letter'),
        'upper': ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'letter'),
        'digits': ('0123456789', 'digit'),
        'math': ('+-×÷=≠≈<>≤≥', 'symbol'),
        'currency': ('$€¥£¢₽₹', 'symbol'),
        'punctuation': (string.punctuation, 'symbol'),
        'greek': ('αβγδεζηθικλμνξοπρστυφχψω', 'letter'),
        'ascii_art': ('─│┌┐└┘├┤┬┴┼', 'symbol'),
        'brackets': ('()[]{}<>', 'symbol')
    }

    # Determine which character sets to use based on options
    selected_sets = {}
    required_types = set()
    
    # Always include letters (both cases)
    selected_sets['lower'] = char_sets['lower']
    selected_sets['upper'] = char_sets['upper']
    required_types.add('letter')
    
    # Include other sets based on options
    if options.get('use_digits'):
        selected_sets['digits'] = char_sets['digits']
        required_types.add('digit')
    if options.get('use_math_symbols'):
        selected_sets['math'] = char_sets['math']
        required_types.add('symbol')
    if options.get('use_currency'):
        selected_sets['currency'] = char_sets['currency']
        required_types.add('symbol')
    if options.get('use_punctuation'):
        selected_sets['punctuation'] = char_sets['punctuation']
        required_types.add('symbol')
    if options.get('use_greek_letters'):
        selected_sets['greek'] = char_sets['greek']
        required_types.add('letter')
    if options.get('use_ascii_art'):
        selected_sets['ascii_art'] = char_sets['ascii_art']
        required_types.add('symbol')
    if options.get('use_brackets'):
        selected_sets['brackets'] = char_sets['brackets']
        required_types.add('symbol')

    if not selected_sets:
        return "Please select at least one character type."

    # Leet speak substitutions
    leet_mapping = {
        'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7',
        'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5', 'T': '7'
    }

    # Generate password ensuring proper distribution
    password = []
    char_counts = defaultdict(int)
    type_counts = defaultdict(int)
    
    # First pass: include at least one character from each selected set
    for set_name, (chars, char_type) in selected_sets.items():
        char = random.choice(chars)
        
        # Apply leet speak if enabled and applicable
        if options.get('use_leet_speak') and char in leet_mapping and random.random() < 0.3:
            char = leet_mapping[char]
        
        password.append(char)
        char_counts[set_name] += 1
        type_counts[char_type] += 1

    # Second pass: fill remaining length with balanced distribution
    while len(password) < length:
        # Calculate weights for each set based on current distribution
        weights = {}
        total_weight = 0
        for set_name, (chars, char_type) in selected_sets.items():
            # Give higher weight to sets that are underrepresented
            weight = max(1, (len(password) / len(selected_sets)) - char_counts[set_name])
            weights[set_name] = weight
            total_weight += weight
        
        # Select a character set based on weights
        rand = random.uniform(0, total_weight)
        current = 0
        selected_set = None
        for set_name, weight in weights.items():
            current += weight
            if rand <= current:
                selected_set = set_name
                break
        
        if selected_set is None:
            selected_set = random.choice(list(selected_sets.keys()))
        
        # Select a character from the chosen set
        chars, char_type = selected_sets[selected_set]
        char = random.choice(chars)
        
        # Apply leet speak if enabled and applicable
        if options.get('use_leet_speak') and char in leet_mapping and random.random() < 0.3:
            char = leet_mapping[char]
        
        password.append(char)
        char_counts[selected_set] += 1
        type_counts[char_type] += 1

    # Final shuffle to mix everything
    random.shuffle(password)
    
    # Convert to string and ensure exact length
    password_str = ''.join(password)[:length]
    
    # Final validation
    if len(password_str) != length:
        return f"Failed to generate password of length {length}"
    
    return password_str

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        length = int(data.get('length', 12))
        
        # Get all options from the request
        options = {
            'use_digits': bool(data.get('use_digits', False)),
            'use_math_symbols': bool(data.get('use_math_symbols', False)),
            'use_currency': bool(data.get('use_currency', False)),
            'use_punctuation': bool(data.get('use_punctuation', False)),
            'use_greek_letters': bool(data.get('use_greek_letters', False)),
            'use_ascii_art': bool(data.get('use_ascii_art', False)),
            'use_leet_speak': bool(data.get('use_leet_speak', False)),
            'use_brackets': bool(data.get('use_brackets', False))
        }

        password = generate_password(length, options)
        
        if isinstance(password, str) and any(
            password.startswith(prefix) 
            for prefix in ["Password must be", "Please select", "Maximum allowed", "Failed to generate"]
        ):
            return jsonify({'error': password}), 400

        return jsonify({'password': password})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
