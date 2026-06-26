# Demo Script

Use this script to present the project to a recruiter or a potential client.

## 1. Introduction (The Problem)
"I built this Telegram Booking Bot to help small local businesses like barbershops or salons. Many of them still take appointments manually via phone or WhatsApp, which is disorganized. This bot provides a structured, automated way to collect booking requests 24/7."

## 2. Live Demo (The User Experience)
*Open Telegram and start the bot.*
- **Step 1**: "Notice how the bot welcomes the user and immediately offers a call to action: 'Записаться'."
- **Step 2**: "The flow is guided. I chose Inline Buttons for services to minimize typing errors."
- **Step 3**: "For the phone number, I implemented both manual entry and the 'Share Contact' feature for convenience."
- **Step 4**: "At the end, the user sees a summary. This reduces mistakes before the data hits the database."

## 3. The Admin Perspective (The Business Value)
- "Once confirmed, the bot doesn't just save the data; it notifies the business owner immediately."
- *Show the Admin message.*
- "I implemented interactive buttons for the admin. By clicking 'Accept', the status is updated in the SQLite database without the admin needing to open any dashboard."

## 4. Technical Highlights (The Code)
- **FSM (Finite State Machine)**: "I used `aiogram`'s FSM to manage the multi-step conversation, ensuring the bot knows exactly what data it's waiting for."
- **Dependency Injection**: "The bot uses modern DI patterns to pass settings and database connections to handlers, making the code testable."
- **Validation**: "I used Regex and custom logic to ensure we don't get junk data in the database."
- **Testing**: "The project includes unit tests for the core logic, ensuring reliability."

## 5. Limitations & Future Scope
- **Polling**: "Currently, it runs on Long Polling for simplicity, but it's ready to be switched to Webhooks for high-load production."
- **SQLite**: "I used SQLite for this demo as it's zero-config, but the repository pattern I used makes it easy to swap for PostgreSQL."
- **Notifications**: "In a production version, I would add a notification back to the user when the admin accepts their booking."

---

## Key Points to Emphasize
- **Reliability**: Data is saved before notification.
- **Simplicity**: No complex UI, just Telegram.
- **Clean Code**: SOLID principles, Repository pattern.
