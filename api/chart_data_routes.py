"""
Chart Data API Routes

Handles saving and loading chart data edits for interactive editor.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any

chart_data_bp = Blueprint('chart_data', __name__)


@chart_data_bp.route('/api/charts/update-data', methods=['POST'])
def update_chart_data():
    """
    Save edited chart data to database.

    Request Body:
    {
        "chart_id": "line-chart-abc123",
        "presentation_id": "presentation-uuid",
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [125000, 145000, 178000, 195000],
        "timestamp": "2025-01-15T10:30:00Z"
    }

    Response:
    {
        "success": true,
        "message": "Chart data updated successfully",
        "chart_id": "line-chart-abc123",
        "updated_at": "2025-01-15T10:30:00Z"
    }
    """
    try:
        data = request.json

        # Validate required fields
        required_fields = ['chart_id', 'presentation_id', 'labels', 'values']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        chart_id = data['chart_id']
        presentation_id = data['presentation_id']
        labels = data['labels']
        values = data['values']

        # Validate data types
        if not isinstance(labels, list) or not isinstance(values, list):
            return jsonify({
                'success': False,
                'error': 'Labels and values must be arrays'
            }), 400

        # Validate equal length
        if len(labels) != len(values):
            return jsonify({
                'success': False,
                'error': f'Labels ({len(labels)}) and values ({len(values)}) must have same length'
            }), 400

        # Import database model
        try:
            from models.chart_data import ChartData
            from extensions import db
        except ImportError:
            # Database not configured - return success but don't save
            print("⚠️ Database not configured, returning success without saving")
            return jsonify({
                'success': True,
                'message': 'Chart data received (database not configured)',
                'chart_id': chart_id,
                'updated_at': datetime.utcnow().isoformat()
            }), 200

        # Find existing record or create new
        existing = ChartData.query.filter_by(
            chart_id=chart_id,
            presentation_id=presentation_id
        ).first()

        if existing:
            # Update existing record
            existing.labels = labels
            existing.values = values
            existing.updated_at = datetime.utcnow()
            print(f"✅ Updated existing chart data: {chart_id}")
        else:
            # Create new record
            new_record = ChartData(
                chart_id=chart_id,
                presentation_id=presentation_id,
                labels=labels,
                values=values,
                updated_at=datetime.utcnow()
            )
            db.session.add(new_record)
            print(f"✅ Created new chart data record: {chart_id}")

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chart data updated successfully',
            'chart_id': chart_id,
            'presentation_id': presentation_id,
            'updated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        print(f"❌ Error updating chart data: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chart_data_bp.route('/api/charts/get-data/<presentation_id>', methods=['GET'])
def get_chart_data(presentation_id: str):
    """
    Get all saved chart data for a presentation.

    Response:
    {
        "success": true,
        "charts": [
            {
                "chart_id": "line-chart-abc123",
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "values": [125000, 145000, 178000, 195000],
                "updated_at": "2025-01-15T10:30:00Z"
            },
            ...
        ]
    }
    """
    try:
        # Import database model
        try:
            from models.chart_data import ChartData
        except ImportError:
            # Database not configured
            print("⚠️ Database not configured, returning empty charts list")
            return jsonify({
                'success': True,
                'charts': []
            }), 200

        # Query all chart data for this presentation
        charts = ChartData.query.filter_by(
            presentation_id=presentation_id
        ).all()

        chart_data_list = [
            {
                'chart_id': chart.chart_id,
                'labels': chart.labels,
                'values': chart.values,
                'updated_at': chart.updated_at.isoformat() if chart.updated_at else None
            }
            for chart in charts
        ]

        print(f"✅ Retrieved {len(chart_data_list)} charts for presentation {presentation_id}")

        return jsonify({
            'success': True,
            'presentation_id': presentation_id,
            'charts': chart_data_list
        }), 200

    except Exception as e:
        print(f"❌ Error fetching chart data: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chart_data_bp.route('/api/charts/delete-data', methods=['DELETE'])
def delete_chart_data():
    """
    Delete chart data for a specific chart.

    Request Body:
    {
        "chart_id": "line-chart-abc123",
        "presentation_id": "presentation-uuid"
    }

    Response:
    {
        "success": true,
        "message": "Chart data deleted successfully"
    }
    """
    try:
        data = request.json

        chart_id = data.get('chart_id')
        presentation_id = data.get('presentation_id')

        if not chart_id or not presentation_id:
            return jsonify({
                'success': False,
                'error': 'chart_id and presentation_id are required'
            }), 400

        # Import database model
        try:
            from models.chart_data import ChartData
            from extensions import db
        except ImportError:
            # Database not configured
            return jsonify({
                'success': True,
                'message': 'Chart data deleted (database not configured)'
            }), 200

        # Find and delete record
        record = ChartData.query.filter_by(
            chart_id=chart_id,
            presentation_id=presentation_id
        ).first()

        if record:
            db.session.delete(record)
            db.session.commit()
            print(f"✅ Deleted chart data: {chart_id}")
        else:
            print(f"⚠️ Chart data not found: {chart_id}")

        return jsonify({
            'success': True,
            'message': 'Chart data deleted successfully'
        }), 200

    except Exception as e:
        print(f"❌ Error deleting chart data: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
