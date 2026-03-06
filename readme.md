# WorkflowBuddyApp 
---

## Stack technologiczny
### Backend:
* Python
* eel
* webview
* pyserial
* threading
* numpy
* pyautogui
* keyboard
* os
* sys
* Pillow

---

### Frontend:
* HTML
* CSS
* JavaScript
* jQuery

---

## Założenia projektu
Utworzenie aplikacji do projektu inżynierskiego, ułatwiającego ergonomiczną pracę przy komputerze. Aplikacja łączyć ma się z ESP32 przez port Serial, umożliwia konfigurację dotykowych przycisków, które znajdują się na dotykowym wyświetlaczu. Po dotknięciu przycisku wykonuje na komputerze akcję przypisaną do niego.

Aplikacja dodatkowo ma samodzielnie szukać podłączonego ESP32, jeśli nie znajdzie urządzenia ponawia próbę za 5 sekund. W przypadku utraty połączenia również próbuje połączyć się ponownie.