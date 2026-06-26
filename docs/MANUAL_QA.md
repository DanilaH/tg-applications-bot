# Manual QA Checklist

This document provides a guide for manual testing of the Telegram Booking Bot to ensure it behaves correctly in a live environment.

## 1. User Booking Flow
- [ ] Send `/start`: Bot greets the user and shows the "Записаться" button.
- [ ] Click **"Записаться"**: Bot shows the list of services (Haircut, etc.).
- [ ] Select a service: Bot asks for the user's name.
- [ ] Enter name (e.g., "John"): Bot asks for the phone number.
- [ ] Enter phone via text (e.g., `+79991234567`): Bot asks for a comment.
- [ ] Click **"Пропустить"** (Skip): Bot shows the final summary.
- [ ] Click **"Подтвердить"**: Bot says "Заявка отправлена" and returns to the main menu.

## 2. Admin Interaction Flow
- [ ] Submit a booking as a user.
- [ ] Verify Admin receives a notification message with correct details.
- [ ] Click **"Принять"** (Accept) as Admin:
    - [ ] Message markup (buttons) disappears.
    - [ ] Admin gets a confirmation: "Заявка #X принята."
- [ ] Click **"Отклонить"** (Decline) as Admin (on a new booking):
    - [ ] Message markup (buttons) disappears.
    - [ ] Admin gets a confirmation: "Заявка #Y отклонена."

## 3. Input Validation & Edge Cases
- [ ] **Name Validation**:
    - [ ] Try sending a 1-character name: Bot should ask to try again.
    - [ ] Try sending a very long name (>80 chars): Bot should ask to try again.
- [ ] **Phone Validation**:
    - [ ] Try sending an invalid phone number (e.g., "abc"): Bot should show an error message.
    - [ ] Use the **"Отправить телефон"** button: Bot should correctly process the shared contact.
- [ ] **Comment Validation**:
    - [ ] Try sending a comment > 500 characters: Bot should ask to shorten it.
- [ ] **Navigation**:
    - [ ] Click **"Отмена"** (Cancel) during any step: Bot should return to the main menu and clear the state.
    - [ ] Click **"Заполнить заново"** (Restart) on the summary screen: Bot should return to service selection.

## 4. SQLite Storage Verification
*Requires access to the server/local machine.*
- [ ] Submit a booking.
- [ ] Open the database (e.g., using `sqlite3 data/bookings.sqlite3`).
- [ ] Run `SELECT * FROM bookings;`:
    - [ ] Verify the new record exists.
    - [ ] Verify the status is `new` initially.
- [ ] Accept/Decline the booking in Telegram.
- [ ] Run `SELECT status FROM bookings WHERE id = X;`:
    - [ ] Verify the status updated to `accepted` or `declined`.

## 5. Security & Environment
- [ ] Verify that non-admin users *cannot* trigger admin actions (if they somehow get the callback data).
- [ ] Verify that `.env` is not in the git history.
- [ ] Verify that `data/` directory is ignored by git.
