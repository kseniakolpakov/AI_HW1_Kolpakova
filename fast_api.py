from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import io
import uvicorn
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
import re

app = FastAPI()

class Item(BaseModel):
    name: str
    year: int
    # selling_price: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float


class Items(BaseModel):
    objects: List[Item]


app = FastAPI()

PATH = 'pipeline.pkl'


def load_pipeline() -> Pipeline:
    try:
        pipeline = joblib.load(PATH)
        return pipeline
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки модели: {str(e)}")


def extract_name(row):
    row['brand'] = " ".join(row['name'].split()[:1])
    row['model'] = " ".join(row['name'].split()[1:2])
    return row


def make_new_features(df):
    df['mileage'] = pd.to_numeric(df['mileage'].str.extract(r'([\d.]+)')[0], errors='coerce')
    df['engine'] = pd.to_numeric(df['engine'].str.extract(r'(\d+)')[0], errors='coerce')
    df['max_power'] = pd.to_numeric(df['max_power'].str.extract(r'(\d+)')[0], errors='coerce')
    df = df.apply(extract_name, axis=1).drop(columns=['name'])
    df = df.apply(extract_torque, axis=1)
    return df.fillna(0)  # Заполняем пропущенные значения нулями

def extract_torque(row):
  if pd.notnull(row['torque']):
    torque_str = str(row['torque'].lower().replace(',', ''))
  else:
    torque_str = ''
  torque_filter = re.search(r"([\d.]+)\s*(nm|kgm)", torque_str)
  if torque_filter:
    torque = float(torque_filter.group(1))
    torque_mu = torque_filter.group(2)
    if torque_mu == 'kgm':
      torque *= 9.8
  else:
    torque = None
  rpm_filter = re.search(r"(\d+)(?:-|–| to )(\d+)?\s*rpm", torque_str)
  if rpm_filter:
    max_rpm = int(rpm_filter.group(2) or rpm_filter.group(1))
  else:
    max_rpm = None
  row['torque'] = torque
  row['max_torque_rpm'] = max_rpm
  return row


def predict_price(features: dict) -> float:
    # feature_values = [
    #       [
    #           features["name"],
    #           features["year"],
    #           features["km_driven"],
    #           features["fuel"],
    #           features["seller_type"],
    #           features["transmission"],
    #           features["owner"],
    #           features["mileage"],
    #           features["engine"],
    #           features["max_power"],
    #           features["torque"],
    #           features["seats"]
    #       ]
    #   ]
    # column_names = [key for key in features.keys()]
    # df = pd.DataFrame(feature_values, columns=column_names)
    df = pd.DataFrame([features])

    df = make_new_features(df)

    pipeline = load_pipeline()

    prediction = pipeline.predict(df)[0]

    return float(prediction)


@app.post("/predict_item")
def predict_item(item_data: dict) -> float:
    try:
        item = Item(**item_data)  # Проверяем валидность данных через Pydantic
        prediction = predict_price(item.dict())
        return prediction
    except Exception as e:
        print(f"Ошибка предсказания: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_items")
async def predict_items(file: UploadFile):
    try:
        contents = await file.read()

        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        required_columns = {"name", "year", "km_driven", "fuel", "seller_type",
                            "transmission", "owner", "mileage", "engine",
                            "max_power", "torque", "seats"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail="в CSV-файле отсутсвуют необходимые признаки")

        df["predicted_price"] = df.apply(lambda row: predict_price(row.to_dict()), axis=1)

        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)

        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv"
                                     )

        response.headers["Content-Disposition"] = "attachment; filename=result.csv"

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# if __name__ == "__main__":
#     item_data = {
#         "name": "Mahindra Xylo E4 BS IV",
#         "year": 2010,
#         "km_driven": 168000,
#         "fuel": "Diesel",
#         "seller_type": "Individual",
#         "transmission": "Manual",
#         "owner": "First Owner",
#         "mileage": "14.0 kmpl",
#         "engine": "2498 CC",
#         "max_power": "112 bhp",
#         "torque": "260 Nm at 1800-2200 rpm",
#         "seats": 7.0
#     }
#     prediction = predict_item(item_data)
#     print(prediction)