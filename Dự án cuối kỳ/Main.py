import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from tsp_solver import TSPSolver


class TSPGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSP Solver - Hill Climbing + Random Restart")
        self.setGeometry(100, 100, 1200, 700)

        self.solver = TSPSolver()
        self.restart_index = 0

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # === Top: SpinBox + Run button ===
        top_layout = QHBoxLayout()
        input_layout = QVBoxLayout()
        self.restart_input = QSpinBox()
        self.restart_input.setRange(1, 99999999)
        self.restart_input.setValue(40)
        self.restart_input.setPrefix("Restarts: ")
        self.restart_input.setFixedWidth(150)

        self.run_button = QPushButton("Run TSP Solver")
        self.run_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.run_button.clicked.connect(self.run_solver)

        input_layout.addWidget(self.restart_input)
        input_layout.addWidget(self.run_button)
        input_layout.addStretch()
        top_layout.addLayout(input_layout)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # === History & Distance Matrix (Left) + Visualization (Right) ===
        content_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        self.route_log = QTableWidget()
        self.route_log.setColumnCount(3)
        self.route_log.setHorizontalHeaderLabels(["Route", "Distance","Iteration"])
        left_layout.addWidget(QLabel("Solution Log"))
        left_layout.addWidget(self.route_log)

        left_layout.addWidget(QLabel("Distance Matrix"))
        self.table = QTableWidget()
        self.table.setRowCount(self.solver.num_campuses)
        self.table.setColumnCount(self.solver.num_campuses)
        self.table.setHorizontalHeaderLabels([c[2] for c in self.solver.campuses])
        self.table.setVerticalHeaderLabels([c[2] for c in self.solver.campuses])
        self.update_distance_table()
        left_layout.addWidget(self.table)
        self.format_tables()

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Visualization"))

        # Tạo layout ngang chứa 2 biểu đồ Distance Distribution và Optimization History
        top_charts_layout = QHBoxLayout()
        self.fig_dist = Figure(figsize=(3, 3))
        self.canvas_dist = FigureCanvas(self.fig_dist)
        top_charts_layout.addWidget(self.canvas_dist)

        self.fig_opt = Figure(figsize=(3, 3))
        self.canvas_opt = FigureCanvas(self.fig_opt)
        top_charts_layout.addWidget(self.canvas_opt)

        right_layout.addLayout(top_charts_layout)  # Thêm layout ngang chứa 2 biểu đồ lên trên

        # Biểu đồ route nằm dưới, chiếm toàn bộ chiều ngang
        self.fig_route = Figure(figsize=(6, 4))
        self.canvas_route = FigureCanvas(self.fig_route)
        right_layout.addWidget(self.canvas_route)

        # Stats
        self.label_best_route = QLabel("Best Route: N/A")
        self.label_best = QLabel("Global Best Length: N/A")
        self.label_mean = QLabel("Mean Length: N/A")
        self.label_std = QLabel("Std. Deviation: N/A")
        for label in [
            self.label_best_route, self.label_best,
            self.label_mean, self.label_std
        ]:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setStyleSheet("font-size: 14px; padding: 4px;")
            right_layout.addWidget(label)

        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)
        main_layout.addLayout(content_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def format_tables(self):
        self.route_log.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.route_log.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.route_log.setAlternatingRowColors(True)
        self.route_log.resizeColumnsToContents()
        self.route_log.horizontalHeader().setStretchLastSection(True)
        self.route_log.setMaximumHeight(250)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMaximumHeight(300)

    def update_distance_table(self):
        for i in range(self.solver.num_campuses):
            for j in range(self.solver.num_campuses):
                self.table.setItem(i, j, QTableWidgetItem(f"{self.solver.distance_matrix[i][j]:.2f}"))

    def update_statistics_labels(self):
        distances = [d for _, d ,_ in self.solver.history]
        if not distances:
            return
        mean = sum(distances) / len(distances)
        std = (sum((x - mean) ** 2 for x in distances) / len(distances)) ** 0.5
        best = self.solver.best_distance
        self.label_best.setText(f"Global Best Length: {best:.4f}")
        self.label_mean.setText(f"Mean Length: {mean:.4f}")
        self.label_std.setText(f"Std. Deviation: {std:.4f}")

    def run_solver(self):
        restarts = self.restart_input.value()
        self.solver.random_restart(restarts)
        self.route_log.setRowCount(0)
        self.restart_index = 0
        self.timer = QTimer(self)
        self.update_route_log()
        self.timer.timeout.connect(self.update_route_animation)
        self.timer.start(250)
        self.animate_route_plot()

    def plot_specific_route(self, route, color="#FF0000"):
        self.fig_route.clear()
        ax = self.fig_route.add_subplot(111)
        x = [self.solver.campuses[i][0] for i in route]
        y = [self.solver.campuses[i][1] for i in route]
        x.append(x[0])
        y.append(y[0])
        ax.plot(x, y, marker='.', linestyle='-', color=color, markersize=6)
        for i in route:
            cx, cy, name = self.solver.campuses[i]
            ax.text(
                cx- 0.4, cy- 0.2, name,                # Dịch vị trí sang phải và lên
                fontsize= 11,
                ha='left',                           # Căn trái để dễ đọc
                color="#000000",                     # Màu chữ dễ nhìn hơn (dark blue)
                 )

        ax.set_title("Route on Map (Current Restart)")
        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.grid(True, linestyle='--', alpha= 1 )
        self.fig_route.tight_layout()
        self.canvas_route.draw()

    def plot_distribution_step(self, index):
        self.fig_dist.clear()
        ax = self.fig_dist.add_subplot(111)
        distances = [d for _, d, _ in self.solver.history[:index + 1]]
        bins = min(len(distances), 10)
        if bins > 0:
            ax.hist(distances, bins=bins, color="skyblue", edgecolor="black")
        ax.set_title("Distance Distribution")
        ax.set_xlabel("Total Distance")
        ax.set_ylabel("Frequency")
        self.fig_dist.tight_layout()
        self.canvas_dist.draw()

    def plot_optimization_step(self, index):
        self.fig_opt.clear()
        ax = self.fig_opt.add_subplot(111)
        distances = [d for _, d,_ in self.solver.history[:index + 1]]
        ax.plot(distances, marker='', linestyle='-', color="red")
        ax.set_title("Optimization History")
        ax.set_xlabel("Restart Iteration")
        ax.set_ylabel("Distance")
        self.fig_opt.tight_layout()
        self.canvas_opt.draw()

    def update_route_log(self):
        self.route_log.setRowCount(len(self.solver.history))
        for i, (route, dist, iteration) in enumerate(self.solver.history):
            route_str = " → ".join([self.solver.campuses[j][2] for j in route])
            self.route_log.setItem(i, 0, QTableWidgetItem(route_str))
            self.route_log.setItem(i, 1, QTableWidgetItem(f"{dist:.4f}"))
            self.route_log.setItem(i, 2, QTableWidgetItem(f"[{iteration} iters] {route_str}"))
        self.route_log.resizeColumnToContents(0)

    def animate_route_plot(self):
        self.restart_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_route_animation)
        self.timer.start(500)

    def update_route_animation(self):
        if self.restart_index < len(self.solver.history):
            route, dist, iteration = self.solver.history[self.restart_index]
            self.plot_specific_route(route)
            self.plot_distribution_step(self.restart_index)
            self.plot_optimization_step(self.restart_index)

            self.route_log.setRowCount(self.restart_index + 1)
            route_str = " → ".join([self.solver.campuses[j][2] for j in route])
            self.route_log.setItem(self.restart_index, 0, QTableWidgetItem(route_str))
            self.route_log.setItem(self.restart_index, 1, QTableWidgetItem(f"{dist:.4f}"))
            self.route_log.setItem(self.restart_index, 2, QTableWidgetItem(str(iteration)))
            self.route_log.resizeColumnToContents(0)

            self.restart_index += 1
        else:
            self.timer.stop()
            best_route = self.solver.history[-1][0]
            self.plot_route_with_color(best_route, color='green')
            self.update_statistics_labels()
            best_route_str = " → ".join([self.solver.campuses[j][2] for j in best_route])
            self.label_best_route.setText(f"Best Route: {best_route_str}")

    def plot_route_with_color(self, route, color='red'):
        self.fig_route.clear()
        ax = self.fig_route.add_subplot(111)
        x = [self.solver.campuses[i][0] for i in route]
        y = [self.solver.campuses[i][1] for i in route]
        x.append(x[0])
        y.append(y[0])
        ax.plot(x, y, marker='.', linestyle='-', color=color, markersize=8)
        for i in route:
            cx, cy, name = self.solver.campuses[i]
            ax.text(
                cx - 0.4, cy - 0.2, name,                # Dịch vị trí sang phải và lên
                fontsize=11,
                ha='left',                           # Căn trái để dễ đọc
                color="#154918",                     # Màu chữ dễ nhìn hơn (dark blue)
                 )
        ax.set_title("Best Route on Map")
        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.grid(True, linestyle='--', alpha= 1)
        self.fig_route.tight_layout()
        self.canvas_route.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TSPGUI()
    window.show()
    sys.exit(app.exec())
