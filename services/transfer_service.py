import time
import os
from services import SerialManager

class FileTransferService:
    def __init__(self, serial_manager):
        self.serial_manager: SerialManager = serial_manager
        
    def _writer(self, command: str, data_path: str):
        if self.serial_manager._reader_thread.is_alive():
            self.serial_manager.stop_reader()
        self.send_command(command)
        if self.wait_for_ready():
            self.send_data(data_path)

        self.serial_manager.start_reader()

    def send_command(self, command: str):
        self.serial_manager.connection.write((command+"\n").encode())

    def wait_for_ready(self) -> bool:
        start_time = time.time()
        while time.time() - start_time < 10:
            line = self.serial_manager.connection.readline().decode(errors='ignore').strip()
            if not line:
                continue
            print("ESP:", line)
            if line == "READY":
                return True
        return False

    def _clear_send(self, button_id: str):
        print(button_id)
        try:
            self.serial_manager.connection.write(f"{button_id}\n".encode())
            time.sleep(0.01)

            start_time = time.time()
            while time.time() - start_time < 10:
                line = self.serial_manager.connection.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                print(f"ESP: {line}")
                if line == "OK":
                    break
                elif line.startswith("ERR"):
                    raise RuntimeError("ESP32 reported error: " + line)
            else:
                raise RuntimeError("No OK from ESP32")
            
            start_done = time.time()
            while time.time() - start_done < 10:
                line = self.serial_manager.connection.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                print(f"ESP: {line}")
                if line == "DONE":
                    break
                elif line.startswith("ERR"):
                    raise RuntimeError("ESP32 reported error: " + line)
        except Exception as e:
            print(f"Error while clearing button {button_id}: {e}")

    def clear_button(self, button_id: str):
        if self.serial_manager._reader_thread.is_alive():
            self.serial_manager.stop_reader()
        self.send_command("clear")
        if self.wait_for_ready():
            self._clear_send(button_id)

        self.serial_manager.start_reader()

    def clear_all_buttons(self):
        button_list = ['btn1-1', 'btn1-2', 'btn1-3', 'btn2-1', 'btn2-2', 'btn2-3']
        for id in button_list:
            if self.serial_manager._reader_thread.is_alive():
                self.serial_manager.stop_reader()
                self.send_command("")
            time.sleep(.05)
            self.send_command("clear")
            if self.wait_for_ready():
                self._clear_send(id)

        self.serial_manager.start_reader()
    
    def send_data(self, data_path: str):
        filename = os.path.basename(data_path)
        filesize = os.path.getsize(data_path)
        filetype = None
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            filetype = 'image'
        elif filename.endswith('.txt'):
            filetype = 'text'

        try:
            if filetype is not None:
                self.serial_manager.connection.write(f"FILENAME:{filename}\n".encode())
                time.sleep(.01)
                self.serial_manager.connection.write(f"SIZE:{filesize}\n".encode())
                time.sleep(.01)
                self.serial_manager.connection.write(b"START\n")
                self.serial_manager.connection.flush()

                start_time = time.time()
                while time.time() - start_time < 10:
                    line = self.serial_manager.connection.readline().decode(errors='ignore').strip()
                    if not line:
                        continue
                    print(f"ESP: {line}")
                    if line == "OK":
                        break
                    elif line.startswith("ERR"):
                        raise RuntimeError("ESP32 reported error: " + line)
                else:
                    raise RuntimeError("No OK from ESP32")
                
                sent = 0
                with open(data_path, "rb") as f:
                    while sent < filesize:
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        self.serial_manager.connection.write(chunk)
                        self.serial_manager.connection.flush()
                        
                        start_ack = time.time()
                        acked = False

                        while time.time() - start_ack < 10:
                            line = self.serial_manager.connection.readline().decode(errors='ignore').strip()
                            if not line:
                                continue
                            print(f"ESP: {line}")
                            if line == "ACK":
                                acked = True
                                break
                            elif line.startswith("ERR"):
                                raise RuntimeError("ESP32 reported error: " + line)
                            elif line == "DONE":
                                acked = True
                                break

                        if not acked:
                            raise RuntimeError("No ACK from ESP32")
                        sent += len(chunk)
                        print(f"Progress: {sent}/{filesize} bytes")

                start_done = time.time()
                while time.time() - start_done < 10:
                    line = self.serial_manager.connection.readline().decode(errors='ignore').strip()
                    if not line:
                        continue
                    print(f"ESP: {line}")
                    if line == "DONE":
                        break
                    elif line.startswith("ERR"):
                        raise RuntimeError("ESP32 reported error: " + line)

        except Exception as e:
            print(f"Error occured while sending data: {e}")
                