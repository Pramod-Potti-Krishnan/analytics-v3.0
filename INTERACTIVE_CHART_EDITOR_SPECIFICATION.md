# Interactive Chart Data Editor - Feature Specification

**Date**: 2025-01-15
**Feature**: Real-time chart data editing with database persistence
**Status**: 📋 SPECIFICATION COMPLETE - Ready for implementation

---

## User Requirements

1. ✅ **Button on each slide with a chart** - "Edit Data" button appears on chart slides
2. ✅ **Save back to database** - Edits persist across sessions
3. ✅ **Edit both X and Y axis** - Labels and values both editable
4. ✅ **Modal popup overlay** - Clean popup interface for editing

---

## Feature Overview

### User Flow

1. User views presentation with chart
2. User clicks **"📊 Edit Data"** button (appears on hover or always visible)
3. Modal popup opens showing editable data table
4. User edits:
   - X-axis labels (Q1 → "January 2024")
   - Y-axis values (125000 → 130000)
   - Add/remove rows
5. User clicks **"Save & Update"**
6. Chart updates instantly with new data
7. Changes saved to database
8. Modal closes

---

## Frontend Implementation

### 1. Edit Button (Per Chart)

**Add to each chart container**:
```html
<div class="chart-container" data-chart-id="line-chart-abc123">
  <!-- Existing chart canvas -->
  <canvas id="line-chart-abc123" data-chart="line" height="600">
  <!--
  {...chart config...}
  -->
  </canvas>

  <!-- NEW: Edit Data Button -->
  <button class="chart-edit-btn"
          data-chart-id="line-chart-abc123"
          title="Edit chart data">
    📊 Edit Data
  </button>
</div>
```

**CSS for button**:
```css
.chart-edit-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  z-index: 100;
  transition: all 0.2s;
}

.chart-edit-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.05);
}

.chart-container {
  position: relative;
}
```

### 2. Modal Popup

**HTML structure**:
```html
<!-- Modal Overlay -->
<div id="chart-data-modal" class="modal-overlay" style="display:none;">
  <div class="modal-content">
    <!-- Modal Header -->
    <div class="modal-header">
      <h2>📊 Edit Chart Data</h2>
      <button class="modal-close">&times;</button>
    </div>

    <!-- Modal Body -->
    <div class="modal-body">
      <div class="chart-info">
        <p><strong>Chart:</strong> <span id="modal-chart-name">Revenue Growth</span></p>
        <p><strong>Type:</strong> <span id="modal-chart-type">Line Chart</span></p>
      </div>

      <!-- Editable Data Table -->
      <div class="table-container">
        <table id="chart-data-table" class="editable-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Label (X-axis)</th>
              <th>Value (Y-axis)</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="data-table-body">
            <!-- Rows populated dynamically -->
            <tr data-row-index="0">
              <td>1</td>
              <td><input type="text" class="label-input" value="Q1 2024"></td>
              <td><input type="number" class="value-input" value="125000"></td>
              <td><button class="delete-row-btn">🗑️</button></td>
            </tr>
            <tr data-row-index="1">
              <td>2</td>
              <td><input type="text" class="label-input" value="Q2 2024"></td>
              <td><input type="number" class="value-input" value="145000"></td>
              <td><button class="delete-row-btn">🗑️</button></td>
            </tr>
            <!-- More rows... -->
          </tbody>
        </table>
      </div>

      <button id="add-row-btn" class="secondary-btn">+ Add Row</button>
    </div>

    <!-- Modal Footer -->
    <div class="modal-footer">
      <button id="cancel-btn" class="secondary-btn">Cancel</button>
      <button id="save-update-btn" class="primary-btn">💾 Save & Update Chart</button>
    </div>
  </div>
</div>
```

**CSS for modal**:
```css
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

/* Modal Content */
.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  font-size: 32px;
  color: #666;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
}

.modal-close:hover {
  color: #333;
}

/* Modal Body */
.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.chart-info {
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.chart-info p {
  margin: 4px 0;
  font-size: 14px;
}

/* Editable Table */
.table-container {
  overflow-x: auto;
  margin-bottom: 16px;
}

.editable-table {
  width: 100%;
  border-collapse: collapse;
}

.editable-table th {
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
  font-size: 14px;
}

.editable-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #e0e0e0;
}

.editable-table input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.editable-table input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.delete-row-btn {
  background: #ff4444;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.delete-row-btn:hover {
  background: #cc0000;
}

/* Buttons */
.primary-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover {
  background: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.secondary-btn {
  background: #f0f0f0;
  color: #333;
  border: 1px solid #ccc;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn:hover {
  background: #e0e0e0;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
}
```

### 3. JavaScript Logic

**File: `chart-data-editor.js`**

