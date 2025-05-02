# Secure Messaging App with Rail Fence Cipher

A real-time chat application that uses the Rail Fence Cipher encryption technique to secure messages. This project demonstrates a simple implementation of cryptography in communications.

## Rail Fence Cipher

The Rail Fence Cipher (also called a Zigzag Cipher) is a simple transposition cipher that arranges plaintext in a zigzag pattern along a set of "rails" and then reads off each rail to produce the ciphertext.

For example, with 3 rails, the message "HELLO WORLD" would be arranged as:

```
H . . . O . . . R . .
. E . L . W . O . L .
. . L . . . . . D . .
```

Reading along each rail gives the ciphertext: "HORDLELWOL"

## Setup & Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the backend server:
   ```
   uvicorn app.backend.main:app --reload
   ```

2. Start the frontend application:
   ```
   python app/frontend/app.py
   ```

