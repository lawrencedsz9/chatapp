# Secure Messaging App with Rail Fence Cipher

A real-time chat application that uses the Rail Fence Cipher encryption technique to secure messages. This project demonstrates a simple implementation of cryptography in communications.

## Features

- Modern Tkinter GUI
- FastAPI backend with WebSockets for real-time communication
- Rail Fence Cipher encryption/decryption
- Adjustable encryption settings (rail count)
- Message decryption tool
- Real-time message updates

## Rail Fence Cipher

The Rail Fence Cipher (also called a Zigzag Cipher) is a simple transposition cipher that arranges plaintext in a zigzag pattern along a set of "rails" and then reads off each rail to produce the ciphertext.

For example, with 3 rails, the message "HELLO WORLD" would be arranged as:

```
H . . . O . . . R . .
. E . L . W . O . L .
. . L . . . . . D . .
```

Reading along each rail gives the ciphertext: "HORDLELWOL"

## Project Structure

```
app/
├── backend/
│   └── main.py         # FastAPI backend with WebSockets
├── common/
│   └── cipher.py       # Rail Fence Cipher implementation
└── frontend/
    └── app.py          # Tkinter GUI
requirements.txt
README.md
```

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

## Usage

1. Launch the frontend application
2. Enter a username and connect to the server
3. Send messages with encryption enabled
4. Adjust rail count to change encryption strength
5. Use the decrypt tool to decrypt messages manually

## Security Considerations

Note that the Rail Fence Cipher is a simple historical cipher and not suitable for truly secure communications. This project is for educational purposes to demonstrate basic encryption concepts.

## License

MIT
