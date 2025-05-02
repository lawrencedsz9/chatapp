"""
Custom implementation of the Rail Fence Cipher for the secure messaging app.
This provides a backup implementation if the original doesn't work properly.
"""

def encrypt_message(text, rails):
    """
    Encrypt a message using the Rail Fence Cipher
    
    Args:
        text (str): The plaintext message to encrypt
        rails (int): The number of rails (rows) to use for encryption
    
    Returns:
        str: The encrypted message
    """
    if rails <= 1 or rails >= len(text):
        return text
    
    # Initialize the fence (matrix)
    fence = [[] for _ in range(rails)]
    
    # Direction of movement on the fence
    rail = 0
    direction = 1  # 1 for moving down, -1 for moving up
    
    # Populate the fence with characters
    for char in text:
        fence[rail].append(char)
        
        # Change direction when we hit the top or bottom rail
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
            
        rail += direction
    
    # Read off the fence to get the ciphertext
    ciphertext = ''.join([''.join(rail_chars) for rail_chars in fence])
    
    return ciphertext

def decrypt_message(ciphertext, rails):
    """
    Decrypt a message that was encrypted using the Rail Fence Cipher
    
    Args:
        ciphertext (str): The encrypted message
        rails (int): The number of rails (rows) used for encryption
    
    Returns:
        str: The decrypted message (plaintext)
    """
    if rails <= 1 or rails >= len(ciphertext):
        return ciphertext
    
    # Create a rails x len(ciphertext) matrix filled with placeholders
    fence = [[None for _ in range(len(ciphertext))] for _ in range(rails)]
    
    # Mark positions where characters would go with 'x'
    rail, direction = 0, 1
    for i in range(len(ciphertext)):
        fence[rail][i] = 'x'
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    # Fill in the fence with the ciphertext characters
    index = 0
    for i in range(rails):
        for j in range(len(ciphertext)):
            if fence[i][j] == 'x' and index < len(ciphertext):
                fence[i][j] = ciphertext[index]
                index += 1
    
    # Read off the fence in zig-zag order to get the plaintext
    result = []
    rail, direction = 0, 1
    for i in range(len(ciphertext)):
        result.append(fence[rail][i])
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    return ''.join(result)

def visualize_encryption(text, rails):
    """
    Create a visual representation of the encryption process
    
    Args:
        text (str): The plaintext message
        rails (int): The number of rails
        
    Returns:
        str: A string showing the rail fence pattern
    """
    if rails <= 1 or rails >= len(text):
        return text
    
    # Create the fence (matrix)
    fence = [[' ' for _ in range(len(text))] for _ in range(rails)]
    
    # Fill the fence with characters in zig-zag pattern
    rail, direction = 0, 1
    for i, char in enumerate(text):
        fence[rail][i] = char
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    # Format the fence for display
    return '\n'.join([''.join(row) for row in fence])

def visualize_decryption(ciphertext, rails):
    """
    Create a visual representation of the decryption process
    
    Args:
        ciphertext (str): The encrypted message
        rails (int): The number of rails
        
    Returns:
        str: A string showing the rail fence pattern with the ciphertext
    """
    if rails <= 1 or rails >= len(ciphertext):
        return ciphertext
    
    # Create a rails x len(ciphertext) matrix filled with spaces
    fence = [[' ' for _ in range(len(ciphertext))] for _ in range(rails)]
    
    # Mark the pattern
    rail, direction = 0, 1
    for i in range(len(ciphertext)):
        fence[rail][i] = 'x'
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    # Count the number of characters in each rail
    counts = [row.count('x') for row in fence]
    
    # Fill in the fence with the ciphertext
    index = 0
    for rail in range(rails):
        for col in range(len(ciphertext)):
            if fence[rail][col] == 'x':
                if index < len(ciphertext):
                    fence[rail][col] = ciphertext[index]
                    index += 1
    
    return '\n'.join([''.join(row) for row in fence]) 