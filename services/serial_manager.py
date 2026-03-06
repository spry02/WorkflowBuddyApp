import serial
import serial.tools.list_ports
from typing import Optional
import time
import threading as th
import eel

class SerialManager:
    _instance = None

    def __new__(cls, data_service):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def __init__(self, data_service):
        self.connection: Optional[serial.Serial] = None
        self.port: Optional[str] = None
        self.status: Optional[str] = None
        self.data = data_service

        self._controller_thread: Optional[th.Thread] = th.Thread(target=self.connection_controller, daemon=True)
        self._controller_thread.start()

        self._reader_thread: Optional[th.Thread] = None
        self._running = False
        
        self._initialized = True

    def connection_controller(self) -> bool:
        self.find_esp()
        while True:
            if self.connection:
                connected_ports = []
                for port in serial.tools.list_ports.comports():
                    connected_ports.append(port.device)
                
                if not self.port in connected_ports:
                    self.status = "dropped"
                    eel.setConnection({"connected": False, "comport": "dropped"})
                    self.disconnect()
            else:
                self.find_esp()
            time.sleep(.01)
            
    def find_esp(self) -> Optional[str]:
        """Find ESP32 device"""
        while self.port is None:
            ports = serial.tools.list_ports.comports()
            for port_info in ports:
                if ("USB-SERIAL CH340" in port_info.description):
                    try:
                        print("Checking port:", port_info.device)
                        ser = serial.Serial(port_info.device, 115200, timeout=1)
                        print("Opened port:", port_info.device)
                        ser.write("\n".encode())
                        line = ser.readline().decode(errors="ignore").strip()
                        ser.close()

                        if (line=="#ESP32_WORKFLOWBUDDY_READY"):
                            self.connect(port_info.device)
                            return port_info.device
                    except Exception as e:
                        print(e)
            print("WorkflowBuddy not detected! Retrying in 5 seconds...")
            time.sleep(5)
    
    def connect(self, port: str) -> bool:
        """Connect to ESP32 device over Serial"""
        try:
            self.connection=serial.Serial(port, 115200, timeout=1)
            self.port = port
            self.status = "connected"
            eel.setConnection({"connected": True, "comport": self.connection.port})
            self.start_reader()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def start_reader(self):
        self._running = True
        self._reader_thread = th.Thread(target=self._reader, daemon=True)
        self._reader_thread.start()

    def stop_reader(self):
        self._running = False
        self._reader_thread.join()

    def disconnect(self):
        self._running = False
        if self._reader_thread:
            self.stop_reader()
        if self.connection and self.connection.is_open:
            self.connection.close()
        if self.status != "dropped":
            eel.setConnection({"connected": False, "comport": "disconnected"})

        self.connection = None
        self.port = None
    
    def _reader(self):
        while self._running:
            try:
                if self.connection.in_waiting:
                    data = self.connection.readline().decode(errors='ignore').strip()

                    if data.startswith("btn"):
                        print(f"Pressed: {data}")
                        from models import ButtonClass
                        button = ButtonClass(button_id=data, data_service=self.data)
                        button.execute()
                    else:
                        print(f"Received: {data}")
            except Exception as e:
                print(e)
                break
