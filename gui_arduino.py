from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton,
    QApplication, QFrame
)
from PySide6.QtCore import QSize, QThread, Signal, Slot
from PySide6.QtGui import QFont
import sys
import asyncio
from bt_connection import send_command


class CommandThread(QThread):
    result_signal = Signal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_command(self.command))
        self.result_signal.emit(result)
        loop.close()


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(650, 450))
        self.bt_info = QFrame(self)
        self.schedule = QPushButton(self)
        self.cpu_fan = QPushButton(self)
        self.bt_taillights = QPushButton(self)
        self.bt_front_lights = QPushButton(self)
        self.state_taillights = False
        self.state_front_lights = False
        self.threads = []
        self.schedule_time = None
        self.fan_status = False

        self.bt_frame()
        self.taillights()
        self.front_lights()
        self.bt_schedule()
        self.bt_cpu_fan()

    def bt_cpu_fan(self) -> None:
        self.cpu_fan.setFixedSize(QSize(235, 140))
        self.cpu_fan.setFont(QFont("Arial", 10))
        self.cpu_fan.setText(f"Velocidad: Bajo")
        self.cpu_fan.setStyleSheet("""
            background-color: #28B463;
            border-radius: 10px;
        """)

        def verify_state():
            match self.fan_status:
                case True:
                    self.cpu_fan.setStyleSheet("""
                        background-color: #28B463;
                        border-radius: 10px;
                    """)
                    self.cpu_fan.setText(f"Velocidad FAN: Bajo")
                    self.send_bt_command("6")
                    self.fan_status = False

                case False:
                    self.cpu_fan.setStyleSheet("""
                        background-color: #E74C3C;
                        border-radius: 10px;
                    """)
                    self.cpu_fan.setText(f"Velocidad FAN: Alto")
                    self.send_bt_command("5")
                    self.fan_status = True

        self.cpu_fan.move(410, 300)
        self.cpu_fan.clicked.connect(lambda: verify_state())

    def bt_schedule(self) -> None:
        self.schedule.setFixedSize(QSize(400, 140))
        self.schedule.setFont(QFont("Arial", 10))
        self.schedule.setText(f"Horario: {self.schedule_time}")
        self.schedule.setStyleSheet("""
            background-color: #EC7063;
            border-radius: 10px;
        """)

        def verify_schedule():
            match self.schedule_time:
                case "T":
                    self.schedule.setStyleSheet("""
                        background-color: #F5B041;
                        border-radius: 10px;
                    """)
                    self.schedule.setText("Horario: Tarde")

                case "D":
                    self.schedule.setStyleSheet("""
                        background-color: #F4D03F;
                        border-radius: 10px;
                    """)
                    self.schedule.setText("Horario: Día")

                case "N":
                    self.schedule.setStyleSheet("""
                        background-color: #17202A;
                        border-radius: 10px;
                    """)
                    self.schedule.setText("Horario: Noche")

        self.schedule.move(5, 300)
        self.schedule.clicked.connect(lambda: verify_schedule())

    def bt_frame(self) -> None:
        name_bt = QLabel(self)
        name_bt.setFixedSize(QSize(700, 60))
        name_bt.setText("""
        Device: BT04-A                                         Permission: 0000FFE2-0000-1000-8000-00805F9B34FB 

        MAC-ADDRESS: 98:DA:BE:01:8D:A7
        """)
        name_bt.setStyleSheet("color: white;")
        name_bt.setFont(QFont("Arial", 10))
        name_bt.move(0, 5)

        self.bt_info.setFixedSize(640, 80)
        self.bt_info.setStyleSheet("""
            background-color: #2e2e2e;
            border-radius: 10px;
        """)
        self.bt_info.move(5, 0)

    def taillights(self) -> None:
        self.bt_taillights.setFixedSize(QSize(317, 200))
        self.bt_taillights.setText("Activar luces traseras")
        self.bt_taillights.setFont(QFont("Arial", 20))
        self.bt_taillights.setStyleSheet("""
            background-color: #34495E;
            border-radius: 10px;
        """)

        def verify_lights() -> None:
            if self.state_taillights:
                self.bt_taillights.setStyleSheet("""
                    background-color: #34495E;
                    border-radius: 10px;
                """)
                self.bt_taillights.setText("Activar luces traseras")
                self.state_taillights = False
                self.send_bt_command("4")

            else:
                self.bt_taillights.setStyleSheet("""
                    background-color: #F7DC6F;
                    border-radius: 10px;
                """)
                self.bt_taillights.setText("Desactivar luces traseras")
                self.state_taillights = True
                self.send_bt_command("3")

        self.bt_taillights.move(5, 90)
        self.bt_taillights.clicked.connect(lambda: verify_lights())

    def front_lights(self) -> None:
        self.bt_front_lights.setFixedSize(QSize(317, 200))
        self.bt_front_lights.setFont(QFont("Arial", 20))
        self.bt_front_lights.setText("Activar luces delanteras")
        self.bt_front_lights.setStyleSheet("""
            background-color: #34495E;
            border-radius: 10px;
        """)

        def verify_lights() -> None:
            if self.state_front_lights:
                self.bt_front_lights.setStyleSheet("""
                    background-color: #34495E;
                    border-radius: 10px;
                """)
                self.bt_front_lights.setText("Activar luces delanteras")
                self.state_front_lights = False
                self.send_bt_command("2")
            else:
                self.bt_front_lights.setStyleSheet("""
                    background-color: #F7DC6F;
                    border-radius: 10px;
                """)
                self.bt_front_lights.setText("Desactivar luces delanteras")
                self.state_front_lights = True
                self.send_bt_command("1")

        self.bt_front_lights.move(327, 90)
        self.bt_front_lights.clicked.connect(lambda: verify_lights())

    def send_bt_command(self, command):
        thread = CommandThread(command)
        thread.result_signal.connect(self.handle_result)
        thread.finished.connect(lambda: self.threads.remove(thread))
        self.threads.append(thread)
        thread.start()

    @Slot(str)
    def handle_result(self, result):
        self.schedule_time = result
        self.schedule.click()


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
