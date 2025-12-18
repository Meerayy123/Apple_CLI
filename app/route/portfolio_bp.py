from flask import Blueprint, request
from app.services.portfolio_service import PortfolioService
from app.services.transaction_service import TransactionService
from app.domain.portfolio import Portfolio

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")


def _portfolio_to_dict(p: Portfolio):
    return {"id": p.id, "name": p.name, "user_id": p.user_id}


def _investment_to_dict(inv):
    return {
        "id": inv.id,
        "portfolio_id": inv.portfolio_id,
        "security_id": inv.security_id,
        "quantity": inv.quantity,
        "avg_price": inv.avg_price,
    }


@portfolio_bp.route("/all", methods=["GET"])
def get_all_portfolios():
    try:
        portfolios = PortfolioService.list_portfolios()
        return {"portfolios": [_portfolio_to_dict(p) for p in portfolios]}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@portfolio_bp.route("/<int:portfolio_id>", methods=["GET"])
def get_portfolio_by_id(portfolio_id: int):
    try:
        portfolio = PortfolioService.get_portfolio(portfolio_id)
        if portfolio is None:
            return {"error": "Portfolio not found."}, 404
        return {"portfolio": _portfolio_to_dict(portfolio)}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@portfolio_bp.route("/create", methods=["POST"])
def create_portfolio():
    try:
        data = request.get_json() or {}
        name = data.get("name")

        # No login in this assignment; owner/user must be passed in request. :contentReference[oaicite:5]{index=5}
        user_id = data.get("user_id") or data.get("owner_id")  # support either key
        if user_id is None:
            raise ValueError("user_id is required.")

        portfolio = PortfolioService.create_portfolio(user_id=int(user_id), name=name)
        return {"message": "Portfolio created.", "portfolio": _portfolio_to_dict(portfolio)}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@portfolio_bp.route("/delete/<int:portfolio_id>", methods=["DELETE"])
def delete_portfolio(portfolio_id: int):
    try:
        PortfolioService.delete_portfolio(portfolio_id)
        return {"message": "Portfolio deleted."}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@portfolio_bp.route("/<int:portfolio_id>/add_security", methods=["POST"])
def add_security_to_portfolio(portfolio_id: int):
    """
    Minimum requirement: adding a new security to an existing portfolio. :contentReference[oaicite:6]{index=6}
    """
    try:
        data = request.get_json() or {}

        user_id = data.get("user_id")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        price_override = data.get("price_override")
        notes = data.get("notes")

        if user_id is None:
            raise ValueError("user_id is required.")
        if quantity is None:
            raise ValueError("quantity is required.")

        inv = TransactionService.buy_security(
            user_id=int(user_id),
            portfolio_id=portfolio_id,
            symbol=symbol,
            quantity=float(quantity),
            price_override=(float(price_override) if price_override is not None else None),
            notes=notes,
        )
        return {"message": "Security added to portfolio.", "investment": _investment_to_dict(inv)}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@portfolio_bp.route("/<int:portfolio_id>/harvest", methods=["POST"])
def harvest_investment(portfolio_id: int):
    """
    Minimum requirement: harvesting an investment from an existing portfolio. :contentReference[oaicite:7]{index=7}
    """
    try:
        data = request.get_json() or {}

        user_id = data.get("user_id")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        price_override = data.get("price_override")
        notes = data.get("notes")

        if user_id is None:
            raise ValueError("user_id is required.")
        if quantity is None:
            raise ValueError("quantity is required.")

        TransactionService.sell_security(
            user_id=int(user_id),
            portfolio_id=portfolio_id,
            symbol=symbol,
            quantity=float(quantity),
            price_override=(float(price_override) if price_override is not None else None),
            notes=notes,
        )
        return {"message": "Investment harvested (sold)."}, 200
    except Exception as e:
        return {"error": str(e)}, 400