```javascript
/**
 * Interactive Chart Data Editor
 * Allows users to edit chart data in real-time with database persistence
 */

class ChartDataEditor {
  constructor() {
    this.currentChartId = null;
    this.currentChartInstance = null;
    this.originalData = null;
    this.init();
  }

  init() {
    // Add edit buttons to all charts
    this.addEditButtonsToCharts();

    // Setup modal event listeners
    this.setupModalListeners();
  }

  /**
   * Add edit buttons to all chart containers
   */
  addEditButtonsToCharts() {
    const chartCanvases = document.querySelectorAll('canvas[data-chart]');

    chartCanvases.forEach(canvas => {
      const chartId = canvas.id;
      const container = canvas.parentElement;

      // Create edit button
      const editBtn = document.createElement('button');
      editBtn.className = 'chart-edit-btn';
      editBtn.setAttribute('data-chart-id', chartId);
      editBtn.innerHTML = '📊 Edit Data';
      editBtn.title = 'Edit chart data';

      // Add click handler
      editBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.openEditor(chartId);
      });

      // Add to container
      container.style.position = 'relative';
      container.appendChild(editBtn);
    });
  }

  /**
   * Open editor modal for a specific chart
   */
  openEditor(chartId) {
    this.currentChartId = chartId;

    // Get Chart.js instance
    const canvas = document.getElementById(chartId);
    this.currentChartInstance = Chart.getChart(canvas);

    if (!this.currentChartInstance) {
      alert('Chart not found!');
      return;
    }

    // Store original data for cancel
    this.originalData = JSON.parse(JSON.stringify(this.currentChartInstance.data));

    // Populate modal
    this.populateModal();

    // Show modal
    document.getElementById('chart-data-modal').style.display = 'flex';
  }

  /**
   * Populate modal with current chart data
   */
  populateModal() {
    const chart = this.currentChartInstance;
    const labels = chart.data.labels || [];
    const datasets = chart.data.datasets || [];

    // Set chart info
    document.getElementById('modal-chart-name').textContent =
      datasets[0]?.label || 'Chart';
    document.getElementById('modal-chart-type').textContent =
      this.getChartTypeName(chart.config.type);

    // Build table rows
    const tbody = document.getElementById('data-table-body');
    tbody.innerHTML = '';

    // For single dataset (most common)
    const values = datasets[0]?.data || [];

    labels.forEach((label, index) => {
      const value = values[index];
      const row = this.createTableRow(index, label, value);
      tbody.appendChild(row);
    });
  }

  /**
   * Create table row for data editing
   */
  createTableRow(index, label, value) {
    const row = document.createElement('tr');
    row.setAttribute('data-row-index', index);

    row.innerHTML = `
      <td>${index + 1}</td>
      <td><input type="text" class="label-input" value="${label}"></td>
      <td><input type="number" class="value-input" value="${value}" step="any"></td>
      <td><button class="delete-row-btn" data-row-index="${index}">🗑️</button></td>
    `;

    // Add delete handler
    row.querySelector('.delete-row-btn').addEventListener('click', (e) => {
      row.remove();
      this.renumberRows();
    });

    return row;
  }

  /**
   * Setup modal event listeners
   */
  setupModalListeners() {
    // Close button
    document.querySelector('.modal-close').addEventListener('click', () => {
      this.closeModal();
    });

    // Cancel button
    document.getElementById('cancel-btn').addEventListener('click', () => {
      this.closeModal();
    });

    // Add row button
    document.getElementById('add-row-btn').addEventListener('click', () => {
      this.addRow();
    });

    // Save & Update button
    document.getElementById('save-update-btn').addEventListener('click', () => {
      this.saveAndUpdate();
    });

    // Close on overlay click
    document.getElementById('chart-data-modal').addEventListener('click', (e) => {
      if (e.target.id === 'chart-data-modal') {
        this.closeModal();
      }
    });
  }

  /**
   * Add new empty row
   */
  addRow() {
    const tbody = document.getElementById('data-table-body');
    const currentRows = tbody.querySelectorAll('tr').length;
    const row = this.createTableRow(currentRows, '', 0);
    tbody.appendChild(row);
    this.renumberRows();
  }

  /**
   * Renumber table rows
   */
  renumberRows() {
    const rows = document.querySelectorAll('#data-table-body tr');
    rows.forEach((row, index) => {
      row.setAttribute('data-row-index', index);
      row.querySelector('td:first-child').textContent = index + 1;
      row.querySelector('.delete-row-btn').setAttribute('data-row-index', index);
    });
  }

  /**
   * Save changes and update chart
   */
  async saveAndUpdate() {
    // 1. Collect new data from table
    const newData = this.collectTableData();

    // 2. Update Chart.js instance
    this.updateChart(newData);

    // 3. Save to database
    const saved = await this.saveToDatabase(newData);

    if (saved) {
      // 4. Close modal
      this.closeModal();

      // 5. Show success message
      this.showSuccessMessage('Chart updated successfully!');
    } else {
      alert('Failed to save changes. Please try again.');
    }
  }

  /**
   * Collect data from table inputs
   */
  collectTableData() {
    const rows = document.querySelectorAll('#data-table-body tr');
    const labels = [];
    const values = [];

    rows.forEach(row => {
      const label = row.querySelector('.label-input').value;
      const value = parseFloat(row.querySelector('.value-input').value);

      labels.push(label);
      values.push(value);
    });

    return { labels, values };
  }

  /**
   * Update Chart.js instance with new data
   */
  updateChart(newData) {
    const chart = this.currentChartInstance;

    // Update labels
    chart.data.labels = newData.labels;

    // Update values (first dataset)
    if (chart.data.datasets && chart.data.datasets.length > 0) {
      chart.data.datasets[0].data = newData.values;
    }

    // Re-render chart
    chart.update();
  }

  /**
   * Save updated data to database
   */
  async saveToDatabase(newData) {
    try {
      const response = await fetch('/api/charts/update-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          chart_id: this.currentChartId,
          presentation_id: this.getPresentationId(),
          labels: newData.labels,
          values: newData.values,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const result = await response.json();
      return result.success;

    } catch (error) {
      console.error('Error saving to database:', error);
      return false;
    }
  }

  /**
   * Get presentation ID from URL
   */
  getPresentationId() {
    // Extract from URL: /p/presentation-id
    const match = window.location.pathname.match(/\/p\/([a-f0-9-]+)/);
    return match ? match[1] : null;
  }

  /**
   * Close modal
   */
  closeModal() {
    document.getElementById('chart-data-modal').style.display = 'none';
    this.currentChartId = null;
    this.currentChartInstance = null;
    this.originalData = null;
  }

  /**
   * Get human-readable chart type name
   */
  getChartTypeName(type) {
    const names = {
      'line': 'Line Chart',
      'bar': 'Bar Chart',
      'doughnut': 'Doughnut Chart',
      'pie': 'Pie Chart',
      'scatter': 'Scatter Plot',
      'bubble': 'Bubble Chart',
      'radar': 'Radar Chart',
      'polarArea': 'Polar Area Chart'
    };
    return names[type] || 'Chart';
  }

  /**
   * Show success message
   */
  showSuccessMessage(message) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'success-toast';
    toast.innerHTML = `✅ ${message}`;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #4CAF50;
      color: white;
      padding: 16px 24px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      z-index: 100000;
      font-size: 14px;
      font-weight: 500;
      animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.chartDataEditor = new ChartDataEditor();
});
```

