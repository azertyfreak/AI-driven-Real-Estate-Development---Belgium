"""
Belgian Housing AI - REST API
Simplified Flask API for GitHub deployment
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = "belgian_housing_full.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    """Execute database query"""
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'name': 'Belgian Housing AI API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'municipalities': '/api/municipalities',
            'municipality': '/api/municipalities/<nis_code>',
            'predictions': '/api/predictions/<nis_code>',
            'search': '/api/search?q=<query>',
            'stats': '/api/stats'
        }
    })

@app.route('/api/health')
def health():
    """Health check"""
    try:
        count = query_db('SELECT COUNT(*) as count FROM municipalities', one=True)
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'municipalities_count': count['count'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/municipalities')
def get_municipalities():
    """Get all municipalities"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query = f"""
        SELECT nis_code, name_nl, name_fr, province, region, 
               population, density
        FROM municipalities
        ORDER BY population DESC
        LIMIT ? OFFSET ?
    """
    
    rows = query_db(query, (limit, offset))
    municipalities = [dict(row) for row in rows]
    
    total = query_db('SELECT COUNT(*) as total FROM municipalities', one=True)
    
    return jsonify({
        'success': True,
        'total': total['total'],
        'count': len(municipalities),
        'data': municipalities
    })

@app.route('/api/municipalities/<nis_code>')
def get_municipality(nis_code):
    """Get specific municipality"""
    mun = query_db(
        'SELECT * FROM municipalities WHERE nis_code = ?',
        (nis_code,),
        one=True
    )
    
    if not mun:
        return jsonify({
            'success': False,
            'error': f'Municipality {nis_code} not found'
        }), 404
    
    pred = query_db(
        'SELECT * FROM apartment_predictions WHERE nis_code = ?',
        (nis_code,),
        one=True
    )
    
    return jsonify({
        'success': True,
        'data': {
            'municipality': dict(mun),
            'prediction': dict(pred) if pred else None
        }
    })

@app.route('/api/predictions/<nis_code>')
def get_prediction(nis_code):
    """Get AI prediction for municipality"""
    query = """
        SELECT 
            m.nis_code, m.name_nl, m.region, m.population, m.density,
            p.studio_demand_pct, p.one_bed_demand_pct, p.two_bed_demand_pct,
            p.confidence_score, p.market_trend
        FROM municipalities m
        LEFT JOIN apartment_predictions p ON m.nis_code = p.nis_code
        WHERE m.nis_code = ?
    """
    
    result = query_db(query, (nis_code,), one=True)
    
    if not result:
        return jsonify({
            'success': False,
            'error': f'No data for {nis_code}'
        }), 404
    
    return jsonify({
        'success': True,
        'data': dict(result)
    })

@app.route('/api/search')
def search():
    """Search municipalities"""
    q = request.args.get('q', '')
    
    if len(q) < 2:
        return jsonify({
            'success': False,
            'error': 'Query must be at least 2 characters'
        }), 400
    
    query = """
        SELECT nis_code, name_nl, name_fr, region, population, density
        FROM municipalities
        WHERE name_nl LIKE ? OR name_fr LIKE ?
        ORDER BY population DESC
        LIMIT 20
    """
    
    results = query_db(query, (f'%{q}%', f'%{q}%'))
    
    return jsonify({
        'success': True,
        'query': q,
        'count': len(results),
        'data': [dict(row) for row in results]
    })

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    
    # Region stats
    region_query = """
        SELECT 
            region,
            COUNT(*) as count,
            SUM(population) as total_pop,
            AVG(density) as avg_density,
            AVG(p.studio_demand_pct) as avg_studio,
            AVG(p.one_bed_demand_pct) as avg_one_bed,
            AVG(p.two_bed_demand_pct) as avg_two_bed
        FROM municipalities m
        LEFT JOIN apartment_predictions p ON m.nis_code = p.nis_code
        GROUP BY region
    """
    
    regions = query_db(region_query)
    
    # Top cities
    top_query = """
        SELECT nis_code, name_nl, region, population, density
        FROM municipalities
        ORDER BY population DESC
        LIMIT 10
    """
    
    top_cities = query_db(top_query)
    
    # General stats
    general = query_db("""
        SELECT 
            COUNT(*) as total_municipalities,
            SUM(population) as total_population,
            AVG(density) as avg_density
        FROM municipalities
    """, one=True)
    
    return jsonify({
        'success': True,
        'data': {
            'general': dict(general),
            'by_region': [dict(row) for row in regions],
            'top_10_cities': [dict(row) for row in top_cities]
        }
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 BELGIAN HOUSING AI - REST API")
    print("=" * 70)
    print(f"💾 Database: {DB_PATH}")
    print(f"🌐 Server: http://0.0.0.0:5000")
    print("=" * 70)
    print("\n📋 Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/municipalities")
    print("  GET  /api/municipalities/<nis>")
    print("  GET  /api/predictions/<nis>")
    print("  GET  /api/search?q=<query>")
    print("  GET  /api/stats")
    print("\n🔥 Server starting...\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
