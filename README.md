# Portfolio CLI – Assignment 1

- Console-only CLI using `rich`
- Login/logout; tracks current user in `db.py`
- Manage Users (admin-only): view/add/delete (blocked if user has portfolios)
- Manage Portfolios: view/create (with immediate initial buys), delete (empty only),
  harvest (partial/full), liquidate-all
- Marketplace: view securities & buy; balance checks
- Auto portfolio IDs via `db.next_portfolio_id`
- Friendly errors; no crashes
- Structure: `app/cli`, `app/domain`, `app/services`, `db.py`, `main.py`
- Run: `python -m main`
