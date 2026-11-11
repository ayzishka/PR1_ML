"""
Практическая работа № 9. Метод опорных векторов (SVM)
Уровень A: сравнение linear и RBF ядер, влияние параметров C и gamma.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

RANDOM_STATE = 42
OUT = Path("results")
OUT.mkdir(exist_ok=True)

# 1. Создаём двумерный учебный датасет.
X, y = make_moons(n_samples=500, noise=0.25, random_state=RANDOM_STATE)

# Одна и та же выборка для всех экспериментов.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
)

def make_model(kernel="rbf", C=1.0, gamma="scale"):
    # Масштабирование выполняется ДО SVM внутри Pipeline.
    return make_pipeline(
        StandardScaler(),
        SVC(kernel=kernel, C=C, gamma=gamma)
    )

def plot_boundary(ax, model, X_all, y_all, title):
    """Рисует точки и границу решения модели."""
    x_min, x_max = X_all[:, 0].min() - 0.7, X_all[:, 0].max() + 0.7
    y_min, y_max = X_all[:, 1].min() - 0.7, X_all[:, 1].max() + 0.7
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 350),
        np.linspace(y_min, y_max, 350)
    )
    grid = np.c_[xx.ravel(), yy.ravel()]
    zz = model.predict(grid).reshape(xx.shape)

    ax.contourf(xx, yy, zz, alpha=0.22, cmap="coolwarm")
    ax.contour(xx, yy, zz, levels=[0.5], colors="black", linewidths=1.4)
    ax.scatter(X_all[:, 0], X_all[:, 1], c=y_all, cmap="coolwarm",
               edgecolors="black", s=24)
    ax.set_title(title)
    ax.set_xlabel("Признак 1")
    ax.set_ylabel("Признак 2")

# 2. Сравниваем линейное и RBF-ядро.
linear_model = make_model(kernel="linear", C=1.0)
rbf_model = make_model(kernel="rbf", C=1.0)

linear_model.fit(X_train, y_train)
rbf_model.fit(X_train, y_train)

linear_pred = linear_model.predict(X_test)
rbf_pred = rbf_model.predict(X_test)

print("СРАВНЕНИЕ ЯДЕР")
print(f"Linear accuracy: {accuracy_score(y_test, linear_pred):.3f}")
print(f"RBF accuracy:    {accuracy_score(y_test, rbf_pred):.3f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
plot_boundary(axes[0], linear_model, X, y, "SVM: linear kernel")
plot_boundary(axes[1], rbf_model, X, y, "SVM: RBF kernel")
fig.suptitle("Сравнение границ решения для разных ядер", fontsize=14)
fig.tight_layout()
fig.savefig(OUT / "svm_kernels.png", dpi=160, bbox_inches="tight")
plt.show()

# 3. Исследуем влияние C на RBF-модель.
C_values = [0.1, 10]
models = []
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

print("\nВЛИЯНИЕ ПАРАМЕТРА C")
for ax, C_value in zip(axes, C_values):
    model = make_model(kernel="rbf", C=C_value)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    score = accuracy_score(y_test, pred)
    print(f"C={C_value}: accuracy={score:.3f}")
    plot_boundary(ax, model, X, y, f"RBF kernel, C={C_value}")
    models.append(model)

fig.suptitle("Как параметр C меняет границу решения", fontsize=14)
fig.tight_layout()
fig.savefig(OUT / "svm_C_comparison.png", dpi=160, bbox_inches="tight")
plt.show()

# 4. Исследуем влияние gamma на RBF-модель.
# gamma определяет, насколько далеко распространяется влияние одной точки.
gamma_values = [0.1, 10]
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

print("\nВЛИЯНИЕ ПАРАМЕТРА GAMMA")
for ax, gamma_value in zip(axes, gamma_values):
    model = make_model(kernel="rbf", C=1.0, gamma=gamma_value)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    score = accuracy_score(y_test, pred)
    print(f"gamma={gamma_value}: accuracy={score:.3f}")
    plot_boundary(ax, model, X, y, f"RBF kernel, gamma={gamma_value}")

fig.suptitle("Как параметр gamma меняет границу решения", fontsize=14)
fig.tight_layout()
fig.savefig(OUT / "svm_gamma_comparison.png", dpi=160, bbox_inches="tight")
plt.show()

# 4. Подробная оценка одной модели.
print("\nCLASSIFICATION REPORT — RBF, C=1")
print(classification_report(y_test, rbf_pred, target_names=["Класс 0", "Класс 1"]))

print("\nВЫВОДЫ")
print("- Linear строит прямую границу; для изогнутых классов может быть недостаточно гибким.")
print("- RBF строит нелинейную границу и лучше подстраивается под форму make_moons.")
print("- Малое C (0.1) сильнее допускает ошибки и стремится к более простой границе.")
print("- Большое C (10) сильнее штрафует ошибки на обучении; граница может стать сложнее.")
print("- gamma управляет радиусом влияния отдельных обучающих точек: большое значение обычно даёт более локальную и сложную границу.")
print("- Масштабирование признаков выполнено через StandardScaler внутри Pipeline.")
