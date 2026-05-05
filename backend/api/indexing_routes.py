"""
Indexing and Knowledge Graph API Endpoints
"""

from flask import Blueprint, request, jsonify
import os
from ..indexing import (
    ProjectIndexer,
    Graphify,
    AICodingAssistant,
    IndexStorage,
)

indexing_bp = Blueprint('indexing', __name__, url_prefix='/api/indexing')


@indexing_bp.route('/index', methods=['POST'])
def index_project():
    """Index the entire project"""
    try:
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        indexer = ProjectIndexer(project_root)
        index_data = indexer.index_project()
        
        storage = IndexStorage()
        index_name = (
            request.json.get("name", "default") if request.json else "default"
        )
        storage.save_index(index_data, index_name)
        
        return jsonify({
            'success': True,
            'message': 'Project indexed successfully',
            'index_name': index_name
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@indexing_bp.route('/graph/build', methods=['POST'])
def build_knowledge_graph():
    """Build knowledge graph from indexed project"""
    try:
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        indexer = ProjectIndexer(project_root)
        indexer.index_project()
        
        graphify = Graphify(indexer)
        graph = graphify.build_graph()
        
        storage = IndexStorage()
        graph_name = (
            request.json.get("graph_name", "default_graph")
            if request.json
            else "default_graph"
        )
        storage.save_knowledge_graph(graph, graph_name)
        
        return jsonify({
            'success': True,
            'message': 'Knowledge graph built successfully',
            'graph_name': graph_name,
            'nodes': len(getattr(graph, 'nodes', {}) or {}),
            'edges': len(getattr(graph, 'edges', []) or []),
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@indexing_bp.route('/graph/list', methods=['GET'])
def list_graphs():
    """List all knowledge graphs"""
    try:
        storage = IndexStorage()
        graphs = storage.list_graphs()
        return jsonify({'success': True, 'graphs': graphs}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@indexing_bp.route('/assistant/health', methods=['GET'])
def project_health():
    """Get project health report"""
    try:
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        indexer = ProjectIndexer(project_root)
        graph_name = request.args.get('graph_name', 'default_graph')

        storage = IndexStorage()
        graph = storage.load_knowledge_graph(graph_name)
        if not graph:
            indexer.index_project()
            graphify = Graphify(indexer)
            graph = graphify.build_graph()

        assistant = AICodingAssistant(graph, indexer)
        health = assistant.get_project_health_report()
        
        return jsonify({'success': True, 'health': health}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@indexing_bp.route('/status', methods=['GET'])
def indexing_status():
    """Get indexing system status"""
    return jsonify({
        'success': True,
        'status': 'operational'
    }), 200


def register_indexing_routes(app):
    """Register indexing routes with Flask app"""
    app.register_blueprint(indexing_bp)
