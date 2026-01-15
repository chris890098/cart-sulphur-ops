# Cart Investments Sulphur Ops

A Streamlit-based operations dashboard for managing sulphur cart investments, sales orders, truck trips, and communications.

## Features

- **Dashboard**: Monthly allocation tracking, completed pickups, remaining allocation, and finish-by date monitoring
- **Sales Orders**: Log sales by buyer with transport mode (self vs Cart-managed)
- **Truck Planner**: Plan and track truck trips with driver, truck ID, and status management
- **Comms Log**: Maintain communication history with Sasol, transporters, buyers, and internal teams
- **Settings/Export**: Manage monthly allocations, buyers, transporters, and export data to CSV

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Admin Access

Set an `ADMIN_TOKEN` environment variable to unlock admin pages (Daily Planner, Settings). Without it, only the Dashboard is visible.

```bash
export ADMIN_TOKEN="your-secret-token"
```

## Render Hosting

1. Push this repo to GitHub.
2. In Render, create a new Web Service and connect the repo.
3. Render will pick up `render.yaml` automatically.
4. Add an environment variable `ADMIN_TOKEN` in Render for admin access.

## Database

The app uses SQLite with automatic schema initialization. Database file: `cart_sulphur_ops.db`

## Default Settings

- Monthly allocation: 1250 MT
- Finish-by day: 25th
- Suppliers: Sasol
- Transporters: Reload (default)
- Buyers: Poly (self-transport), Tram (Cart-managed)