---

## Backend Implementation

### API Endpoints

**File: `api/chart_data_routes.py`** (or equivalent in Layout Builder)

```python
from flask import Blueprint, request, jsonify
from datetime import datetime

chart_data_bp = Blueprint('chart_data', __name__)

@chart_data_bp.route('/api/charts/update-data', methods=['POST'])
def update_chart_data():
    """
    Update chart data and save to database.

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
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        chart_id = data['chart_id']
        presentation_id = data['presentation_id']
        labels = data['labels']
        values = data['values']

        # Validate data
        if len(labels) != len(values):
            return jsonify({
                'success': False,
                'error': 'Labels and values must have same length'
            }), 400

        # Save to database
        chart_data_record = {
            'chart_id': chart_id,
            'presentation_id': presentation_id,
            'labels': labels,
            'values': values,
            'updated_at': datetime.utcnow(),
            'updated_by': 'user_id_here'  # Get from session
        }

        # Update in database (example with SQLAlchemy)
        from models import ChartData, db

        # Find existing record or create new
        existing = ChartData.query.filter_by(
            chart_id=chart_id,
            presentation_id=presentation_id
        ).first()

        if existing:
            existing.labels = labels
            existing.values = values
            existing.updated_at = datetime.utcnow()
        else:
            new_record = ChartData(**chart_data_record)
            db.session.add(new_record)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chart data updated successfully',
            'chart_id': chart_id,
            'updated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        print(f"Error updating chart data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chart_data_bp.route('/api/charts/get-data/<presentation_id>', methods=['GET'])
def get_chart_data(presentation_id):
    """
    Get all chart data for a presentation.

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
        from models import ChartData

        charts = ChartData.query.filter_by(
            presentation_id=presentation_id
        ).all()

        chart_data_list = [
            {
                'chart_id': chart.chart_id,
                'labels': chart.labels,
                'values': chart.values,
                'updated_at': chart.updated_at.isoformat()
            }
            for chart in charts
        ]

        return jsonify({
            'success': True,
            'charts': chart_data_list
        }), 200

    except Exception as e:
        print(f"Error fetching chart data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## Database Schema

### New Table: `chart_data_edits`

```sql
CREATE TABLE chart_data_edits (
    id SERIAL PRIMARY KEY,
    chart_id VARCHAR(255) NOT NULL,
    presentation_id UUID NOT NULL,
    labels JSONB NOT NULL,  -- Array of X-axis labels
    values JSONB NOT NULL,  -- Array of Y-axis values
    chart_type VARCHAR(50),  -- 'line', 'bar', etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),  -- User ID who made the edit

    -- Indexes
    CONSTRAINT unique_chart_per_presentation
        UNIQUE (chart_id, presentation_id),

    -- Foreign key (if presentations table exists)
    FOREIGN KEY (presentation_id)
        REFERENCES presentations(id)
        ON DELETE CASCADE
);

