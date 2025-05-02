def encrypt(text, rails):
    """
    Encrypt a message using the Rail Fence Cipher
    
    Args:
        text (str): The plaintext message to encrypt
        rails (int): The number of rails (rows) to use for encryption
    
    Returns:
        str: The encrypted message
    """
    if rails <= 1:
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
    ciphertext = ''
    for rail_chars in fence:
        ciphertext += ''.join(rail_chars)
    
    return ciphertext

def decrypt(ciphertext, rails):
    """
    Decrypt a message that was encrypted using the Rail Fence Cipher
    
    Args:
        ciphertext (str): The encrypted message
        rails (int): The number of rails (rows) used for encryption
    
    Returns:
        str: The decrypted message (plaintext)
    """
    if rails <= 1:
        return ciphertext
    
    # Calculate the positions where characters would be placed in the fence
    fence_positions = []
    rail = 0
    direction = 1
    
    for i in range(len(ciphertext)):
        fence_positions.append((rail, i))
        
        # Change direction when we hit the top or bottom rail
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
            
        rail += direction
    
    # Sort positions by rail to get the order in which the characters appear in the ciphertext
    fence_positions.sort()
    
    # Substitute characters back into their original positions
    result = [''] * len(ciphertext)
    for position, char in zip(fence_positions, ciphertext):
        rail, index = position
        result[index] = char
    
    return ''.join(result)
