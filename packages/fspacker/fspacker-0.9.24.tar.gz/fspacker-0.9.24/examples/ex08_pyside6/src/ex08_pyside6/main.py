from platform import python_version

from PySide6 import __version__
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


def main() -> None:
    app = QApplication([])

    win = QWidget()

    layout = QVBoxLayout()
    label = QLabel(
        f"Hello, PySide6!\nPySide6 ver: {__version__}\nPython ver: {python_version()}",
    )
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    btn = QPushButton(text="PUSH ME")
    layout.addWidget(btn)

    win.setLayout(layout)
    win.resize(400, 300)

    btn.clicked.connect(
        lambda: [
            print("exit"),  # noqa: T201
            win.close(),
        ],
    )

    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
