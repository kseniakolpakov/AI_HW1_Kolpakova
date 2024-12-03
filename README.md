# AI_HW1_Kolpakova

## Описание работы сервиса с FastAPI

1. Первый метод POST отвечает за предсказывание цены одного автомобиля (в формате json подаются признаки одного объекта, на выходе сервис выдает предсказанную стоимость машины). Для тестирования в swagger передали следующее тело запроса:
```
{
  "name": "Mahindra Xylo E4 BS IV",
  "year": 2010,
  "km_driven": 168000,
  "fuel": "Diesel",
  "seller_type": "Individual",
  "transmission": "Manual",
  "owner": "First Owner",
  "mileage": "14.0 kmpl",
  "engine": "2498 CC",
  "max_power": "112 bhp",
  "torque": "260 Nm at 1800-2200 rpm",
  "seats": 7.0
}
```
Результат его выполнения:
<img width="1512" alt="Снимок экрана 2024-12-03 в 11 33 43" src="https://github.com/user-attachments/assets/d3295006-4aeb-4861-be5c-a359504665a4">

2. Второй метод POST отвечает за предсказание цены нескольких автомобилей (на вход подается csv-файл с признаками тестовых объектов, на выходе получаем файл с +1 столбцом - предсказаниями на этих объектах). Для тестирования данного метода был сделан датасет, состоящий из 5 объектов - test.csv (https://github.com/kseniakolpakov/AI_HW1_Kolpakova/blob/main/test.csv), на выходе получили result.csv файл (https://github.com/kseniakolpakov/AI_HW1_Kolpakova/blob/main/result.csv). Ниже приведен скриншот выполненя данной операции в Swagger:

<img width="1503" alt="Снимок экрана 2024-12-03 в 11 42 21" src="https://github.com/user-attachments/assets/a337cd4d-1ac2-41ad-bc85-dc549bfabcf5">


