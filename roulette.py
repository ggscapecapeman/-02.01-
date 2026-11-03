"""Симуляция европейской рулетки с подсчётом выигрышей и проигрышей.

Режимы запуска:
    python roulette.py                      - интерактивная игра
    python roulette.py --auto 20 --seed 1   - автоматическая симуляция
"""
import argparse
import random
from datetime import datetime

RED = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
PAYOUT_NUMBER = 35   # выплата за ставку на число (35 к 1)
PAYOUT_COLOR = 1     # выплата за ставку на цвет (1 к 1)
MIN_BET = 10
MAX_BET = 1000


def color_of(number):
    """Возвращает цвет ячейки: 'зелёное', 'красное' или 'чёрное'."""
    if number == 0:
        return "зелёное"
    return "красное" if number in RED else "чёрное"


def spin(rng):
    """Вращение колеса: случайное число от 0 до 36."""
    return rng.randint(0, 36)


def check_bet(kind, value, amount, balance):
    """Проверка ставки. Возвращает текст ошибки или None."""
    if amount < MIN_BET or amount > MAX_BET:
        return f"Ставка должна быть от {MIN_BET} до {MAX_BET}"
    if amount > balance:
        return "Ставка больше баланса"
    if kind == "number" and not (isinstance(value, int) and 0 <= value <= 36):
        return "Число должно быть от 0 до 36"
    if kind == "color" and value not in ("красное", "чёрное"):
        return "Цвет: красное или чёрное"
    if kind not in ("number", "color"):
        return "Неизвестный тип ставки"
    return None


def settle(kind, value, amount, number):
    """Результат раунда: изменение баланса (+ выигрыш, - проигрыш)."""
    if kind == "number":
        win = value == number
        payout = PAYOUT_NUMBER
    else:
        win = value == color_of(number)
        payout = PAYOUT_COLOR
    return amount * payout if win else -amount


def format_money(x):
    """Денежный формат: два знака после запятой и суффикс 'р'."""
    return f"{x:,.2f}".replace(",", " ").replace(".", ",") + "р"


def make_report(player, start, balance, history, finished):
    """Итоговый отчёт об игре в виде списка строк."""
    wins = sum(1 for h in history if h["delta"] > 0)
    losses = len(history) - wins
    won = sum(h["delta"] for h in history if h["delta"] > 0)
    lost = -sum(h["delta"] for h in history if h["delta"] < 0)
    return [
        "=== ОТЧЕТ ОБ ИГРЕ ===",
        f"Игрок: {player}",
        f"Раундов: {len(history)}",
        f"Выигрышей: {wins}, проигрышей: {losses}",
        f"Выиграно: {format_money(won)}",
        f"Проиграно: {format_money(lost)}",
        f"Баланс в начале: {format_money(start)}",
        f"ИТОГО: {format_money(balance)}",
        f"Время завершения: {finished:%d.%m.%Y %H:%M}",
    ]


def play_round(rng, balance, kind, value, amount, history):
    """Один раунд: проверка, вращение, расчёт. Возвращает новый баланс."""
    error = check_bet(kind, value, amount, balance)
    if error:
        print("Ошибка:", error)
        return balance
    number = spin(rng)
    delta = settle(kind, value, amount, number)
    balance += delta
    history.append({"number": number, "delta": delta})
    word = "Выигрыш" if delta > 0 else "Проигрыш"
    print(f"Выпало {number} ({color_of(number)}). {word}: "
          f"{format_money(abs(delta))}. Баланс: {format_money(balance)}")
    return balance


def auto_game(rng, start, rounds):
    """Автоматическая игра: случайные ставки на число и на цвет."""
    balance, history = start, []
    for _ in range(rounds):
        if balance < MIN_BET:
            print("Средств недостаточно, игра остановлена")
            break
        amount = rng.choice([10, 50, 100])
        if rng.random() < 0.3:
            kind, value = "number", rng.randint(0, 36)
        else:
            kind, value = "color", rng.choice(["красное", "чёрное"])
        balance = play_round(rng, balance, kind, value, amount, history)
    return balance, history


def interactive_game(rng, start):
    """Интерактивная игра: ввод ставок с клавиатуры."""
    balance, history = start, []
    print(f"Баланс: {format_money(balance)}. Ставка: число/цвет, 'q' - выход")
    while balance >= MIN_BET:
        kind = input("Тип ставки (число/цвет/q): ").strip().lower()
        if kind == "q":
            break
        try:
            if kind == "число":
                value, k = int(input("Число 0-36: ")), "number"
            elif kind == "цвет":
                value, k = input("красное/чёрное: ").strip().lower(), "color"
            else:
                print("Введите: число, цвет или q")
                continue
            amount = int(input("Сумма ставки: "))
        except ValueError:
            print("Ошибка: нужно ввести целое число")
            continue
        balance = play_round(rng, balance, k, value, amount, history)
    return balance, history


def main():
    parser = argparse.ArgumentParser(description="Симуляция рулетки")
    parser.add_argument("--auto", type=int, metavar="N", help="сыграть N раундов автоматически")
    parser.add_argument("--seed", type=int, help="начальное значение генератора")
    parser.add_argument("--balance", type=int, default=1000, help="начальный баланс")
    parser.add_argument("--name", default="Макс", help="имя игрока")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    if args.auto:
        balance, history = auto_game(rng, args.balance, args.auto)
    else:
        balance, history = interactive_game(rng, args.balance)
    print()
    for line in make_report(args.name, args.balance, balance, history, datetime.now()):
        print(line)


if __name__ == "__main__":
    main()