-- Index for fast lookup
CREATE INDEX idx_chart_edits_presentation
    ON chart_data_edits(presentation_id);

CREATE INDEX idx_chart_edits_chart
    ON chart_data_edits(chart_id);
```

**SQLAlchemy Model**:

```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from extensions import db

class ChartData(db.Model):
    __tablename__ = 'chart_data_edits'

    id = Column(Integer, primary_key=True)
    chart_id = Column(String(255), nullable=False)
    presentation_id = Column(UUID(as_uuid=True), nullable=False)
    labels = Column(JSONB, nullable=False)
    values = Column(JSONB, nullable=False)
    chart_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255))

    __table_args__ = (
        db.UniqueConstraint('chart_id', 'presentation_id',
                           name='unique_chart_per_presentation'),
    )

    def to_dict(self):
        return {
            'chart_id': self.chart_id,
            'presentation_id': str(self.presentation_id),
            'labels': self.labels,
            'values': self.values,
            'chart_type': self.chart_type,
            'updated_at': self.updated_at.isoformat()
        }
```

---

## Load Saved Data on Presentation Load

**Modify presentation loader to inject saved data**:

```javascript
// In presentation-viewer.html or reveal-config.js

async function loadPresentationWithChartData(presentationId) {
  try {
    // 1. Load saved chart data from API
    const response = await fetch(`/api/charts/get-data/${presentationId}`);
    const result = await response.json();

    if (result.success && result.charts.length > 0) {
      // 2. Wait for Reveal.js to be ready
      Reveal.on('ready', () => {
        // 3. Update each chart with saved data
        result.charts.forEach(chartData => {
          updateChartWithSavedData(chartData);
        });
      });
    }
  } catch (error) {
    console.error('Error loading saved chart data:', error);
  }
}

function updateChartWithSavedData(chartData) {
  const canvas = document.getElementById(chartData.chart_id);
  if (!canvas) return;

  const chart = Chart.getChart(canvas);
  if (!chart) return;

  // Update chart data
  chart.data.labels = chartData.labels;
  if (chart.data.datasets && chart.data.datasets.length > 0) {
    chart.data.datasets[0].data = chartData.values;
  }

  // Re-render
  chart.update();
}

// Call on page load
const presentationId = getPresentationIdFromURL();
loadPresentationWithChartData(presentationId);
```

---

## Summary

### Files to Create/Modify

**Layout Builder (Frontend)**:
1. `presentation-viewer.html` - Add modal HTML
2. `chart-editor.css` - Add modal and button styles
3. `chart-data-editor.js` - Add JavaScript logic
4. `reveal-config.js` - Add data loading on presentation load

**Backend (API)**:
1. `api/chart_data_routes.py` - Create API endpoints
2. `models/chart_data.py` - Create database model
3. Database migration to create `chart_data_edits` table

### Implementation Timeline

**Phase 1 - Frontend UI (2-3 days)**:
- Add edit buttons to charts
- Create modal popup
- Implement table editing

**Phase 2 - Chart Update Logic (1-2 days)**:
- Connect to Chart.js instances
- Update charts in real-time
- Handle add/delete rows

**Phase 3 - Backend API (2-3 days)**:
- Create API endpoints
- Database schema
- Save/load functionality

**Phase 4 - Integration & Testing (2-3 days)**:
- Load saved data on presentation load
- End-to-end testing
- Error handling

**Total: 1-2 weeks**

---

## Next Steps

1. ✅ Review this specification
2. ⏸️ Create proof-of-concept demo
3. ⏸️ Layout Builder team implements frontend
4. ⏸️ Backend team implements API
5. ⏸️ Database migration
6. ⏸️ Integration testing
7. ⏸️ Production deployment

---

**Status**: 📋 Specification complete - Ready for implementation
