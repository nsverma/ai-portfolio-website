from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.demos import exports, registry

router = APIRouter(prefix="/api/demos", tags=["demos"])


class PredictRequest(BaseModel):
    inputs: dict


@router.get("")
def list_demos():
    return {"slugs": sorted(registry.DEMOS.keys())}


@router.get("/{slug}")
def get_demo(slug: str):
    schema = registry.get_schema(slug)
    if schema is None:
        raise HTTPException(status_code=404, detail="No live demo for this project")
    return schema


@router.get("/{slug}/dataset")
def download_dataset(slug: str):
    if not exports.has_dataset(slug):
        raise HTTPException(status_code=404, detail="No dataset export for this project")
    try:
        filename, csv_text = exports.build(slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{slug}/predict")
def predict(slug: str, body: PredictRequest):
    try:
        return registry.run_predict(slug, body.inputs)
    except KeyError:
        raise HTTPException(status_code=404, detail="No live demo for this project")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
