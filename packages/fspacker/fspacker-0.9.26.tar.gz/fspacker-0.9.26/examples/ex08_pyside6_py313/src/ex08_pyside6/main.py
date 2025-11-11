from platform import python_version
from random import randint

from PySide6 import __version__
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


def main() -> None:
    app = QApplication([])

    win = QWidget()

    layout = QVBoxLayout()
    label = QLabel(
        f"Hello, PySide6!\nPySide6 ver: {__version__}\n"
        f"Python ver: {python_version()}",
    )
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    btn = QPushButton(text="PUSH ME")
    layout.addWidget(btn)

    bar = QProgressBar(value=50)
    layout.addWidget(bar)
    bar.valueChanged.connect(
        lambda: bar.setValue(0 if bar.value() >= 95 else bar.value()),  # noqa: PLR2004
    )

    # 模拟进度条
    timer = QTimer()
    timer.timeout.connect(lambda: bar.setValue(bar.value() + randint(1, 5)))
    timer.start(30)

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
