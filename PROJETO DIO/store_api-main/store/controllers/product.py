from typing import List

from database import get_db
from fastapi import (APIRouter, Body, Depends, HTTPException, Path, Query,
                     status)
from pydantic import UUID4
from sqlalchemy.orm import Session
from store.core.exceptions import NotFoundException
from store.schemas.product import (ProductIn, ProductOut, ProductUpdate,
                                   ProductUpdateOut)
from store.usecases.product import ProductUsecase

from .services import create_produto, get_produtos_por_preco, update_produto

router = APIRouter(tags=["products"])


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
    return await usecase.create(body=body)


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query()


@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    return await usecase.update(id=id, body=body)


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


router = APIRouter()

@router.post("/produtos")
def create_produto_endpoint(nome: str, preco: int, db: Session = Depends(get_db)):
    try:
        produto = create_produto(db, nome, preco)
        return {
            "success": True,
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "preco": produto.preco
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.patch("/produtos/{produto_id}")
def update_produto_endpoint(
    produto_id: int,
    nome: str = None,
    preco: int = None,
    updated_at: datetime = None,
    db: Session = Depends(get_db)
):
    try:
        produto = update_produto(db, produto_id, nome, preco, updated_at)
        return {
            "success": True,
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "preco": produto.preco,
                "updated_at": produto.updated_at
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "não encontrado" in str(e) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.get("/produtos/filtro")
def produtos_filtrados(preco_min: int = Query(None), preco_max: int = Query(None), db: Session = Depends(get_db)):
    produtos = get_produtos_por_preco(db, preco_min, preco_max)
    return {
        "success": True,
        "produtos": [
            {"id": p.id, "nome": p.nome, "preco": p.preco, "updated_at": p.updated_at} for p in produtos
        ]
    }