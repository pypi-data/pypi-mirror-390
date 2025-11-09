from fastapi import FastAPI, UploadFile, Form
import pandas as pd
from io import StringIO
from topsisx.pipeline import DecisionPipeline
from topsisx.reports import generate_report

app = FastAPI()

@app.post("/decision/")
async def decision_api(
    file: UploadFile,
    weights: str = Form("entropy"),
    method: str = Form("topsis"),
    impacts: str = Form("+,-"),
    report: bool = Form(False)
):
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))

    pipe = DecisionPipeline(weights=weights, method=method)
    result = pipe.run(df.iloc[:, 1:], impacts=impacts.split(","))
    
    if report:
        generate_report(result, method=method)

    return {"status": "success", "method": method, "weights": weights, "result": result.to_dict()}
