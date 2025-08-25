from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Produto


#CREATE
def create_produto(db: Session, nome: str, preco: int):
    # Validação de preço positivo
    if preco <= 0:
        raise ValueError("O preço do produto inserido deve ser maior que zero.")

    novo_produto = Produto(nome=nome, preco=preco)
    db.add(novo_produto)
    try:
        db.commit()
        db.refresh(novo_produto)
        return novo_produto
    except IntegrityError:
        db.rollback()  # evita inconsistência do banco
        raise ValueError(f"Produto'{nome}' já existe!")
    
#UPDATE
def update_produto(db: Session, produto_id: int, nome: str = None, preco: int = None, updated_at: datetime = None):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise ValueError(f"Produto com id {produto_id} não encontrado.")

    if nome:
        produto.nome = nome
    if preco is not None:
        if preco <= 0:
            raise ValueError("O preço do produto inserido deve ser maior que zero.")
        produto.preco = preco

    # Atualiza updated_at com a hora atual se não for passado
    produto.updated_at = updated_at if updated_at else datetime.utcnow()

    try:
        db.commit()
        db.refresh(produto)
        return produto
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Já existe um produto com o nome '{nome}'.")


#Filtro para preços maior que 5mil e menor que 8mil
def get_produtos_por_preco(db: Session, preco_min: int = None, preco_max: int = None):
    query = db.query(Produto)
    
    if preco_min is not None:
        query = query.filter(Produto.preco > preco_min)
    if preco_max is not None:
        query = query.filter(Produto.preco < preco_max)
    
    return query.all()