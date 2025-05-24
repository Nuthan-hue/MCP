# simple_model.py

def predict(input_value: float) -> float:
    """
    A very simple "model" that doubles the input.
    """
    return input_value * 2.0

def get_model_info():
    return {
        "name": "SimpleDoublerModel",
        "version": "1.0.0",
        "type": "hardcoded_rule",
        "description": "A placeholder model that doubles the input numerical value."
    }

if __name__ == "__main__":
    test_input = 5.0
    result = predict(test_input)
    print(f"Input: {test_input}, Output: {result}")