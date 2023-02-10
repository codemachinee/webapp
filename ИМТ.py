import pywebio
from pywebio.input import input, FLOAT
from pywebio.output import put_text


def bmi():
    height = input("Введите рост(cm)：", type=FLOAT)
    weight = input("Введите вес(kg)：", type=FLOAT)

    BMI = weight / (height / 100) ** 2

    top_status = [(16, 'Критический недостаток в весе'), (18.5, 'недостаток в весе'),
                  (25, 'Нормальный вес'), (30, 'Избыточный вес'),
                  (35, 'Умеренное ожирение'), (float('inf'), 'Сильное ожирение')]

    for top, status in top_status:
        if BMI <= top:
            put_text('Ваш ИМТ: %.1f. Category: %s' % (BMI, status))
            break


if __name__ == '__main__':
    pywebio.start_server(bmi, port=80)